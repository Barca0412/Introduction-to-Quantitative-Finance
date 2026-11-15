"""Statistics computation for tags, keywords, and site summaries."""

from collections import Counter, defaultdict
from datetime import date, datetime, timedelta
from typing import Dict, Any, List

from .config import MIN_KEYWORD_COUNT, PREDEFINED_TAGS, PRIMARY_FOCUS_TAGS, ARXIV_CATEGORIES
from .enrich import ids as taxonomy_ids
from .storage import save_stats


def compute_tag_stats(papers: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Calculate daily and cumulative tag statistics.

    Args:
        papers: List of paper dictionaries with 'tags' and 'published_date'

    Returns:
        Dictionary with 'daily' and 'cumulative' tag counts by date
    """
    # Get all unique dates
    dates = sorted({p["published_date"] for p in papers if p.get("published_date")})

    # Daily counts
    daily = []
    daily_counts = {}

    for date in dates:
        # Count tags for this date
        counts = defaultdict(int)
        for paper in papers:
            if paper.get("published_date") == date:
                for tag in paper.get("tags", []):
                    if tag in PREDEFINED_TAGS:
                        counts[tag] += 1

        # Ensure all tags are present
        full_counts = {tag: counts.get(tag, 0) for tag in PREDEFINED_TAGS.keys()}
        full_counts = {k: v for k, v in full_counts.items() if v > 0}

        daily.append({"date": date, "counts": full_counts})
        daily_counts[date] = full_counts

    # Cumulative counts
    cumulative = []
    running_counts = defaultdict(int)

    for date in dates:
        # Add today's counts
        for tag, count in daily_counts.get(date, {}).items():
            running_counts[tag] += count

        # Filter to only positive counts
        filtered_counts = {k: v for k, v in running_counts.items() if v > 0}

        cumulative.append({"date": date, "counts": filtered_counts})

    return {"daily": daily, "cumulative": cumulative}


def compute_keyword_stats(
    papers: List[Dict[str, Any]],
    min_count: int = MIN_KEYWORD_COUNT
) -> Dict[str, Any]:
    """
    Calculate daily and cumulative keyword statistics.

    Args:
        papers: List of paper dictionaries with 'keywords' and 'published_date'
        min_count: Minimum count for keyword to appear in stats

    Returns:
        Dictionary with 'daily' and 'cumulative' keyword counts by date
    """
    # Get all unique dates
    dates = sorted({p["published_date"] for p in papers if p.get("published_date")})

    # Collect all keywords first to filter by minimum count
    all_keyword_counts = defaultdict(int)
    for paper in papers:
        for keyword in paper.get("keywords", []):
            all_keyword_counts[keyword.lower()] += 1

    # Filter keywords by minimum count
    valid_keywords = {
        kw for kw, count in all_keyword_counts.items()
        if count >= min_count
    }

    # Daily counts
    daily = []
    daily_counts = {}

    for date in dates:
        # Count keywords for this date
        counts = defaultdict(int)
        for paper in papers:
            if paper.get("published_date") == date:
                for keyword in paper.get("keywords", []):
                    kw_lower = keyword.lower()
                    if kw_lower in valid_keywords:
                        counts[kw_lower] += 1

        # Convert to sorted dict (by count descending)
        sorted_counts = dict(sorted(counts.items(), key=lambda x: -x[1]))

        daily.append({"date": date, "counts": sorted_counts})
        daily_counts[date] = counts

    # Cumulative counts
    cumulative = []
    running_counts = defaultdict(int)

    for date in dates:
        # Add today's counts
        for keyword, count in daily_counts.get(date, {}).items():
            running_counts[keyword] += count

        # Convert to sorted dict (by count descending)
        sorted_counts = dict(sorted(running_counts.items(), key=lambda x: -x[1]))

        cumulative.append({"date": date, "counts": sorted_counts})

    return {"daily": daily, "cumulative": cumulative}


def compute_and_save_stats(papers: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Compute statistics over the full history and save them to data/stats.json."""
    stats = build_stats(papers)
    # What the site shows, for the README status block (full-history numbers above).
    from .site_filter import site_visible

    shown = [p for p in papers if site_visible(p)]
    stats["site_summary"] = {
        "papers": len(shown),
        "core_papers": sum(1 for p in shown if p.get("relevance") == 3),
        "since": min((p.get("published_date", "") for p in shown), default=""),
        "latest": max((p.get("published_date", "") for p in shown), default=""),
    }
    save_stats(stats)
    return stats


FACET_DIMENSIONS = (
    # stats key, paper field, taxonomy key
    ("finance_domains", "finance_domains", "finance_domains"),
    ("task_types", "task_types", "task_types"),
    ("methods", "methods", "methods"),
    ("paper_types", "paper_type", "paper_types"),
    ("data_markets", "data_market", "data_markets"),
)


def _week_start(day: str) -> str:
    """Monday of the ISO week of a YYYY-MM-DD date."""
    parsed = date.fromisoformat(day)
    return (parsed - timedelta(days=parsed.weekday())).isoformat()


def compute_facet_stats(papers: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Counts by the S3 v2 classification, for the trends page and the overview grid.

    Only papers enriched with v2 (they have a paper_type) are counted. A paper with two
    finance domains counts once in each; totals per dimension can therefore exceed the
    number of papers. Series are aligned to ``dates`` (days with papers) and ``weeks``
    (Mondays). ``grid`` is finance domain x task type, in taxonomy order.
    """
    scored = [p for p in papers if p.get("paper_type") and p.get("published_date")]
    dates = sorted({p["published_date"] for p in scored})
    weeks = sorted({_week_start(d) for d in dates})
    day_index = {d: i for i, d in enumerate(dates)}
    week_index = {w: i for i, w in enumerate(weeks)}

    def series() -> Dict[str, List[int]]:
        return {"daily": [0] * len(dates), "weekly": [0] * len(weeks)}

    def bump(target: Dict[str, List[int]], day: str) -> None:
        target["daily"][day_index[day]] += 1
        target["weekly"][week_index[_week_start(day)]] += 1

    total, core = series(), series()
    dims: Dict[str, Any] = {}
    for key, field, tax_key in FACET_DIMENSIONS:
        order = taxonomy_ids(tax_key)
        counted: Dict[str, Dict[str, List[int]]] = {}
        for paper in scored:
            values = paper.get(field) or []
            values = [values] if isinstance(values, str) else values
            for value in dict.fromkeys(values):
                if value not in order:
                    continue
                bump(counted.setdefault(value, series()), paper["published_date"])
        dims[key] = {
            "total": {v: sum(counted[v]["daily"]) for v in order if v in counted},
            "daily": {v: counted[v]["daily"] for v in order if v in counted},
            "weekly": {v: counted[v]["weekly"] for v in order if v in counted},
        }

    for paper in scored:
        bump(total, paper["published_date"])
        if paper.get("relevance") == 3:
            bump(core, paper["published_date"])

    rows, cols = taxonomy_ids("finance_domains"), taxonomy_ids("task_types")
    cells = [[0] * len(cols) for _ in rows]
    for paper in scored:
        for domain in dict.fromkeys(paper.get("finance_domains") or []):
            for task in dict.fromkeys(paper.get("task_types") or []):
                if domain in rows and task in cols:
                    cells[rows.index(domain)][cols.index(task)] += 1

    return {
        "papers": len(scored),
        "dates": dates,
        "weeks": weeks,
        "total": total,
        "core": core,
        "dims": dims,
        "grid": {"rows": rows, "cols": cols, "cells": cells},
    }


def build_stats(papers: List[Dict[str, Any]]) -> Dict[str, Any]:
    """All statistics for a set of papers (the full history, or the site's subset)."""
    tag_stats = compute_tag_stats(papers)
    keyword_stats = compute_keyword_stats(papers)
    summary = compute_site_summary(papers, tag_stats)

    stats = {
        "last_updated": datetime.utcnow().isoformat(),
        "tag_stats": {
            "_all": tag_stats
        },
        "keyword_stats": {
            "_all": keyword_stats
        },
        "summary": summary,
        "facets": compute_facet_stats(papers),
    }
    return stats


def compute_site_summary(papers: List[Dict[str, Any]], tag_stats: Dict[str, Any]) -> Dict[str, Any]:
    """Build a compact summary used by the homepage and focus views."""
    category_counter = Counter(
        category
        for paper in papers
        for category in paper.get("categories", [])
    )
    focus_counter = Counter(
        tag
        for paper in papers
        for tag in paper.get("tags", [])
        if tag in PRIMARY_FOCUS_TAGS
    )
    primary_topic_counter = Counter(
        paper.get("focus", {}).get("primary_topic")
        for paper in papers
        if paper.get("focus", {}).get("primary_topic")
    )
    focus_papers = [paper for paper in papers if paper.get("focus", {}).get("is_focus")]
    latest_date = max((paper.get("published_date", "") for paper in papers), default="")

    return {
        "total_papers": len(papers),
        "focus_papers": len(focus_papers),
        "monitored_categories": len(ARXIV_CATEGORIES),
        "observed_categories": len(category_counter),
        "tracked_tags": len(PREDEFINED_TAGS),
        "latest_published_date": latest_date,
        "focus_tag_counts": dict(focus_counter.most_common()),
        "focus_topic_counts": dict(primary_topic_counter.most_common()),
        "top_categories": dict(category_counter.most_common(10)),
        "tag_days": len(tag_stats.get("daily", [])),
    }


if __name__ == "__main__":
    from .storage import load_papers

    # Load and compute stats
    data = load_papers()
    if data and data.get("papers"):
        print(f"Computing stats for {len(data['papers'])} papers...")
        stats = compute_and_save_stats(data["papers"])
        print(f"Stats saved. Last updated: {stats['last_updated']}")
    else:
        print("No papers found. Run fetch_papers.py first.")
