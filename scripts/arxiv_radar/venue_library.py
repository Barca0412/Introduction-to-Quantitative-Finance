"""S11 accepted-paper library (design doc S11): every accepted paper of the top venues,
per venue and year, kept as data for tagging radar papers, finding missed finance
papers and later analysis.

    python -m scripts.arxiv_radar.venue_library fetch [--venue neurips] [--year 2024] [--since 2020]
    python -m scripts.arxiv_radar.venue_library status

Files: data/venue_library/<venue>-<year>.parquet, one row per paper:
  venue_id, year, track, decision, title, authors, doi, url, arxiv_id, adapter,
  fetched_at, fin_flag (rule prefilter), ai_flag, title_key
Abstracts are read to compute the flags but never stored (user decision 2026-11-15:
abstracts only internal; the library may be published).

Adapters (4.11): virtual_site (NeurIPS/ICML/ICLR official JSON), acl_anthology
(volume BibTeX), openalex_source (source id + year), crossref_issn (journal + year).
DBLP and the OpenReview API sit behind bot checks and are not used.
"""

from __future__ import annotations

import argparse
import ast
import json
import logging
import re
import subprocess
import time
import unicodedata
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional
from urllib.parse import urlencode

from .config import DATA_DIR, FINANCE_TERM_PATTERN, openalex_url, redact

logger = logging.getLogger(__name__)

LIBRARY_DIR = DATA_DIR / "venue_library"
USER_AGENT = "FinPaperRadar/0.2 (+https://github.com/Barca0412/Introduction-to-Quantitative-Finance)"
FIRST_YEAR = 2020

# Where each top venue's accepted papers come from (ids match vocab/venues.yaml).
SOURCES: Dict[str, Dict[str, Any]] = {
    "neurips": {"adapter": "virtual_site", "host": "neurips.cc", "slug": "neurips"},
    "icml": {"adapter": "virtual_site", "host": "icml.cc", "slug": "icml"},
    "iclr": {"adapter": "virtual_site", "host": "iclr.cc", "slug": "iclr"},
    "acl": {"adapter": "acl_anthology", "volumes": ["acl-main", "acl-long", "acl-short", "findings-acl"]},
    "emnlp": {"adapter": "acl_anthology", "volumes": ["emnlp-main", "findings-emnlp"]},
    "naacl": {"adapter": "acl_anthology", "volumes": ["naacl-main", "naacl-long", "naacl-short", "findings-naacl"]},
    "kdd": {"adapter": "openalex_source", "source": "S4363608767"},
    "aaai": {"adapter": "openalex_source", "source": "S4210191458"},
    "ijcai": {"adapter": "openalex_source", "source": "S4306419999"},
    "www": {"adapter": "openalex_source", "source": "S7407088480"},
    "sigir": {"adapter": "openalex_source", "source": "S4363608773"},
    "cikm": {"adapter": "openalex_source", "source": "S4393918199"},
    "wsdm": {"adapter": "openalex_source", "source": "S4363608885"},
    "acm-mm": {"adapter": "openalex_source", "source": "S4363608757"},
    "icaif": {"adapter": "openalex_source", "source": "S7407087532"},
    "jf": {"adapter": "crossref_issn", "issn": "0022-1082"},
    "jfe": {"adapter": "crossref_issn", "issn": "0304-405X"},
    "rfs": {"adapter": "crossref_issn", "issn": "0893-9454"},
}

# Finance venues: every paper is finance; the interesting ones use AI/ML.
FINANCE_VENUES = {"jf", "jfe", "rfs"}
AI_TERM_PATTERN = re.compile(
    r"(?<![a-z])(machine learning|deep learning|neural network|large language model|language model|\bllms?\b|"
    r"reinforcement learning|artificial intelligence|\bai\b|random forest|gradient boost|lasso|"
    r"natural language processing|\bnlp\b|text mining|textual analysis|chatgpt|\bgpt|transformer|"
    r"computer vision|image|alternative data|big data)", re.I)


# --------------------------------------------------------------------------
# HTTP (curl: honours the proxy and system certificates everywhere)
# --------------------------------------------------------------------------

def _get(url: str, attempts: int = 4, timeout: int = 300) -> Optional[bytes]:
    for attempt in range(attempts):
        result = subprocess.run(
            ["curl", "-sL", "--compressed", "-A", USER_AGENT, "--max-time", str(timeout), "-w", "\n%{http_code}", url],
            capture_output=True,
        )
        body, _, code = result.stdout.rpartition(b"\n")
        if code == b"200":
            return body
        if code == b"404":
            return None
        time.sleep(3 * (attempt + 1))
    logger.warning("Giving up on %s", redact(url))
    return None


