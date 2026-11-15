"""Add AI x finance papers from the top-venue library that the radar missed (S11 补漏).

    python -m scripts.arxiv_radar.discover --since-year 2026 --dry-run   # find, no LLM
    python -m scripts.arxiv_radar.discover --since-year 2026             # find + enrich + merge

1. Candidates: library papers from ``--since-year`` on with the rule flags (finance
   terms; finance journals also need AI terms) that are not in the radar.
2. Their arXiv version: the library's arXiv id, else an OpenAlex title search whose
   locations include arXiv; the arXiv title must match (ratio >= 0.9).
3. Those arXiv papers go through the normal pipeline (LLM relevance and fields,
   institutions, keywords, venue). The LLM decides relevance: rule flags are loose.
Papers with no arXiv version are only counted for now (no abstract to enrich from).
"""

from __future__ import annotations

import argparse
import asyncio
import json
import logging
from difflib import SequenceMatcher
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import quote

import arxiv

from . import venue_library as L
from .config import LLM_API_KEY, openalex_url
from .storage import load_papers
from .utils import build_paper_record, normalize_arxiv_id

logger = logging.getLogger(__name__)


def _openalex_arxiv_id(title: str) -> str:
    """arXiv id of a paper found by title in OpenAlex, or ''. One try: a failed or odd
    title search only means this candidate is skipped."""
    import subprocess

    words = " ".join(w for w in L.re.split(r"[^A-Za-z0-9]+", title) if w)[:200]
    url = openalex_url(f"https://api.openalex.org/works?filter=title.search:{quote(words)}&per-page=5&select=title,locations,doi")
    result = subprocess.run(["curl", "-s", "-A", L.USER_AGENT, "--max-time", "30", url], capture_output=True)
    try:
        data = json.loads(result.stdout or b"{}")
    except json.JSONDecodeError:
        return ""
    for work in data.get("results", []) if isinstance(data, dict) else []:
        if SequenceMatcher(None, L.title_key(work.get("title") or ""), L.title_key(title)).ratio() < 0.9:
            continue
        locations = " ".join(str((l or {}).get("landing_page_url") or "") for l in work.get("locations") or [])
        found = L.arxiv_id_in(locations, work.get("doi") or "")
        if found:
            return found
    return ""


def find_arxiv_versions(candidates: List[Dict[str, Any]]) -> Tuple[Dict[str, Dict[str, Any]], List[Dict[str, Any]]]:
    """{arxiv_id: library row} for candidates with an arXiv version; the rest.
    Title searches run 4 at a time (OpenAlex allows ~10 requests a second)."""
    from concurrent.futures import ThreadPoolExecutor

    found: Dict[str, Dict[str, Any]] = {}
    missing: List[Dict[str, Any]] = []
    need = [row for row in candidates if not row.get("arxiv_id")]
    for row in candidates:
        if row.get("arxiv_id"):
            found.setdefault(row["arxiv_id"], row)
    with ThreadPoolExecutor(max_workers=4) as pool:
        for n, (row, arxiv_id) in enumerate(zip(need, pool.map(lambda r: _openalex_arxiv_id(r["title"]), need)), 1):
            if arxiv_id:
                found.setdefault(arxiv_id, row)
            else:
                missing.append(row)
            if n % 50 == 0 or n == len(need):
                logger.info("Title searches %s/%s: %s candidates have an arXiv version", n, len(need), len(found))
    return found, missing


def fetch_arxiv_records(ids_to_rows: Dict[str, Dict[str, Any]]) -> List[Dict[str, Any]]:
    """arXiv records whose title really is the library paper's title."""
    client = arxiv.Client(page_size=100, delay_seconds=3.0, num_retries=5)
    ids = list(ids_to_rows)
    records = []
    for start in range(0, len(ids), 100):
        batch = ids[start:start + 100]
        for result in client.results(arxiv.Search(id_list=batch, max_results=len(batch))):
            paper = build_paper_record(result)
            row = ids_to_rows.get(normalize_arxiv_id(paper["id"]))
            if row and SequenceMatcher(None, L.title_key(paper["title"]), row["title_key"]).ratio() >= 0.85:
                records.append(paper)
    return records


def main(argv: Optional[List[str]] = None) -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--since-year", type=int, default=2026)
    parser.add_argument("--dry-run", action="store_true", help="find candidates and arXiv versions only")
    args = parser.parse_args(argv)

    rows = L.load_all()
    if not rows:
        raise SystemExit("No library on disk: run `python -m scripts.arxiv_radar.venue_library fetch` first.")
    radar = load_papers().get("papers", [])
    radar_ids = {normalize_arxiv_id(str(p.get("id", ""))) for p in radar}
    candidates = L.missed_finance_papers(radar, rows, args.since_year)
    logger.info("%s library candidates since %s not in the radar", len(candidates), args.since_year)

    found, missing = find_arxiv_versions(candidates)
    found = {k: v for k, v in found.items() if normalize_arxiv_id(k) not in radar_ids}
    records = fetch_arxiv_records(found)
    summary = {"candidates": len(candidates), "with_arxiv": len(found), "arxiv_records": len(records),
               "no_arxiv_version": len(missing)}
    logger.info("Discovery: %s", summary)
    print(json.dumps({**summary, "examples": [r["title"] for r in records[:10]]}, ensure_ascii=False, indent=1))
    if args.dry_run or not records:
        return
    if not LLM_API_KEY:
        raise SystemExit("LLM_API_KEY is not set: run with --dry-run, or export the key.")
    from .fetch_papers import run_pipeline

    asyncio.run(run_pipeline(fetched=records))


if __name__ == "__main__":
    main()
