"""Main paper fetching script for the daily radar pipeline."""

import asyncio
import logging
import os
import time
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple

import arxiv

from .institutions import enrich_institutions
from .keywords import normalize_all
from .venues import classify_all
from .compute_stats import compute_and_save_stats
from .config import (
    ARXIV_CATEGORIES,
    FETCH_BACKOFF_SECONDS,
    FETCH_DAYS,
    FINANCE_FILTERED_CATEGORIES,
    FINANCE_QUERY,
    FINANCE_TERM_PATTERN,
    LLM_API_KEY,
    MAX_RESULTS_PER_CATEGORY,
)
from .generate_charts import generate_all_charts, generate_combined_chart
from .enrich import ENRICH_VERSION, needs_enrich
from .llm_processor import LLMBudgetExhausted, fallback_tags_for_paper, process_papers_batch
from .storage import (
    append_checkpoint,
    clear_checkpoint,
    load_papers,
    merge_papers,
    read_checkpoint,
    refresh_rule_tags,
    save_papers,
)
from .utils import build_paper_record, get_target_dates, normalize_arxiv_id


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def fetch_category_papers(
    category: str,
    target_dates: List[str],
    max_results: int = MAX_RESULTS_PER_CATEGORY,
    client: Optional[arxiv.Client] = None,
    backoff: Tuple[float, ...] = FETCH_BACKOFF_SECONDS,
    sleep: Callable[[float], None] = time.sleep,
    query_filter: str = "",
    keep: Optional[Callable[[Dict[str, Any]], bool]] = None,
) -> Tuple[List[Dict[str, Any]], Optional[str]]:
    """Fetch every paper of one arXiv category submitted on the target dates.

    ``query_filter`` narrows the arXiv query (ANDed with the category), and ``keep``
    drops papers locally afterwards; both are used for the finance-only categories.

    Pages through the whole date window (up to ``max_results``). arXiv answers
    bursts with HTTP 429, and the arxiv client's own retries (3 s apart) are often
    not enough, so the whole category is retried after each delay in ``backoff``.

    Returns (papers, error). ``error`` is None on success; otherwise it describes the
    last failure and ``papers`` holds whatever the best attempt managed to read.
    """
    client = client or arxiv.Client()
    target_date_set = set(target_dates)
    start_date = min(target_date_set).replace("-", "") + "0000"
    end_date = max(target_date_set).replace("-", "") + "2359"

    best: List[Dict[str, Any]] = []
    error: Optional[str] = None
    for attempt in range(len(backoff) + 1):
        if attempt:
            logger.warning("Retrying %s in %.0f s (attempt %s/%s): %s", category, backoff[attempt - 1], attempt + 1, len(backoff) + 1, error)
            sleep(backoff[attempt - 1])
        papers: List[Dict[str, Any]] = []
        try:
            search = arxiv.Search(
                query=f"cat:{category}{f' AND ({query_filter})' if query_filter else ''} AND submittedDate:[{start_date} TO {end_date}]",
                max_results=max_results,
                sort_by=arxiv.SortCriterion.SubmittedDate,
                sort_order=arxiv.SortOrder.Descending,
            )
            for result in client.results(search):
                paper = build_paper_record(result)
                if paper["published_date"] in target_date_set and (keep is None or keep(paper)):
                    papers.append(paper)
            logger.info("Fetched %s papers from %s", len(papers), category)
            return papers, None
        except Exception as exc:  # arxiv.HTTPError (429 etc.), empty pages, network errors
            error = f"{type(exc).__name__}: {exc}"
            if len(papers) > len(best):
                best = papers
    logger.error("Giving up on %s after %s attempts: %s", category, len(backoff) + 1, error)
    return best, error


def looks_financial(paper: Dict[str, Any]) -> bool:
    """Whole-word finance terms in title or abstract (see FINANCE_TERM_PATTERN)."""
    return bool(FINANCE_TERM_PATTERN.search(f"{paper.get('title', '')} {paper.get('abstract', '')}"))