def _json(url: str, attempts: int = 3) -> Optional[Any]:
    """Parsed JSON, or None for 404. A truncated download (the conference JSON files
    are 15-25 MB) is fetched again; still broken after ``attempts`` raises."""
    for attempt in range(attempts):
        body = _get(url)
        if body is None:
            return None
        try:
            return json.loads(body.decode("utf-8", "ignore"), strict=False)
        except json.JSONDecodeError:
            logger.warning("Broken JSON from %s (%s bytes), retrying", redact(url.split("?")[0]), len(body))
            time.sleep(5 * (attempt + 1))
    raise RuntimeError(f"broken JSON after {attempts} downloads: {redact(url.split('?')[0])}")


# --------------------------------------------------------------------------
# Records
# --------------------------------------------------------------------------

def title_key(title: str) -> str:
    """Comparable title: ASCII, lower case, letters and digits only."""
    text = unicodedata.normalize("NFKD", title or "").encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", "", text)


_ARXIV_ID = re.compile(r"arxiv\.org/(?:abs|pdf)/(\d{4}\.\d{4,5})|10\.48550/arxiv\.(\d{4}\.\d{4,5})", re.I)


def arxiv_id_in(*texts: str) -> str:
    for text in texts:
        found = _ARXIV_ID.search(text or "")
        if found:
            return found.group(1) or found.group(2)
    return ""


def make_record(venue_id: str, year: int, adapter: str, title: str, authors: List[str], abstract: str = "",
                track: str = "main", decision: str = "", doi: str = "", url: str = "", arxiv_id: str = "") -> Dict[str, Any]:
    title = " ".join(re.sub(r"[{}]", "", title or "").split())
    text = f"{title} {abstract or ''}"
    return {
        "venue_id": venue_id, "year": year, "track": track, "decision": decision,
        "title": title, "authors": [a for a in authors if a][:50], "doi": (doi or "").lower(), "url": url,
        "arxiv_id": arxiv_id, "adapter": adapter,
        "fetched_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "fin_flag": bool(FINANCE_TERM_PATTERN.search(text)) or venue_id in FINANCE_VENUES,
        "ai_flag": bool(AI_TERM_PATTERN.search(text)),
        "title_key": title_key(title),
    }


# --------------------------------------------------------------------------
# Adapters
# --------------------------------------------------------------------------

def fetch_virtual_site(venue_id: str, year: int, cfg: Dict[str, Any]) -> List[Dict[str, Any]]:
    url = f"https://{cfg['host']}/static/virtual/data/{cfg['slug']}-{year}-orals-posters.json"
    data = _json(url)
    if not data or not data.get("results"):
        raise RuntimeError(f"no papers in {url}")
    out = []
    for item in data.get("results", []):
        if str(item.get("eventtype") or item.get("event_type") or "").lower() not in ("poster", "oral", "spotlight", ""):
            continue
        authors = item.get("authors") or []
        if isinstance(authors, str):
            try:
                authors = ast.literal_eval(authors)
            except (ValueError, SyntaxError):
                authors = []
        names = [a.get("fullname", "") if isinstance(a, dict) else str(a) for a in authors]
        source = str(item.get("sourceurl") or "")
        track = "datasets_and_benchmarks" if "datasets" in source.lower() or "benchmark" in source.lower() else "main"
        out.append(make_record(
            venue_id, year, "virtual_site", item.get("name", ""), names, item.get("abstract") or "",
            track=track, decision=str(item.get("decision") or item.get("eventtype") or ""),
            url=str(item.get("paper_url") or f"https://{cfg['host']}{item.get('virtualsite_url', '')}"),
            arxiv_id=arxiv_id_in(str(item.get("paper_pdf_url") or ""), str(item.get("url") or "")),
        ))
    return out


_BIB_ENTRY = re.compile(r"@inproceedings\{[^,]+,(.*?)\n\}", re.S)
_BIB_FIELD = re.compile(r'(\w+)\s*=\s*"((?:[^"\\]|\\.)*)"', re.S)


def _bib_authors(text: str) -> List[str]:
    names = []
    for part in re.split(r"\s+and\s+", " ".join(text.split())):
        part = re.sub(r"[{}]", "", part)
        if "," in part:
            last, first = part.split(",", 1)
            part = f"{first.strip()} {last.strip()}"
        names.append(part.strip())
    return names


