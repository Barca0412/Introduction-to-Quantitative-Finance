"""NBER working papers (design doc: non-arXiv sources, "nber_api").

    python -m scripts.arxiv_radar.nber --since 2026-01-01 --dry-run   # list + rule filter, no LLM
    python -m scripts.arxiv_radar.nber --since 2026-01-01             # ... + enrich + merge

1. List: NBER's public listing API (newest first, the one the NBER site uses),
   paged until the papers are older than ``--since``. robots.txt allows /api and /papers.
2. Details: each new paper's page (standard citation_* meta tags, the full abstract,
   its NBER programs). Pages that were read and rejected are remembered in
   data/nber_seen.json, so a daily run only reads the week's new papers. One request at a time, >= 1 s apart.
3. Rule filter: AI / ML terms in title or abstract (same pattern as the venue library).
   Every NBER paper is economics, so finance relevance is left to the LLM (S3) like
   for arXiv; the rule only keeps the LLM bill to the AI candidates.
4. Papers whose title the radar already has (an arXiv version) are skipped.
   The rest join with id "nber:w12345", DOI 10.3386/w12345, journal_ref
   "NBER Working Paper w12345" (venue: working paper, finance-econ) and no PDF link.
"""

from __future__ import annotations

import argparse
import asyncio
import html
import json
import logging
import re
import time
from datetime import date
from typing import Any, Dict, List, Optional, Tuple

from . import venue_library as L
from .config import DATA_DIR, LLM_API_KEY
from .storage import load_papers

logger = logging.getLogger(__name__)

BASE = "https://www.nber.org"
LIST_URL = BASE + "/api/v1/working_page_listing/contentType/working_paper/_/_/search?page={page}&perPage=100"
SEEN_FILE = DATA_DIR / "nber_seen.json"
DELAY = 1.0
MONTHS = {m: i for i, m in enumerate(["january", "february", "march", "april", "may", "june", "july", "august",
                                      "september", "october", "november", "december"], 1)}


def _month_start(display: str) -> Optional[str]:
    """'November 2026' -> '2026-11-01'."""
    parts = (display or "").lower().split()
    if len(parts) == 2 and parts[0] in MONTHS and parts[1].isdigit():
        return f"{parts[1]}-{MONTHS[parts[0]]:02d}-01"
    return None


def list_papers(since: str, max_pages: int = 60) -> List[Dict[str, Any]]:
    """Listing entries (number, title, month) from the newest back to ``since``'s month."""
    floor = since[:7] + "-01"
    out: List[Dict[str, Any]] = []
    for page in range(1, max_pages + 1):
        data = L._json(LIST_URL.format(page=page))
        results = (data or {}).get("results") or []
        if not results:
            break
        older = 0
        for item in results:
            number = str(item.get("url", "")).rsplit("/", 1)[-1]
            month = _month_start(item.get("displaydate", ""))
            if not re.fullmatch(r"w\d+", number) or not month:
                continue
            if month < floor:
                older += 1
                continue
            out.append({"number": number, "title": html.unescape(item.get("title") or ""), "month": month})
        if older == len(results):  # a whole page before --since: done (the list is newest first)
            break
        time.sleep(DELAY)
    return out


_META = re.compile(r'<meta name="(citation_[a-z_]+)" content="([^"]*)"')
_PROGRAM = re.compile(r'programs-working-groups/[a-z-]+"[^>]*>([^<]+)<')


def parse_page(text: str) -> Dict[str, Any]:
    """Title, authors, date, DOI, abstract and programs from a paper page."""
    meta: Dict[str, List[str]] = {}
    for key, value in _META.findall(text):
        meta.setdefault(key, []).append(html.unescape(value).strip())
    start = text.find("page-header__intro-inner")
    abstract, programs = "", []
    if start >= 0:
        block = re.search(r"<p>(.*?)</p>", text[start:start + 20000], re.S)
        if block:
            abstract = " ".join(html.unescape(re.sub(r"<[^>]+>", " ", block.group(1))).split())
        # The paper's own programs follow the abstract; the site menu above lists them all.
        programs = list(dict.fromkeys(html.unescape(p).strip() for p in _PROGRAM.findall(text[start:])))
    day = (meta.get("citation_publication_date") or [""])[0].replace("/", "-")
    return {
        "title": (meta.get("citation_title") or [""])[0],
        "authors": meta.get("citation_author") or [],
        "date": day if re.fullmatch(r"\d{4}-\d{2}-\d{2}", day) else "",
        "doi": (meta.get("citation_doi") or [""])[0].lower(),
        "number": (meta.get("citation_technical_report_number") or [""])[0],
        "abstract": abstract,
        "programs": programs,
    }


