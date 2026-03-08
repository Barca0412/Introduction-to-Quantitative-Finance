"""Statistics computation for tags, keywords, and site summaries."""

from collections import Counter, defaultdict
from datetime import datetime
from typing import Dict, Any, List

from .config import MIN_KEYWORD_COUNT, PREDEFINED_TAGS, PRIMARY_FOCUS_TAGS, ARXIV_CATEGORIES
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
    """
    Compute all statistics and save to file.

    Args:
        papers: List of paper dictionaries

    Returns:
        Complete statistics dictionary
    """
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
    }

    save_stats(stats)

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
