"""Data persistence helpers for papers and statistics."""

import json
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from .affiliations import normalize_affiliation_fields
from .config import PAPERS_FILE, STATS_FILE
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

    normalized["focus"] = build_focus_metadata(normalized)
    return normalized


def merge_duplicate_paper(existing: Dict[str, Any], incoming: Dict[str, Any]) -> Dict[str, Any]:
    """Merge two records of the same paper, preferring richer fields."""
    merged = normalize_paper(existing)
    candidate = normalize_paper(incoming)

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
        json.dump(data, tmp_file, ensure_ascii=False, indent=2)
        tmp_path = Path(tmp_file.name)

    tmp_path.replace(filepath)