def to_record(number: str, page: Dict[str, Any], month: str) -> Dict[str, Any]:
    doi = page["doi"] or f"10.3386/{number}"
    return {
        "id": f"nber:{number}",
        "title": page["title"],
        "abstract": page["abstract"],
        "authors": [{"name": a} for a in page["authors"]],
        "categories": [],
        "published_date": page["date"] or month,
        "pdf_link": "",
        "abs_link": f"{BASE}/papers/{number}",
        "doi": doi,
        "journal_ref": f"NBER Working Paper {number}",
        "source": "nber",
        "nber_programs": page["programs"],
        "tags": [], "keywords": [], "summary_zh": "", "affiliation": "",
    }


def load_seen() -> Dict[str, Any]:
    try:
        return json.loads(SEEN_FILE.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def collect(since: str, limit: int = 0) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    """Records of AI candidates not in the radar yet, and a summary."""
    radar = load_papers().get("papers", [])
    have_ids = {str(p.get("id")) for p in radar}
    have_titles = {L.title_key(p.get("title", "")) for p in radar}
    seen = load_seen()
    listed = list_papers(since)
    todo = [x for x in listed if f"nber:{x['number']}" not in have_ids and x["number"] not in seen]
    if limit:
        todo = todo[:limit]
    logger.info("NBER: %s papers since %s, %s new to read", len(listed), since, len(todo))

    records, read, failed = [], 0, 0
    for n, item in enumerate(todo, 1):
        body = L._get(f"{BASE}/papers/{item['number']}", attempts=3, timeout=60)
        time.sleep(DELAY)
        if body is None:
            failed += 1
            continue
        page = parse_page(body.decode("utf-8", "replace"))
        read += 1
        ai = bool(L.AI_TERM_PATTERN.search(f"{page['title']} {page['abstract']}"))
        dup = L.title_key(page["title"]) in have_titles
        if ai and not dup and len(page["abstract"]) >= 80:
            # Not remembered as seen: once merged its id is in the radar; if the LLM run
            # fails it is read again next time.
            records.append(to_record(item["number"], page, item["month"]))
        else:
            seen[item["number"]] = {"ai": ai, "dup": dup, "date": page["date"] or item["month"]}
        if n % 50 == 0:
            logger.info("NBER: read %s/%s pages, %s AI candidates", n, len(todo), len(records))
            SEEN_FILE.write_text(json.dumps(seen, indent=0), encoding="utf-8")
    SEEN_FILE.write_text(json.dumps(seen, indent=0), encoding="utf-8")
    summary = {"listed": len(listed), "read": read, "failed": failed, "ai_candidates": len(records),
               "already_in_radar_by_title": sum(1 for x in todo if seen.get(x["number"], {}).get("dup"))}
    return records, summary


def main(argv: Optional[List[str]] = None) -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--since", default=f"{date.today().year}-01-01", help="YYYY-MM-DD (month precision)")
    parser.add_argument("--limit", type=int, default=0, help="read at most N new pages (testing)")
    parser.add_argument("--dry-run", action="store_true", help="list and filter only, no LLM")
    args = parser.parse_args(argv)

    records, summary = collect(args.since, args.limit)
    print(json.dumps({**summary, "examples": [r["title"] for r in records[:10]]}, ensure_ascii=False, indent=1))
    if args.dry_run or not records:
        return
    if not LLM_API_KEY:
        raise SystemExit("LLM_API_KEY is not set: run with --dry-run, or export the key.")
    from .fetch_papers import run_pipeline

    asyncio.run(run_pipeline(fetched=records))


if __name__ == "__main__":
    main()
