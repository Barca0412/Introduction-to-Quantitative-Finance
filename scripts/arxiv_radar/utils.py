"""Utility helpers for the paper ingestion and site pipeline."""

import asyncio
import functools
import re
from datetime import datetime, timedelta
from typing import Any, Dict, List, Tuple

from dateutil import parser as date_parser


def get_date_range(days: int = 2) -> Tuple[str, str]:
    """Return the UTC date range that covers the last ``days`` full dates."""
    today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    start_date = (today - timedelta(days=days)).isoformat() + "Z"
    end_date = today.isoformat() + "Z"
    return start_date, end_date


def get_target_dates(days: int = 2) -> List[str]:
    """Return a UTC date window ending today in ascending order.

    The workflow runs after arXiv's daily release window. Excluding the
    current UTC date meant the newest API results were routinely discarded;
    a wider inclusive window also covers weekends and announcement delays.
    """
    if days < 1:
        raise ValueError("days must be at least 1")

    today = datetime.utcnow().date()
    return [
        (today - timedelta(days=offset)).isoformat()
        for offset in range(days - 1, -1, -1)
    ]


def parse_arxiv_date(date_string: str) -> str:
    """Parse an arXiv date string and return ``YYYY-MM-DD`` or an empty string."""
    if not date_string:
        return ""

    try:
        dt = date_parser.parse(date_string)
        return dt.strftime("%Y-%m-%d")
    except Exception:
        return ""


def normalize_arxiv_id(arxiv_id: str) -> str:
    """Normalize arXiv IDs by stripping URLs, suffixes, and version markers."""
    if not arxiv_id:
        return ""

    candidate = arxiv_id.strip().rstrip("/")
    if candidate.startswith("http"):
        candidate = candidate.split("/")[-1]

    if candidate.endswith(".pdf"):
        candidate = candidate[:-4]

    return re.sub(r"v\d+$", "", candidate)


def to_https(url: str) -> str:
    """Upgrade known HTTP URLs to HTTPS."""
    if not url:
        return ""
    return url.replace("http://", "https://", 1)


def build_arxiv_abs_link(arxiv_id: str) -> str:
    """Build a stable arXiv abstract link from a normalized ID."""
    normalized = normalize_arxiv_id(arxiv_id)
    return f"https://arxiv.org/abs/{normalized}" if normalized else ""


def build_arxiv_pdf_link(arxiv_id: str) -> str:
    """Build a stable arXiv PDF link from a normalized ID."""
    normalized = normalize_arxiv_id(arxiv_id)
    return f"https://arxiv.org/pdf/{normalized}.pdf" if normalized else ""


def async_retry(max_retries: int = 3, base_delay: float = 1.0):
    """Retry an async function with exponential backoff."""

    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(max_retries):
                try:
                    return await func(*args, **kwargs)
                except Exception as exc:
                    last_exception = exc
                    if attempt < max_retries - 1:
                        delay = base_delay * (2 ** attempt)
                        await asyncio.sleep(delay)
            exception = last_exception
            if exception is None:
                raise RuntimeError("async_retry failed without capturing an exception")
            raise exception

        return wrapper

    return decorator


def format_authors(authors: list) -> list:
    """Format arXiv author objects into serializable dictionaries."""
    return [
        {
            "name": str(author).strip(),
            "affiliation": "",
        }
        for author in authors
    ]


def normalize_author_entries(authors: Any) -> List[Dict[str, str]]:
    """Normalize author entries from persisted JSON or arXiv results."""
    normalized: List[Dict[str, str]] = []

    if not isinstance(authors, list):
        return normalized

    for author in authors:
        if isinstance(author, dict):
            name = str(author.get("name", "")).strip()
            affiliation = str(author.get("affiliation", "")).strip()
        else:
            name = str(author).strip()
            affiliation = ""

        if not name:
            continue

        normalized.append({
            "name": name,
            "affiliation": affiliation,
        })

    return normalized


def merge_unique_strings(*values: Any) -> List[str]:
    """Merge one or more iterables into an ordered list of unique strings."""
    merged: List[str] = []
    seen = set()

    for value in values:
        if not isinstance(value, list):
            continue
        for item in value:
            text = str(item).strip()
            if not text or text in seen:
                continue
            seen.add(text)
            merged.append(text)

    return merged


def build_paper_record(result: Any) -> Dict[str, Any]:
    """Convert an arXiv result object into the normalized paper schema."""
    arxiv_id = normalize_arxiv_id(result.get_short_id())

    return {
        "id": arxiv_id,
        "title": str(result.title).strip(),
        "abstract": str(result.summary).replace("\n", " ").strip(),
        "authors": format_authors(result.authors),
        "categories": list(result.categories),
        "published_date": parse_arxiv_date(str(result.published)),
        "pdf_link": build_arxiv_pdf_link(arxiv_id),
        "abs_link": build_arxiv_abs_link(arxiv_id),
        "tags": [],
        "keywords": [],
        "summary_zh": "",
        "affiliation": "",
    }
