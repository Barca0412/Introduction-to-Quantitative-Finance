"""Main paper fetching script for the daily radar pipeline."""

import asyncio
import logging
import os
import time
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Set, Tuple

import arxiv

from .affiliations import enrich_affiliations
from .compute_stats import compute_and_save_stats
from .config import ARXIV_CATEGORIES, FETCH_BACKOFF_SECONDS, FETCH_DAYS, MAX_RESULTS_PER_CATEGORY
from .generate_charts import generate_all_charts, generate_combined_chart
from .llm_processor import process_papers_batch
from .storage import load_papers, merge_papers, save_papers
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
) -> Tuple[List[Dict[str, Any]], Optional[str]]:
    """Fetch every paper of one arXiv category submitted on the target dates.

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
                query=f"cat:{category} AND submittedDate:[{start_date} TO {end_date}]",
                max_results=max_results,
                sort_by=arxiv.SortCriterion.SubmittedDate,
                sort_order=arxiv.SortOrder.Descending,
            )
            for result in client.results(search):
                paper = build_paper_record(result)
                if paper["published_date"] in target_date_set:
                    papers.append(paper)
            logger.info("Fetched %s papers from %s", len(papers), category)
            return papers, None
        except Exception as exc:  # arxiv.HTTPError (429 etc.), empty pages, network errors
            error = f"{type(exc).__name__}: {exc}"
            if len(papers) > len(best):
                best = papers
    logger.error("Giving up on %s after %s attempts: %s", category, len(backoff) + 1, error)
    return best, error


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
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """Fetch recent papers from all monitored categories within arXiv's rate limit.

    Returns (papers, report) where report has one row per category.
    """
    target_dates = get_target_dates(days)
    logger.info("Fetching papers for target dates: %s", ", ".join(target_dates))
    logger.info("Fetching papers from %s categories...", len(categories))

    loop = asyncio.get_running_loop()
    # One shared client serializes requests and enforces arXiv's 3-second
    # minimum delay. Parallel clients can otherwise produce intermittent 429s.
    client = client or arxiv.Client(page_size=100, delay_seconds=3.0, num_retries=3)
    all_papers: List[Dict[str, Any]] = []
    report: List[Dict[str, Any]] = []
    for category in categories:
        papers, error = await loop.run_in_executor(
            None,
            lambda c=category: fetch_category_papers(c, target_dates, MAX_RESULTS_PER_CATEGORY, client, backoff, sleep),
        )
        all_papers.extend(papers)
        report.append({"category": category, "papers": len(papers), "error": error})

    logger.info("Total raw papers fetched: %s", len(all_papers))
    failed = [r["category"] for r in report if r["error"]]
    if failed:
        logger.warning("Categories with fetch errors: %s", ", ".join(failed))
    return all_papers, report


def needs_enrichment(fetched: List[Dict[str, Any]], existing: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Drop papers already stored with an LLM summary, so the LLM only sees new ones.

    Papers stored without a summary (LLM failure or rule-based fallback) are kept,
    so they get another chance on the next run.
    """
    enriched: Set[str] = {
        normalize_arxiv_id(str(p.get("id", "")))
        for p in existing.get("papers", [])
        if str(p.get("summary_zh", "")).strip()
    }
    return [p for p in fetched if normalize_arxiv_id(str(p.get("id", ""))) not in enriched]


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
    new_batch = needs_enrichment(deduped_batch, existing)
    logger.info(
        "%s fetched papers are already stored with a summary; %s are new or need another try",
        len(deduped_batch) - len(new_batch),
        len(new_batch),
    )

    if new_batch:
        logger.info("\n[Step 2] Processing %s papers with LLM...", len(new_batch))
        processed_papers = await process_papers_batch(new_batch)

        logger.info("\n[Step 3] Normalizing affiliations...")
        enriched_papers = await enrich_affiliations(processed_papers)
    else:
        logger.info("\n[Step 2-3] Nothing new to enrich")
        enriched_papers = []

    logger.info("\n[Step 4] Merging with existing data...")
    merged = merge_papers(existing, enriched_papers)
    logger.info("Total papers after merge: %s", merged["total_count"])

    logger.info("\n[Step 5] Saving papers data...")
    save_papers(merged)
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