def fetch_acl_anthology(venue_id: str, year: int, cfg: Dict[str, Any]) -> List[Dict[str, Any]]:
    out = []
    for volume in cfg["volumes"]:
        body = _get(f"https://aclanthology.org/volumes/{year}.{volume}.bib")
        if not body:
            continue
        for entry in _BIB_ENTRY.findall(body.decode("utf-8", "ignore")):
            fields = {k.lower(): v for k, v in _BIB_FIELD.findall(entry)}
            if not fields.get("title"):
                continue
            out.append(make_record(
                venue_id, year, "acl_anthology", fields["title"], _bib_authors(fields.get("author", "")),
                fields.get("abstract", ""), track="findings" if volume.startswith("findings") else volume.split("-", 1)[1],
                decision="accept", doi=fields.get("doi", ""), url=fields.get("url", ""),
            ))
    return out


def _abstract(inverted: Optional[Dict[str, List[int]]]) -> str:
    if not inverted:
        return ""
    words = sorted((pos, word) for word, positions in inverted.items() for pos in positions)
    return " ".join(word for _, word in words)


def _track_by_pages(biblio: Optional[Dict[str, Any]]) -> str:
    """Proceedings indexed in OpenAlex mix papers with 1-2 page items (keynotes, tutorial
    and workshop descriptions, student abstracts). >= 5 pages: full paper; 3-4: short
    paper; <= 2: abstract (not an accepted paper, not used for tagging); no pages: unknown."""
    try:
        pages = int((biblio or {}).get("last_page")) - int((biblio or {}).get("first_page")) + 1
    except (TypeError, ValueError):
        return "unknown"
    if pages <= 0:
        return "unknown"
    return "full" if pages >= 5 else "short" if pages >= 3 else "abstract"


def fetch_openalex_source(venue_id: str, year: int, cfg: Dict[str, Any]) -> List[Dict[str, Any]]:
    # Numbered pages: since 2026 OpenAlex wants an API key for cursor paging, while
    # page=N works without one up to 10,000 results (the largest venue-year here,
    # AAAI 2026, has ~4,900).
    out: List[Dict[str, Any]] = []
    page, total = 1, None
    while total is None or (page - 1) * 200 < min(total, 10_000):
        query = urlencode({
            "filter": f"primary_location.source.id:{cfg['source']},publication_year:{year}",
            "per-page": 200, "page": page,
            "select": "id,doi,title,authorships,locations,ids,abstract_inverted_index,type,biblio",
        })
        data = _json(openalex_url(f"https://api.openalex.org/works?{query}"))
        if not data or not data.get("results"):
            if total is not None and len(out) < total:
                raise RuntimeError(f"{venue_id} {year}: OpenAlex stopped at {len(out)} of {total}")
            break
        total = (data.get("meta") or {}).get("count", 0)
        for work in data["results"]:
            locations = " ".join(str((l or {}).get("landing_page_url") or "") for l in work.get("locations") or [])
            out.append(make_record(
                venue_id, year, "openalex_source", work.get("title") or "",
                [((a.get("author") or {}).get("display_name") or "") for a in work.get("authorships") or []],
                _abstract(work.get("abstract_inverted_index")),
                track=_track_by_pages(work.get("biblio")),
                decision="published", doi=(work.get("doi") or "").replace("https://doi.org/", ""),
                url=work.get("id", ""), arxiv_id=arxiv_id_in(locations, work.get("doi") or ""),
            ))
        page += 1
        time.sleep(0.2)
    return out


def fetch_crossref_issn(venue_id: str, year: int, cfg: Dict[str, Any]) -> List[Dict[str, Any]]:
    out, cursor = [], "*"
    while cursor:
        query = urlencode({
            "filter": f"from-pub-date:{year}-01-01,until-pub-date:{year}-12-31,type:journal-article",
            "rows": 500, "cursor": cursor, "select": "DOI,title,author,abstract,URL",
        })
        data = _json(f"https://api.crossref.org/journals/{cfg['issn']}/works?{query}")
        items = ((data or {}).get("message") or {}).get("items") or []
        if not items:
            break
        for item in items:
            authors = [f"{a.get('given', '')} {a.get('family', '')}".strip() for a in item.get("author") or []]
            out.append(make_record(
                venue_id, year, "crossref_issn", (item.get("title") or [""])[0], authors,
                re.sub(r"<[^>]+>", " ", item.get("abstract") or ""), decision="published",
                doi=item.get("DOI", ""), url=item.get("URL", ""),
            ))
        cursor = data["message"].get("next-cursor")
        time.sleep(0.5)
    return out


