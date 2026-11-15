"""Data persistence helpers for papers and statistics."""

import json
import re
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from .affiliations import normalize_affiliation_fields
from .config import ENRICH_CHECKPOINT_FILE, PAPERS_FILE, STATS_FILE
from .focus import build_focus_metadata
from .utils import (
    build_arxiv_abs_link,
    build_arxiv_pdf_link,
    merge_unique_strings,
    normalize_arxiv_id,
    normalize_author_entries,
    parse_arxiv_date,
    to_https,
)


def load_papers() -> Dict[str, Any]:
    """Load papers from disk."""
    if not PAPERS_FILE.exists():
        return {"last_updated": None, "total_count": 0, "papers": []}

    with open(PAPERS_FILE, "r", encoding="utf-8") as file_handle:
        return json.load(file_handle)


def save_papers(data: Dict[str, Any]) -> None:
    """Normalize, enrich, and persist papers data atomically."""
    payload = prepare_papers_payload(data.get("papers", []))
    write_atomically(PAPERS_FILE, payload)


def load_stats() -> Optional[Dict[str, Any]]:
    """Load statistics from disk."""
    if not STATS_FILE.exists():
        return None

    with open(STATS_FILE, "r", encoding="utf-8") as file_handle:
        return json.load(file_handle)


def save_stats(data: Dict[str, Any]) -> None:
    """Persist statistics data atomically."""
    data["last_updated"] = datetime.utcnow().isoformat()
    write_atomically(STATS_FILE, data)


def normalize_paper(paper: Dict[str, Any]) -> Dict[str, Any]:
    """Normalize a paper record into the canonical schema."""
    paper_id = normalize_arxiv_id(str(paper.get("id", "")))
    published_date = str(paper.get("published_date", "")).strip()
    if "T" in published_date or " " in published_date:
        published_date = parse_arxiv_date(published_date)

    if paper.get("institutions"):
        # S6 (institutions.py) already gives clean names; the old splitter would cut
        # names with commas ("Agency for Science, Technology and Research").
        names = list(dict.fromkeys(i.get("name", "") for i in paper["institutions"] if i.get("name")))
        normalized_affiliation = {"affiliation": "; ".join(names), "affiliations": names}
    else:
        normalized_affiliation = normalize_affiliation_fields(
            paper.get("affiliation", ""),
            paper.get("affiliations", []),
        )

    normalized = {
        "id": paper_id,
        "title": str(paper.get("title", "")).strip(),
        "abstract": str(paper.get("abstract", "")).replace("\n", " ").strip(),
        "authors": normalize_author_entries(paper.get("authors", [])),
        "categories": merge_unique_strings(paper.get("categories", [])),
        "published_date": published_date,
        "pdf_link": build_arxiv_pdf_link(paper_id) or to_https(str(paper.get("pdf_link", "")).strip()),
        "abs_link": build_arxiv_abs_link(paper_id) or to_https(str(paper.get("abs_link", "")).strip()),
        "tags": merge_unique_strings(paper.get("tags", [])),
        "keywords": merge_unique_strings(paper.get("keywords", [])),
        "summary_zh": str(paper.get("summary_zh", "")).strip(),
        "affiliation": normalized_affiliation["affiliation"],
        "affiliations": normalized_affiliation["affiliations"],
    }
    normalized.update(_v2_fields(paper))

    normalized["focus"] = build_focus_metadata(normalized)
    return normalized


# arXiv metadata kept since 2026-11-15, plus the S3 v2 enrichment (enrich.py). Old
# records have none of these; they read as "not enriched with v2 yet".
ARXIV_EXTRA_FIELDS = ("primary_category", "comment", "journal_ref", "doi", "source")
# S6 institutions (institutions.py).
INSTITUTION_FIELDS = (
    "institutions", "author_affiliations", "affiliation_source", "affiliation_checked_at", "affiliation_raw",
    "author_ids",
)
V2_FIELDS = (
    "relevance", "relevance_reason_zh", "paper_type", "task_types", "finance_domains",
    "methods", "keywords_raw", "data_market", "reproducibility", "tldr_zh", "points_zh",
    "venue_mention", "withdrawn", "schema_version", "stage_versions", "attempts",
    "last_error", "enrich_warnings", "quality_flags", "keywords_norm",
    "venue", "team_background", "discipline", "discipline_basis", "venue_list",
)


def _v2_fields(paper: Dict[str, Any]) -> Dict[str, Any]:
    out: Dict[str, Any] = {key: str(paper.get(key) or "").strip() for key in ARXIV_EXTRA_FIELDS}
    for key in V2_FIELDS + INSTITUTION_FIELDS:
        if paper.get(key) is not None:
            out[key] = paper[key]
    return out


def _enrich_version(paper: Dict[str, Any]) -> tuple:
    """Comparable form of stage_versions.enrich: "s3-v2.10" > "s3-v2.9" > none."""
    version = str((paper.get("stage_versions") or {}).get("enrich") or "")
    return tuple(int(part) for part in re.findall(r"\d+", version))


