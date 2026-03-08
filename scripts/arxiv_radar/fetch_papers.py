"""Main paper fetching script for the daily radar pipeline."""

import asyncio
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

import arxiv

from .affiliations import enrich_affiliations
from .compute_stats import compute_and_save_stats
from .config import ARXIV_CATEGORIES, FETCH_DAYS, MAX_RESULTS_PER_CATEGORY
from .generate_charts import copy_data_to_public, generate_all_charts, generate_combined_chart
from .llm_processor import process_papers_batch
from .storage import load_papers, merge_papers, save_papers
from .utils import build_paper_record, get_target_dates


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def fetch_category_papers(
    category: str,
    target_dates: List[str],
    max_results: int = MAX_RESULTS_PER_CATEGORY,
) -> List[Dict[str, Any]]:
    """Fetch papers from a single arXiv category and filter by target dates."""
    logger.info("Fetching papers from category: %s", category)

    papers: List[Dict[str, Any]] = []
    client = arxiv.Client()
    target_date_set = set(target_dates)

    try:
        search = arxiv.Search(
            query=f"cat:{category}",
            max_results=max_results,
            sort_by=arxiv.SortCriterion.SubmittedDate,
            sort_order=arxiv.SortOrder.Descending,
        )

        for result in client.results(search):
            paper = build_paper_record(result)
            if paper["published_date"] not in target_date_set:
                continue
            papers.append(paper)

        logger.info("Fetched %s papers from %s", len(papers), category)
    except Exception as exc:
        logger.error("Error fetching from %s: %s", category, exc)

    return papers


async def fetch_all_categories_parallel(
    categories: List[str],
    days: int = FETCH_DAYS,
) -> List[Dict[str, Any]]:
    """Fetch recent papers from all monitored categories in parallel."""
    target_dates = get_target_dates(days)
    logger.info("Fetching papers for target dates: %s", ", ".join(target_dates))
    logger.info("Fetching papers from %s categories...", len(categories))

    loop = asyncio.get_running_loop()
    tasks = [
        loop.run_in_executor(None, fetch_category_papers, category, target_dates)
        for category in categories
    ]

    results = await asyncio.gather(*tasks)
    all_papers: List[Dict[str, Any]] = []
    for papers in results:
        all_papers.extend(papers)

    logger.info("Total raw papers fetched: %s", len(all_papers))
    return all_papers


async def run_pipeline() -> Optional[Dict[str, Any]]:
    """Run the daily fetch -> enrich -> persist -> stats pipeline."""
    logger.info("=" * 60)
    logger.info("Starting LLM-Finance-Radar paper fetch pipeline")
    logger.info("=" * 60)

    logger.info("\n[Step 1] Fetching papers from arXiv...")
    fetched_papers = await fetch_all_categories_parallel(ARXIV_CATEGORIES)
    if not fetched_papers:
        logger.warning("No papers fetched. Exiting.")
        return None

    deduped_batch = merge_papers({"papers": []}, fetched_papers)["papers"]
    if len(deduped_batch) != len(fetched_papers):
        logger.info(
            "Deduplicated %s overlapping category hits before LLM processing",
            len(fetched_papers) - len(deduped_batch),
        )

    logger.info("\n[Step 2] Processing %s papers with LLM...", len(deduped_batch))
    processed_papers = await process_papers_batch(deduped_batch)

    logger.info("\n[Step 3] Normalizing affiliations...")
    enriched_papers = await enrich_affiliations(processed_papers)

    logger.info("\n[Step 4] Merging with existing data...")
    existing = load_papers()
    merged = merge_papers(existing, enriched_papers)
    logger.info("Total papers after merge: %s", merged["total_count"])

    logger.info("\n[Step 5] Saving papers data...")
    save_papers(merged)
    logger.info("Papers saved successfully")

    logger.info("\n[Step 6] Computing statistics...")
    stats = compute_and_save_stats(merged["papers"])
    logger.info("Statistics saved. Tracked dates: %s", len(stats["tag_stats"]["_all"]["daily"]))

    logger.info("\n[Step 7] Generating charts and public data...")
    generate_all_charts(stats)
    generate_combined_chart(stats)
    copy_data_to_public()
    logger.info("Charts and public data refreshed")

    logger.info("\n" + "=" * 60)
    logger.info("Pipeline completed successfully")
    logger.info("=" * 60)

    return {
        "new_papers": len(deduped_batch),
        "total_papers": merged["total_count"],
    }


if __name__ == "__main__":
    asyncio.run(run_pipeline())