def report_enrichment(papers: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Job-summary table for the S3 run: done/failed, relevance mix, warnings, flags."""
    from collections import Counter

    done = [p for p in papers if (p.get("stage_versions") or {}).get("enrich") == ENRICH_VERSION]
    failed = [p for p in papers if p not in done]
    relevance = Counter(p.get("relevance") for p in done)
    flags = Counter(flag for p in done for flag in p.get("quality_flags", []))
    warned = sum(1 for p in done if p.get("enrich_warnings"))
    tldr = [len(p.get("tldr_zh", "")) for p in done]
    summary = {
        "processed": len(papers), "succeeded": len(done), "failed": len(failed),
        "relevance": {str(k): relevance.get(k, 0) for k in (3, 2, 1, 0)},
        "with_warnings": warned, "flags": dict(flags),
        "tldr_avg_chars": round(sum(tldr) / len(tldr)) if tldr else 0,
    }
    lines = [
        f"### LLM enrichment ({ENRICH_VERSION})", "",
        f"- processed {summary['processed']}, succeeded {summary['succeeded']}, failed {summary['failed']}",
        "- relevance 3/2/1/0: " + " / ".join(str(summary["relevance"][k]) for k in ("3", "2", "1", "0")),
        f"- answers with soft fixes: {warned}; average TL;DR length: {summary['tldr_avg_chars']} chars",
        "- suspicious (S4): " + (", ".join(f"{k} {v}" for k, v in flags.most_common()) or "none"),
    ]
    if failed:
        lines.append("- failed ids: " + ", ".join(str(p.get("id")) for p in failed[:20]))
        print(f"::warning title=LLM enrichment::{len(failed)} of {len(papers)} papers failed; they are retried on the next run", flush=True)
    logger.info("Enrichment: %s", summary)
    path = os.getenv("GITHUB_STEP_SUMMARY")
    if path:
        with open(path, "a", encoding="utf-8") as fh:
            fh.write("\n".join(lines) + "\n\n")
    return summary


def report_keywords(report: Dict[str, Any]) -> None:
    """Coverage and the most frequent new terms, for the weekly vocabulary review."""
    if not report.get("keywords"):
        return
    lines = [
        "### Keywords", "",
        f"- {report['matched']} of {report['keywords']} keywords matched a standard keyword ({report['coverage']:.0%})",
        "- most frequent new terms (candidates for vocab/keywords.yaml): "
        + ", ".join(f"{term} ({n})" for term, n in report["top_new_terms"][:20]),
        "",
    ]
    path = os.getenv("GITHUB_STEP_SUMMARY")
    if path:
        with open(path, "a", encoding="utf-8") as fh:
            fh.write("\n".join(lines) + "\n")


def report_venues(report: Dict[str, Any]) -> None:
    if not report.get("papers"):
        return
    lines = [
        "### Venue and discipline", "",
        f"- {report['with_venue']} of {report['papers']} enriched papers name a venue",
        "- discipline: " + ", ".join(f"{k} {v}" for k, v in sorted(report["discipline"].items())),
        "- based on: " + ", ".join(f"{k} {v}" for k, v in sorted(report["basis"].items())),
    ]
    if report["unknown_venues"]:
        lines.append("- venues not in vocab/venues.yaml yet: " + "; ".join(f"{n} ({c})" for n, c in report["unknown_venues"][:10]))
    path = os.getenv("GITHUB_STEP_SUMMARY")
    if path:
        with open(path, "a", encoding="utf-8") as fh:
            fh.write("\n".join(lines) + "\n\n")


def report_institutions(counts: Dict[str, int]) -> None:
    looked = counts.get("looked_up", 0)
    if not looked:
        return
    line = (f"### Authors and institutions\n\n- looked up {looked} relevant papers; "
            f"{counts['with_institution']} with an institution, {counts['all_authors']} with every author covered, "
            f"{counts['html_used']} needed the arXiv page\n\n")
    path = os.getenv("GITHUB_STEP_SUMMARY")
    if path:
        with open(path, "a", encoding="utf-8") as fh:
            fh.write(line)


def report_fetch(report: List[Dict[str, Any]]) -> None:
    """Make fetch problems visible: GitHub warning annotations + a job-summary table."""
    lines = ["### arXiv fetch", "", "| Category | Papers | Status |", "| --- | ---: | --- |"]
    for row in report:
        status = "ok" if not row["error"] else ("partial: " if row["papers"] else "failed: ") + row["error"]
        lines.append(f"| {row['category']} | {row['papers']} | {status.replace('|', '/')} |")
        if row["error"]:
            # Shows up as a yellow warning on the workflow run page.
            print(f"::warning title=arXiv fetch {row['category']}::{status}", flush=True)
    summary = os.getenv("GITHUB_STEP_SUMMARY")
    if summary:
        with open(summary, "a", encoding="utf-8") as fh:
            fh.write("\n".join(lines) + "\n\n")


async def fetch_all_categories(
    categories: List[str],
    days: int = FETCH_DAYS,
    client: Optional[arxiv.Client] = None,
    backoff: Tuple[float, ...] = FETCH_BACKOFF_SECONDS,
    sleep: Callable[[float], None] = time.sleep,
    filtered_categories: Optional[List[str]] = None,
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """Fetch recent papers from all monitored categories within arXiv's rate limit.

    ``categories`` are fetched whole; ``filtered_categories`` (default: cs.LG and
    stat.ML) only through the finance-term query plus the local whole-word check.
    Papers listed in several categories come back more than once; the caller dedups.

    Returns (papers, report) where report has one row per fetched source.
    """
    if filtered_categories is None:
        filtered_categories = FINANCE_FILTERED_CATEGORIES
    sources = [(c, c, "", None) for c in categories]
    sources += [(f"{c} (finance terms)", c, FINANCE_QUERY, looks_financial) for c in filtered_categories if c not in categories]
    target_dates = get_target_dates(days)
    logger.info("Fetching papers for target dates: %s", ", ".join(target_dates))
    logger.info("Fetching papers from %s sources...", len(sources))

    loop = asyncio.get_running_loop()
    # One shared client serializes requests and enforces arXiv's 3-second
    # minimum delay. Parallel clients can otherwise produce intermittent 429s.
    client = client or arxiv.Client(page_size=100, delay_seconds=3.0, num_retries=3)
    all_papers: List[Dict[str, Any]] = []
    report: List[Dict[str, Any]] = []
    for label, category, query_filter, keep in sources:
        papers, error = await loop.run_in_executor(
            None,
            lambda c=category, q=query_filter, k=keep: fetch_category_papers(
                c, target_dates, MAX_RESULTS_PER_CATEGORY, client, backoff, sleep, q, k
            ),
        )
        all_papers.extend(papers)
        report.append({"category": label, "papers": len(papers), "error": error})

    logger.info("Total raw papers fetched: %s", len(all_papers))
    failed = [r["category"] for r in report if r["error"]]
    if failed:
        logger.warning("Categories with fetch errors: %s", ", ".join(failed))
    return all_papers, report


def needs_enrichment(fetched: List[Dict[str, Any]], existing: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Papers the LLM should (re)process: new ones, and stored ones without a
    current-version enrichment that have not failed too often (enrich.needs_enrich).

    Each returned paper starts from its stored record (old enrichment, failure count),
    with the freshly fetched arXiv metadata on top, so a failed attempt keeps both.
    """
    stored = {normalize_arxiv_id(str(p.get("id", ""))): p for p in existing.get("papers", [])}
    todo: List[Dict[str, Any]] = []
    for paper in fetched:
        old = stored.get(normalize_arxiv_id(str(paper.get("id", ""))))
        if old is None:
            todo.append(paper)
        elif needs_enrich(old):
            fresh = {key: value for key, value in paper.items() if value not in ("", [], None)}
            todo.append({**old, **fresh})
    return todo


async def run_pipeline() -> Optional[Dict[str, Any]]:
    """Run the daily fetch -> enrich -> persist -> stats pipeline."""
    logger.info("=" * 60)
    logger.info("Starting LLM-Finance-Radar paper fetch pipeline")
    logger.info("=" * 60)

    logger.info("\n[Step 1] Fetching papers from arXiv...")
    fetched_papers, fetch_report = await fetch_all_categories(ARXIV_CATEGORIES)
    report_fetch(fetch_report)
    if not fetched_papers:
        raise RuntimeError(
            "No papers matched the arXiv date window. Refusing to publish stale Radar data."
        )

    deduped_batch = merge_papers({"papers": []}, fetched_papers)["papers"]
    if len(deduped_batch) != len(fetched_papers):
        logger.info(
            "Deduplicated %s overlapping category hits before LLM processing",
            len(fetched_papers) - len(deduped_batch),
        )

    existing = load_papers()
    recovered = read_checkpoint()
    if recovered:
        # An earlier run was interrupted after enriching these: keep its work.
        existing = merge_papers(existing, recovered)
        logger.info("Recovered %s enriched papers from the checkpoint of an interrupted run", len(recovered))
    new_batch = needs_enrichment(deduped_batch, existing)
    logger.info(
        "%s fetched papers are already stored with a summary; %s are new or need another try",
        len(deduped_batch) - len(new_batch),
        len(new_batch),
    )

    if new_batch:
        logger.info("\n[Step 2] Processing %s papers with LLM...", len(new_batch))
        written = 0

        async def checkpoint(done: List[Dict[str, Any]]) -> None:
            # Append only what is new since the last checkpoint: milliseconds, whereas
            # rewriting the 30k-paper history takes ~10 s. Merged back on the next run.
            nonlocal written
            append_checkpoint(done[written:])
            written = len(done)
            logger.info("Checkpoint: %s of %s papers enriched and kept", written, len(new_batch))

        try:
            processed_papers = await process_papers_batch(new_batch, checkpoint=checkpoint)
        except LLMBudgetExhausted as exc:
            save_papers(merge_papers(existing, exc.papers))
            clear_checkpoint()
            if LLM_API_KEY:
                report_enrichment(exc.papers)
            untouched = len(new_batch) - len(exc.papers)
            message = (
                f"LLM API refused requests ({exc}). Saved {len(exc.papers)} finished papers; "
                f"{untouched} were not attempted and keep no failure count. "
                "Top up / fix the key, then run again (locally: RESUME=1)."
            )
            print(f"::error title=LLM stopped::{message}", flush=True)
            summary_path = os.getenv("GITHUB_STEP_SUMMARY")
            if summary_path:
                with open(summary_path, "a", encoding="utf-8") as fh:
                    fh.write(f"**Stopped early:** {message}\n\n")
            raise SystemExit(message) from exc

        if LLM_API_KEY:
            report_enrichment(processed_papers)

        enriched_papers = processed_papers
    else:
        logger.info("\n[Step 2-3] Nothing new to enrich")
        enriched_papers = []

    logger.info("\n[Step 4] Merging with existing data...")
    merged = merge_papers(existing, enriched_papers)
    logger.info("Total papers after merge: %s", merged["total_count"])
    # Papers never seen by the LLM carry rule-based tags; keep them in step with the rules.
    retagged = refresh_rule_tags(merged["papers"], fallback_tags_for_paper)
    logger.info("Re-applied keyword-rule tags to %s papers without an LLM summary", retagged)

    # S5: map the LLM's keywords to the standard vocabulary (vocab/keywords.yaml).
    keyword_report = normalize_all(merged["papers"])
    logger.info("Keywords: %s of %s matched a standard keyword (%.0f%%)", keyword_report["matched"],
                keyword_report["keywords"], 100 * keyword_report["coverage"])
    report_keywords(keyword_report)

    # S6: institutions for relevant papers (new ones, and young ones OpenAlex had not
    # covered yet). OpenAlex + arXiv HTML, no LLM. Replaces the old LLM affiliation clean-up.
    logger.info("\n[Step 4b] Authors and institutions...")
    institution_counts = await enrich_institutions(merged["papers"])
    report_institutions(institution_counts)

    # Venue and discipline (4.3.6): needs the institutions above for the team guess.
    venue_report = classify_all(merged["papers"])
    report_venues(venue_report)

    logger.info("\n[Step 5] Saving papers data...")
    save_papers(merged)
    clear_checkpoint()
    logger.info("Papers saved successfully")

    logger.info("\n[Step 6] Computing statistics...")
    stats = compute_and_save_stats(merged["papers"])
    logger.info("Statistics saved. Tracked dates: %s", len(stats["tag_stats"]["_all"]["daily"]))

    logger.info("\n[Step 7] Generating charts...")
    generate_all_charts(stats)
    generate_combined_chart(stats)
    # Site data (docs/public/arxiv-data) is built later by build_site_data.py,
    # after embeddings exist; the full history is never copied to the site.
    logger.info("Charts refreshed")

    logger.info("\n" + "=" * 60)
    logger.info("Pipeline completed successfully")
    logger.info("=" * 60)

    return {
        "new_papers": len(new_batch),
        "total_papers": merged["total_count"],
        "fetch_report": fetch_report,
    }


if __name__ == "__main__":
    asyncio.run(run_pipeline())