def merge_duplicate_paper(existing: Dict[str, Any], incoming: Dict[str, Any]) -> Dict[str, Any]:
    """Merge two records of the same paper, preferring richer fields."""
    merged = normalize_paper(existing)
    candidate = normalize_paper(incoming)
    # The incoming record was enriched by the LLM and the stored one never was: its
    # tags/keywords came from the keyword rules, so replace them instead of merging.
    llm_upgrade = bool(candidate["summary_zh"]) and not merged["summary_zh"]
    # A newer enrichment version replaces the whole S3 output (tags, keywords, summary,
    # classification), never merged with the older one.
    v2_upgrade = _enrich_version(candidate) > _enrich_version(merged)

    merged["title"] = candidate["title"] or merged["title"]
    merged["abstract"] = candidate["abstract"] or merged["abstract"]
    merged["summary_zh"] = candidate["summary_zh"] or merged["summary_zh"]
    merged["affiliation"] = candidate["affiliation"] or merged["affiliation"]
    merged["affiliations"] = merge_unique_strings(
        merged.get("affiliations", []),
        candidate.get("affiliations", []),
    )
    merged["affiliation"] = "; ".join(merged["affiliations"]) or merged["affiliation"]
    merged["published_date"] = candidate["published_date"] or merged["published_date"]
    merged["pdf_link"] = candidate["pdf_link"] or merged["pdf_link"]
    merged["abs_link"] = candidate["abs_link"] or merged["abs_link"]
    merged["categories"] = merge_unique_strings(merged["categories"], candidate["categories"])
    for key in ARXIV_EXTRA_FIELDS:
        merged[key] = candidate[key] or merged[key]
    if str(candidate.get("affiliation_checked_at") or "") > str(merged.get("affiliation_checked_at") or ""):
        for key in INSTITUTION_FIELDS:
            merged[key] = candidate.get(key)
        merged["affiliations"] = candidate["affiliations"]
        merged["affiliation"] = candidate["affiliation"]
    if v2_upgrade:
        for key in V2_FIELDS:
            merged.pop(key, None)
            if key in candidate:
                merged[key] = candidate[key]
        merged["summary_zh"] = candidate["summary_zh"]
    elif "attempts" in candidate and _enrich_version(candidate) == _enrich_version(merged):
        # Same version: keep the failure count and error of the newer attempt.
        for key in ("attempts", "last_error"):
            merged[key] = candidate.get(key, merged.get(key))
    if llm_upgrade or v2_upgrade:
        merged["tags"] = candidate["tags"]
        merged["keywords"] = candidate["keywords"]
    else:
        merged["tags"] = merge_unique_strings(merged["tags"], candidate["tags"])
        merged["keywords"] = merge_unique_strings(merged["keywords"], candidate["keywords"])

    merged["authors"] = (
        candidate["authors"]
        if len(candidate["authors"]) > len(merged["authors"])
        else merged["authors"]
    )

    merged["focus"] = build_focus_metadata(merged)
    return merged


def prepare_papers_payload(papers: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Prepare normalized, deduplicated papers payload for persistence."""
    deduped: Dict[str, Dict[str, Any]] = {}

    for paper in papers:
        normalized = normalize_paper(paper)
        paper_id = normalized.get("id")
        if not paper_id:
            continue

        if paper_id in deduped:
            deduped[paper_id] = merge_duplicate_paper(deduped[paper_id], normalized)
        else:
            deduped[paper_id] = normalized

    merged = list(deduped.values())
    merged.sort(
        key=lambda paper: (
            paper.get("published_date", ""),
            paper.get("focus", {}).get("score", 0),
            paper.get("id", ""),
        ),
        reverse=True,
    )

    return {
        "last_updated": datetime.utcnow().isoformat(),
        "total_count": len(merged),
        "papers": merged,
    }


def merge_papers(existing: Dict[str, Any], new_papers: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Merge existing and new papers, deduplicating by normalized arXiv ID."""
    return prepare_papers_payload(existing.get("papers", []) + new_papers)


def write_atomically(filepath: Path, data: Any) -> None:
    """Write JSON data atomically using a temp file + rename."""
    filepath.parent.mkdir(parents=True, exist_ok=True)

    with tempfile.NamedTemporaryFile(
        mode="w",
        encoding="utf-8",
        dir=filepath.parent,
        delete=False,
        suffix=".tmp",
    ) as tmp_file:
        # Compact JSON: indent=2 roughly doubled the file size.
        json.dump(data, tmp_file, ensure_ascii=False, separators=(",", ":"))
        tmp_path = Path(tmp_file.name)

    tmp_path.replace(filepath)


def refresh_rule_tags(papers: List[Dict[str, Any]], tagger) -> int:
    """Re-run the keyword rules on papers the LLM never enriched (no summary_zh).

    Their tags came from the rules alone, so a rule fix should reach them too.
    Returns how many papers changed.
    """
    changed = 0
    for paper in papers:
        if str(paper.get("summary_zh", "")).strip():
            continue
        tags = tagger(paper)
        if tags != paper.get("tags", []):
            paper["tags"] = tags
            paper["focus"] = build_focus_metadata(paper)
            changed += 1
    return changed


def append_checkpoint(papers: List[Dict[str, Any]]) -> None:
    """Append freshly enriched papers to the checkpoint file (fast: no full rewrite)."""
    ENRICH_CHECKPOINT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(ENRICH_CHECKPOINT_FILE, "a", encoding="utf-8") as fh:
        for paper in papers:
            fh.write(json.dumps(paper, ensure_ascii=False) + "\n")
        fh.flush()


def read_checkpoint() -> List[Dict[str, Any]]:
    """Papers left by an interrupted run; a torn last line (crash mid-write) is skipped."""
    if not ENRICH_CHECKPOINT_FILE.exists():
        return []
    papers = []
    with open(ENRICH_CHECKPOINT_FILE, encoding="utf-8") as fh:
        for line in fh:
            try:
                papers.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return papers


def clear_checkpoint() -> None:
    ENRICH_CHECKPOINT_FILE.unlink(missing_ok=True)