ADAPTERS = {
    "virtual_site": fetch_virtual_site,
    "acl_anthology": fetch_acl_anthology,
    "openalex_source": fetch_openalex_source,
    "crossref_issn": fetch_crossref_issn,
}


# --------------------------------------------------------------------------
# Storage
# --------------------------------------------------------------------------

def _schema():
    import pyarrow as pa

    return pa.schema([
        ("venue_id", pa.string()), ("year", pa.int32()), ("track", pa.string()), ("decision", pa.string()),
        ("title", pa.string()), ("authors", pa.list_(pa.string())), ("doi", pa.string()), ("url", pa.string()),
        ("arxiv_id", pa.string()), ("adapter", pa.string()), ("fetched_at", pa.string()),
        ("fin_flag", pa.bool_()), ("ai_flag", pa.bool_()), ("title_key", pa.string()),
    ])


def path_for(venue_id: str, year: int) -> Path:
    return LIBRARY_DIR / f"{venue_id}-{year}.parquet"


def dedupe(records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """One row per paper: the official conference JSON lists an oral paper twice (oral and
    poster session), OpenAlex sometimes has two works for one paper. Same title_key = same
    paper; the first row is kept and filled with the others' links and flags."""
    kept: Dict[str, Dict[str, Any]] = {}
    out: List[Dict[str, Any]] = []
    for rec in records:
        key = rec.get("title_key") or ""
        first = kept.get(key) if key else None
        if first is None:
            rec = dict(rec)
            if key:
                kept[key] = rec
            out.append(rec)
            continue
        for field in ("doi", "url", "arxiv_id"):
            if not first.get(field) and rec.get(field):
                first[field] = rec[field]
        first["fin_flag"] = bool(first.get("fin_flag") or rec.get("fin_flag"))
        first["ai_flag"] = bool(first.get("ai_flag") or rec.get("ai_flag"))
    return out


def save(venue_id: str, year: int, records: List[Dict[str, Any]]) -> Path:
    import pyarrow as pa
    import pyarrow.parquet as pq

    records = dedupe(records)
    LIBRARY_DIR.mkdir(parents=True, exist_ok=True)
    path = path_for(venue_id, year)
    pq.write_table(pa.Table.from_pylist(records, schema=_schema()), path, compression="zstd")
    return path


def load_all() -> List[Dict[str, Any]]:
    import pyarrow.parquet as pq

    rows: List[Dict[str, Any]] = []
    for path in sorted(LIBRARY_DIR.glob("*.parquet")):
        rows.extend(pq.read_table(path).to_pylist())
    return rows


def fetch(venue_id: str, year: int) -> int:
    cfg = SOURCES[venue_id]
    records = dedupe(ADAPTERS[cfg["adapter"]](venue_id, year, cfg))
    if records:
        save(venue_id, year, records)
    logger.info("%s %s: %s papers (%s finance-flagged)", venue_id, year, len(records), sum(r["fin_flag"] for r in records))
    return len(records)


# --------------------------------------------------------------------------
# Matching radar papers to the library (design S11 "匹配")
# --------------------------------------------------------------------------

def _surnames(names: Iterable[str]) -> set:
    out = set()
    for name in names:
        parts = re.split(r"[^a-z]+", unicodedata.normalize("NFKD", str(name)).encode("ascii", "ignore").decode().lower())
        parts = [p for p in parts if len(p) > 1]
        if parts:
            out.add(parts[-1])
    return out


class LibraryIndex:
    """Lookup by arXiv id, DOI and title; fuzzy title (ratio >= 0.90) only with a
    shared author surname, since camera-ready titles often differ by a few words."""

    FUZZY = 0.90

    def __init__(self, rows: List[Dict[str, Any]]):
        self.by_arxiv: Dict[str, Dict[str, Any]] = {}
        self.by_doi: Dict[str, Dict[str, Any]] = {}
        self.by_title: Dict[str, Dict[str, Any]] = {}
        self.buckets: Dict[str, List[Dict[str, Any]]] = {}
        for row in rows:
            if row.get("track") == "abstract":  # keynotes, tutorials, 2-page abstracts
                continue
            row["_surnames"] = _surnames(row.get("authors") or [])
            if row.get("arxiv_id"):
                self.by_arxiv.setdefault(row["arxiv_id"], row)
            if row.get("doi"):
                self.by_doi.setdefault(row["doi"].lower(), row)
            key = row.get("title_key") or ""
            if len(key) >= 12:
                self.by_title.setdefault(key, row)
                # Two buckets (start and end of the title) so a changed word at either
                # end still leaves one shared bucket for the fuzzy comparison.
                for bucket in {"^" + key[:8], "$" + key[-8:]}:
                    self.buckets.setdefault(bucket, []).append(row)

    def match(self, paper: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        from difflib import SequenceMatcher

        arxiv_id = str(paper.get("id", "")).split("v")[0]
        if arxiv_id in self.by_arxiv:
            return {**self.by_arxiv[arxiv_id], "match_method": "arxiv_id"}
        doi = str(paper.get("doi") or "").lower()
        if doi and doi in self.by_doi:
            return {**self.by_doi[doi], "match_method": "doi"}
        key = title_key(paper.get("title", ""))
        if len(key) < 12:
            return None
        if key in self.by_title:
            return {**self.by_title[key], "match_method": "title_exact"}
        authors = _surnames(a.get("name", "") if isinstance(a, dict) else a for a in paper.get("authors") or [])
        if not authors:
            return None
        best, best_ratio = None, self.FUZZY
        candidates = {id(r): r for b in ("^" + key[:8], "$" + key[-8:]) for r in self.buckets.get(b, [])}
        for row in candidates.values():
            other = row["title_key"]
            # Cheap filters first: a shared author, similar length, then difflib.
            if abs(len(other) - len(key)) > 0.2 * max(len(key), len(other)):
                continue
            if not authors & row["_surnames"]:
                continue
            matcher = SequenceMatcher(None, key, other)
            if matcher.real_quick_ratio() < best_ratio or matcher.quick_ratio() < best_ratio:
                continue
            ratio = matcher.ratio()
            if ratio >= best_ratio:
                best, best_ratio = row, ratio
        if best is None:
            return None
        return {**{k: v for k, v in best.items() if k != "_surnames"}, "match_method": "title_fuzzy"}


def tag_papers(papers: List[Dict[str, Any]], rows: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
    """Set ``venue_list`` on every v2-enriched paper found in the library (else None).
    venues.classify_paper then prefers it over what the authors wrote."""
    rows = load_all() if rows is None else rows
    if not rows:
        return {"library_papers": 0, "matched": 0}
    index = LibraryIndex(rows)
    matched, methods = 0, {}
    for paper in papers:
        if paper.get("relevance") is None:
            continue
        hit = index.match(paper)
        paper["venue_list"] = None if hit is None else {
            "venue_id": hit["venue_id"], "year": hit["year"], "track": hit["track"],
            "decision": hit["decision"], "match_method": hit["match_method"],
        }
        if hit:
            matched += 1
            methods[hit["match_method"]] = methods.get(hit["match_method"], 0) + 1
    return {"library_papers": len(rows), "matched": matched, "methods": methods}


def missed_finance_papers(papers: List[Dict[str, Any]], rows: List[Dict[str, Any]], since_year: int) -> List[Dict[str, Any]]:
    """Library papers from ``since_year`` on that look like AI x finance (rule flags)
    but are not in the radar: candidates to add (design S11 "补漏")."""
    in_radar = {(p.get("venue_list") or {}).get("venue_id", "") + "|" + title_key(p.get("title", "")) for p in papers}
    radar_titles = {title_key(p.get("title", "")) for p in papers}
    out = []
    for row in rows:
        if row["year"] < since_year or not row["fin_flag"]:
            continue
        if row["venue_id"] in FINANCE_VENUES and not row["ai_flag"]:
            continue
        if row["title_key"] in radar_titles or f"{row['venue_id']}|{row['title_key']}" in in_radar:
            continue
        out.append(row)
    return out


def years(since: int = FIRST_YEAR) -> List[int]:
    return list(range(since, datetime.now(timezone.utc).year + 1))


def _arxiv_title_query(title: str) -> str:
    words = re.sub(r"[^A-Za-z0-9 ]+", " ", unicodedata.normalize("NFKD", title)).split()
    return 'ti:"' + " ".join(words[:14]) + '"' if len(words) >= 3 else ""


def arxiv_flags(venue_id: str, year: int, batch: int = 20) -> Dict[str, int]:
    """Rule flags from arXiv abstracts for library rows that came without an abstract.

    The 2026 NeurIPS / ICML / ICLR files have no abstracts, so their finance flag only
    saw the title (NeurIPS 2026: 11 of 9,114 flagged; 2025 with abstracts: 61). This asks
    the arXiv API by title, 20 titles per request, 3 s apart (arXiv's rule), keeps hits
    whose title matches (ratio >= 0.9), records the arXiv id and ORs the flags."""
    import arxiv
    from difflib import SequenceMatcher

    path = path_for(venue_id, year)
    import pyarrow.parquet as pq

    rows = pq.read_table(path).to_pylist()
    todo = [r for r in rows if not r.get("arxiv_id") and _arxiv_title_query(r["title"])]
    client = arxiv.Client(page_size=100, delay_seconds=3.0, num_retries=3)
    found = flagged = 0
    for start in range(0, len(todo), batch):
        group = todo[start:start + batch]
        query = " OR ".join(_arxiv_title_query(r["title"]) for r in group)
        try:
            results = list(client.results(arxiv.Search(query=query, max_results=batch * 2)))
        except Exception as exc:  # one failed batch only leaves those rows as they were
            logger.warning("arXiv batch %s failed: %s", start // batch, exc)
            continue
        for row in group:
            best, ratio = None, 0.9
            for res in results:
                r = SequenceMatcher(None, row["title_key"], title_key(res.title)).ratio()
                if r >= ratio:
                    best, ratio = res, r
            if best is None:
                continue
            found += 1
            row["arxiv_id"] = best.get_short_id().split("v")[0]
            text = f"{row['title']} {best.summary}"
            fin = bool(FINANCE_TERM_PATTERN.search(text))
            flagged += fin and not row["fin_flag"]
            row["fin_flag"] = row["fin_flag"] or fin
            row["ai_flag"] = row["ai_flag"] or bool(AI_TERM_PATTERN.search(text))
        if (start // batch) % 25 == 24:
            save(venue_id, year, rows)
            logger.info("%s %s: %s/%s asked, %s on arXiv, %s newly finance-flagged",
                        venue_id, year, start + len(group), len(todo), found, flagged)
    save(venue_id, year, rows)
    summary = {"rows": len(rows), "asked": len(todo), "on_arxiv": found, "newly_flagged": flagged,
               "finance_flagged": sum(r["fin_flag"] for r in rows)}
    logger.info("%s %s arXiv flags: %s", venue_id, year, summary)
    return summary


def main(argv: Optional[Iterable[str]] = None) -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")
    parser = argparse.ArgumentParser(description="Top-venue accepted-paper library (S11)")
    sub = parser.add_subparsers(dest="cmd", required=True)
    f = sub.add_parser("fetch")
    f.add_argument("--venue", action="append", choices=sorted(SOURCES))
    f.add_argument("--year", type=int, action="append")
    f.add_argument("--since", type=int, default=FIRST_YEAR)
    f.add_argument("--missing-only", action="store_true", help="skip venue-years already on disk")
    sub.add_parser("status")
    a = sub.add_parser("arxiv-flags", help="finance/AI flags from arXiv abstracts for rows without one")
    a.add_argument("--venue", action="append", required=True, choices=sorted(SOURCES))
    a.add_argument("--year", type=int, required=True)
    args = parser.parse_args(list(argv) if argv is not None else None)

    if args.cmd == "status":
        rows = load_all()
        from collections import Counter

        by = Counter((r["venue_id"], r["year"]) for r in rows)
        for (venue, year), count in sorted(by.items()):
            fin = sum(1 for r in rows if r["venue_id"] == venue and r["year"] == year and r["fin_flag"])
            print(f"{venue:8} {year}  {count:6}  finance-flagged {fin}")
        print(f"total {len(rows)} papers, {sum(r['fin_flag'] for r in rows)} finance-flagged")
        return

    if args.cmd == "arxiv-flags":
        for venue in args.venue:
            print(json.dumps({venue: arxiv_flags(venue, args.year)}))
        return

    failed = []
    for venue in args.venue or sorted(SOURCES):
        for year in args.year or years(args.since):
            if args.missing_only and path_for(venue, year).exists():
                continue
            try:
                fetch(venue, year)
            except Exception as exc:  # keep going; nothing partial is saved
                logger.error("%s %s failed: %s", venue, year, exc)
                failed.append(f"{venue}-{year}")
    if failed:
        raise SystemExit(f"Failed: {', '.join(failed)}")


if __name__ == "__main__":
    main()
