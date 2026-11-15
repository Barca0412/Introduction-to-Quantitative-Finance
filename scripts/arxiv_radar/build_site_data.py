"""Build the light-weight Radar data served by the VitePress site.

Reads the full history from ``data/`` (papers.json, embeddings.f32) and writes
``docs/public/arxiv-data/`` for the papers the site shows: scored relevance >= 2 by
the LLM, using an AI/ML method, not withdrawn (site_visible). The rest stays in the
published dataset.

    manifest.json                    what exists, sizes, theme vectors, schema
    stats.json                       trend statistics of the shown papers (Trends / overview)
    recent/papers-N.json             last ~90 days, slim records (first load)
    recent/details-N.json           Chinese key points and stable entity links, on demand
    recent/vectors-N.i8              int8 embeddings, row-major, loaded on demand
    recent/vectors-N.json            {"ids": [...], "scales": [...]} for that .i8
    archive/YYYY-MM/...              same four kinds for older months, on demand

Constraints (see config.py): every file <= SITE_MAX_FILE_BYTES and the Papers
page's first load (manifest + recent/papers-*) <= SITE_FIRST_LOAD_BUDGET. If the
budget is exceeded the recent window shrinks week by week (not below
SITE_MIN_RECENT_DAYS). Only metadata and our Chinese summaries are published; no English abstracts,
full text or figures.

Usage::

    python -m scripts.arxiv_radar.build_site_data
"""

from __future__ import annotations

import json
import logging
import shutil
from collections import defaultdict
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

from .config import (
    SITE_DATA_DIR,
    SITE_FIRST_LOAD_BUDGET,
    SITE_MAX_AUTHORS,
    SITE_MAX_FILE_BYTES,
    SITE_MIN_RECENT_DAYS,
    SITE_MIN_RELEVANCE,
    SITE_REQUIRE_AI_METHOD,
    SITE_RECENT_DAYS,
    PAPERS_FILE,
)
from .compute_stats import build_stats
from . import leaders, trends
from .enrich import ENRICH_VERSION, taxonomy
from .site_filter import site_visible
from .utils import is_arxiv_id
from .data_store import load_local_embeddings

logger = logging.getLogger("arxiv_radar.build_site_data")

SCHEMA = {
    "id": "stable paper id (arXiv, DOI, venue or NBER)",
    "t": "title",
    "a": f"author names (first {SITE_MAX_AUTHORS})",
    "an": "total author count, only when authors were truncated",
    "c": "arXiv categories",
    "d": "published date YYYY-MM-DD",
    "g": "tags",
    "k": "keywords",
    "z": "Chinese summary",
    "f": "affiliations",
    "u": "paper landing-page URL",
    "p": "PDF URL, empty when unavailable",
    "ar": "1 for arXiv records, 0 for other sources",
    "fo": "focus: s=score, f=is_focus(0/1), p=primary topic, t=topics, r=reasons",
    # S3 v2 enrichment and P2 fields; ids are explained in taxonomy.json.
    "r": "relevance to AI x finance, 2 or 3 on the site (3 = core)",
    "pt": "paper type id",
    "tt": "task type ids",
    "fd": "finance domain ids",
    "m": "method ids",
    "dm": "data market ids (omitted when not stated)",
    "tl": "one-sentence Chinese summary (tldr_zh)",
    "kn": "standard keywords: [id, Chinese name or English, kind f|t]",
    "v": "venue: n=name, k=kind, s=status, y=year (only when recognised); o=1 when it comes from the"
         " venue's official accepted list, t=track/decision from that list (e.g. Spotlight)",
    "vm": "venue as the authors wrote it, when not recognised",
    "ds": "discipline: cs | finance-econ | interdisciplinary | other (omitted when unknown)",
    "cd": "1 when the code is said to be released",
    "dc": "index of the details-N.json chunk for this paper",
}

# details-N.json: {paper id: {...}}, loaded when a paper is opened.
DETAIL_SCHEMA = {
    "pz": "Chinese key points: problem, method, result, limitation",
    "rr": "one-line Chinese reason for the relevance score",
    "ins": "institutions: n=name, c=country code, t=type (education/company/...)",
    "aa": "per author (same order as au), indices into ins",
    "au": "authors: id=stable identity, n=name, page=existing author page or empty",
}


def _dumps(payload: Any) -> bytes:
    return json.dumps(payload, ensure_ascii=False, separators=(",", ":")).encode("utf-8")


def slim_paper(paper: Dict[str, Any]) -> Tuple[Dict[str, Any], Optional[str]]:
    """Return public metadata and None; abstracts remain in the internal dataset."""
    authors = [a.get("name", "") if isinstance(a, dict) else str(a) for a in paper.get("authors", [])]
    focus = paper.get("focus") or {}
    arxiv = is_arxiv_id(paper["id"])

    record: Dict[str, Any] = {
        "id": paper["id"],
        "t": paper.get("title", ""),
        "a": authors[:SITE_MAX_AUTHORS],
        "c": paper.get("categories", []),
        "d": paper.get("published_date", ""),
        "g": paper.get("tags", []),
        "u": paper.get("abs_link") or (f"https://arxiv.org/abs/{paper['id']}" if arxiv else ""),
        "p": paper.get("pdf_link", f"https://arxiv.org/pdf/{paper['id']}" if arxiv else ""),
        "ar": int(arxiv),
        "fo": {
            "s": int(focus.get("score", 0) or 0),
            "f": 1 if focus.get("is_focus") else 0,
            "p": focus.get("primary_topic"),
            "t": focus.get("topics", []),
            "r": focus.get("reasons", []),
        },
    }
    if len(authors) > SITE_MAX_AUTHORS:
        record["an"] = len(authors)
    # Optional fields are omitted when empty to keep the first load small.
    if paper.get("keywords"):
        record["k"] = paper["keywords"]
    if paper.get("summary_zh"):
        record["z"] = paper["summary_zh"]
    if paper.get("affiliations"):
        record["f"] = paper["affiliations"]
    record.update(_v2_fields(paper))
    return record, None


def _v2_fields(paper: Dict[str, Any]) -> Dict[str, Any]:
    """List-level fields from the S3 v2 enrichment and P2; empty ones are left out."""
    out: Dict[str, Any] = {}
    relevance = paper.get("relevance")
    if isinstance(relevance, int) and not isinstance(relevance, bool):
        out["r"] = relevance
    if paper.get("paper_type"):
        out["pt"] = paper["paper_type"]
    for key, field in (("tt", "task_types"), ("fd", "finance_domains"), ("m", "methods")):
        if paper.get(field):
            out[key] = list(paper[field])
    markets = [m for m in paper.get("data_market") or [] if m != "none"]
    if markets:
        out["dm"] = markets
    if paper.get("tldr_zh"):
        out["tl"] = paper["tldr_zh"]
    keywords = [
        [k.get("id", ""), k.get("zh") or k.get("en") or k.get("raw", ""), "f" if k.get("kind") == "finance" else "t"]
        for k in paper.get("keywords_norm") or []
        if isinstance(k, dict) and (k.get("zh") or k.get("en") or k.get("raw"))
    ]
    if keywords:
        out["kn"] = keywords
    venue = paper.get("venue")
    if isinstance(venue, dict) and venue.get("name"):
        out["v"] = {key: venue[field] for key, field in (("n", "name"), ("k", "kind"), ("s", "status"), ("y", "year")) if venue.get(field)}
        if venue.get("source") == "venue_list":
            out["v"]["o"] = 1
            if venue.get("text"):
                out["v"]["t"] = venue["text"]
    elif paper.get("venue_mention"):
        out["vm"] = str(paper["venue_mention"])[:120]
    if paper.get("discipline") and paper["discipline"] != "unknown":
        out["ds"] = paper["discipline"]
    if (paper.get("reproducibility") or {}).get("code") is True:
        out["cd"] = 1
    return out


def paper_detail(paper: Dict[str, Any], refs: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """What the detail drawer needs beyond the list record (see DETAIL_SCHEMA)."""
    out: Dict[str, Any] = {}
    points = paper.get("points_zh")
    if isinstance(points, dict) and any(points.values()):
        out["pz"] = {key: points.get(key, "") for key in ("problem", "method", "result", "limitation")}
    if paper.get("relevance_reason_zh"):
        out["rr"] = paper["relevance_reason_zh"]
    institutions = [
        {key: inst[field] for key, field in (("n", "name"), ("c", "country"), ("t", "type")) if inst.get(field)}
        for inst in paper.get("institutions") or []
        if isinstance(inst, dict) and inst.get("name")
    ]
    if refs is not None:
        institutions = [{"id": i["id"], "n": i["name"], "page": i["page"], "c": i["country"], "t": i["type"]}
                        for i in refs.get("institutions", [])]
        out["au"] = [{"id": a["id"], "n": a["name"], "page": a["page"]} for a in refs.get("authors", [])]
    if institutions:
        out["ins"] = institutions
        links = paper.get("author_affiliations") or []
        if any(links):
            out["aa"] = [list(item or []) for item in links]
    return out


def _chunk(items: Iterable[Any], max_bytes: int, overhead: int = 64) -> List[List[Any]]:
    chunks: List[List[Any]] = [[]]
    size = overhead
    for item in items:
        item_size = len(_dumps(item)) + 1
        if chunks[-1] and size + item_size > max_bytes:
            chunks.append([])
            size = overhead
        chunks[-1].append(item)
        size += item_size
    return [chunk for chunk in chunks if chunk]


def _write(path: Path, payload: bytes, max_bytes: int) -> Dict[str, Any]:
    if len(payload) > max_bytes:
        raise RuntimeError(f"{path} would be {len(payload)} bytes (> {max_bytes})")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(payload)
    return {"file": path.relative_to(SITE_DATA_DIR).as_posix(), "bytes": len(payload)}


def _quantize(matrix):
    """Per-row symmetric int8 quantization: v ≈ q * scale."""
    import numpy as np

    peaks = np.abs(matrix).max(axis=1) if matrix.size else np.zeros((0,), dtype=np.float32)
    scales = np.where(peaks > 0, peaks / 127.0, 1.0).astype(np.float32)
    quantized = np.clip(np.rint(matrix / scales[:, None]), -127, 127).astype(np.int8)
    return quantized, scales


class SlimCache:
    """slim_paper() results and their serialized sizes, computed once per paper."""

    # `,"dc":N` points at the details chunk.
    DETAIL_FIELD_BYTES = 8

    def __init__(self) -> None:
        self._items: Dict[str, Tuple[Dict[str, Any], Optional[str], int]] = {}

    def get(self, paper: Dict[str, Any]) -> Tuple[Dict[str, Any], Optional[str]]:
        record, full, _ = self._entry(paper)
        return dict(record), full

    def size(self, paper: Dict[str, Any]) -> int:
        return self._entry(paper)[2]

    def _entry(self, paper: Dict[str, Any]):
        paper_id = paper["id"]
        if paper_id not in self._items:
            record, full = slim_paper(paper)
            size = len(_dumps(record)) + 1 + self.DETAIL_FIELD_BYTES
            self._items[paper_id] = (record, full, size)
        return self._items[paper_id]


def estimate_first_load(papers: List[Dict[str, Any]], cache: SlimCache, max_bytes: int) -> int:
    """Bytes of the papers-N.json chunks for this group, without writing anything."""
    sizes = [cache.size(p) for p in papers]
    chunks = max(1, -(-sum(sizes) // max(1, max_bytes - 64)))
    return sum(sizes) + chunks * len(_dumps({"papers": []}))


def build_group(
    name: str,
    papers: List[Dict[str, Any]],
    vectors_by_id: Dict[str, int],
    matrix,
    max_bytes: int,
    cache: Optional[SlimCache] = None,
    paper_refs: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Write papers/details/vectors chunks for one group (recent or a month)."""
    cache = cache or SlimCache()
    slim_and_full = [cache.get(p) for p in papers]

    # Detail chunks (key points, institutions per author), loaded when a paper is opened.
    details = [(p["id"], detail) for p in papers for detail in [paper_detail(p, (paper_refs or {}).get(p["id"]))] if detail]
    detail_of: Dict[str, int] = {}
    detail_files = []
    for index, chunk in enumerate(_chunk(details, max_bytes)):
        for paper_id, _ in chunk:
            detail_of[paper_id] = index
        detail_files.append(_write(SITE_DATA_DIR / name / f"details-{index}.json", _dumps(dict(chunk)), max_bytes))

    records = []
    for record, _ in slim_and_full:
        if record["id"] in detail_of:
            record["dc"] = detail_of[record["id"]]
        records.append(record)
    paper_files = [
        _write(SITE_DATA_DIR / name / f"papers-{index}.json", _dumps({"papers": chunk}), max_bytes)
        for index, chunk in enumerate(_chunk(records, max_bytes))
    ]

    vector_files = []
    rows = [(p["id"], vectors_by_id[p["id"]]) for p in papers if p["id"] in vectors_by_id]
    if rows and matrix.size:
        dim = matrix.shape[1]
        per_chunk = max(1, (max_bytes - 1024) // dim)
        for index in range(0, len(rows), per_chunk):
            part = rows[index : index + per_chunk]
            quantized, scales = _quantize(matrix[[row for _, row in part]])
            chunk_index = index // per_chunk
            bin_info = _write(SITE_DATA_DIR / name / f"vectors-{chunk_index}.i8", quantized.tobytes(), max_bytes)
            ids_info = _write(
                SITE_DATA_DIR / name / f"vectors-{chunk_index}.json",
                _dumps({"ids": [pid for pid, _ in part], "scales": [round(float(s), 7) for s in scales]}),
                max_bytes,
            )
            vector_files.append({"bin": bin_info, "index": ids_info, "rows": len(part)})

    return {
        "count": len(papers),
        "papers": paper_files,
        "details": detail_files,
        "vectors": vector_files,
        "first_load_bytes": sum(f["bytes"] for f in paper_files),
    }


def _round_vector(values: List[float]) -> List[float]:
    return [round(float(v), 5) for v in values]


def site_taxonomy() -> Dict[str, Any]:
    """Chinese names for every classification id, from vocab/taxonomy.yaml: the site
    reads this one file instead of keeping its own copy of the labels."""
    tax = taxonomy()
    out: Dict[str, Any] = {
        key: [{"id": item["id"], "zh": item["zh"]} for item in tax[key]]
        for key in ("paper_types", "task_types", "finance_domains", "methods", "data_markets")
    }
    out["relevance"] = {str(score): value["zh"] for score, value in tax["relevance"].items()}
    out["version"] = ENRICH_VERSION
    return out


def build(today: Optional[date] = None) -> Dict[str, Any]:
    payload = json.loads(PAPERS_FILE.read_text(encoding="utf-8"))
    history = [p for p in payload.get("papers", []) if p.get("id")]
    papers = [p for p in history if site_visible(p)]
    logger.info(
        "Site shows %s of %s papers (relevance >= %s%s, not withdrawn); the rest stay in the dataset",
        len(papers), len(history), SITE_MIN_RELEVANCE, ", AI/ML method" if SITE_REQUIRE_AI_METHOD else "",
    )
    papers.sort(
        key=lambda p: (p.get("published_date", ""), (p.get("focus") or {}).get("score", 0), p.get("id", "")),
        reverse=True,
    )
    meta, matrix = load_local_embeddings()
    vectors_by_id = {paper_id: row for row, paper_id in enumerate(meta.get("ids", []))}

    latest = max((p.get("published_date", "") for p in papers), default="")
    anchor = today or (date.fromisoformat(latest) if latest else datetime.now(timezone.utc).date())

    if SITE_DATA_DIR.exists():
        shutil.rmtree(SITE_DATA_DIR)
    SITE_DATA_DIR.mkdir(parents=True)

    # Resolve identities once for both the leaderboards and paper drawers.
    paper_refs: Dict[str, Any] = {}
    agg_info = trends.build(papers, SITE_DATA_DIR / "agg")
    agg_info["leaders"] = leaders.build(papers, SITE_DATA_DIR / "agg", paper_refs=paper_refs)

    # Pick the window from size estimates first, then write the group once.
    cache = SlimCache()
    days = SITE_RECENT_DAYS
    while True:
        cutoff = (anchor - timedelta(days=days - 1)).isoformat()
        recent = [p for p in papers if p.get("published_date", "") >= cutoff]
        estimate = estimate_first_load(recent, cache, SITE_MAX_FILE_BYTES)
        if estimate <= SITE_FIRST_LOAD_BUDGET - 200_000 or days <= SITE_MIN_RECENT_DAYS:
            break
        logger.warning(
            "Recent window of %s days needs ~%.2f MB on first load; shrinking by a week",
            days,
            estimate / 1e6,
        )
        days = max(SITE_MIN_RECENT_DAYS, days - 7)
    recent_info = build_group("recent", recent, vectors_by_id, matrix, SITE_MAX_FILE_BYTES, cache, paper_refs)
    logger.info(
        "Recent first load: estimated %.3f MB, written %.3f MB",
        estimate / 1e6,
        recent_info["first_load_bytes"] / 1e6,
    )

    by_month: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    undated = 0
    for paper in papers:
        published = paper.get("published_date", "")
        if published >= cutoff:
            continue
        if not published:
            undated += 1
            continue
        by_month[published[:7]].append(paper)

    archive = []
    for month in sorted(by_month, reverse=True):
        info = build_group(f"archive/{month}", by_month[month], vectors_by_id, matrix, SITE_MAX_FILE_BYTES, cache, paper_refs)
        info.pop("first_load_bytes")
        archive.append({"month": month, **info})

    # Trends, keywords and the overview count only the papers the site shows.
    site_stats = build_stats(papers)
    site_stats["summary"]["history_papers"] = len(history)
    site_stats["summary"]["min_relevance"] = SITE_MIN_RELEVANCE
    site_stats["summary"]["core_papers"] = sum(1 for p in papers if p.get("relevance") == 3)
    stats_info = _write(SITE_DATA_DIR / "stats.json", _dumps(site_stats), SITE_MAX_FILE_BYTES)
    taxonomy_info = _write(SITE_DATA_DIR / "taxonomy.json", _dumps(site_taxonomy()), SITE_MAX_FILE_BYTES)

    paper_index = {p["id"]: "recent" for p in recent}
    for month, group in by_month.items():
        paper_index.update({p["id"]: f"archive/{month}" for p in group})
    index_info = _write(SITE_DATA_DIR / "paper-index.json", _dumps(paper_index), SITE_MAX_FILE_BYTES)

    manifest = {
        "version": 3,
        "paper_index": index_info,
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "source_last_updated": payload.get("last_updated"),
        "total_papers": len(papers),
        "history_papers": len(history),
        "min_relevance": SITE_MIN_RELEVANCE,
        "require_ai_method": SITE_REQUIRE_AI_METHOD,
        "undated_papers_skipped": undated,
        "latest_published_date": latest,
        "embedding": {
            "model": meta.get("model"),
            "dimension": int(matrix.shape[1]) if matrix.size else 0,
            "quantization": "int8, per-row scale: vector ≈ int8 * scale",
            "theme_queries": meta.get("theme_queries", {}),
            "theme_vectors": {k: _round_vector(v) for k, v in (meta.get("theme_vectors") or {}).items()},
        },
        "recent": {"since": cutoff, "until": anchor.isoformat(), "days": days, **recent_info},
        "archive": archive,
        "stats": stats_info,
        "agg": agg_info,
        "taxonomy": taxonomy_info,
        "detail_schema": DETAIL_SCHEMA,
        "schema": SCHEMA,
        "limits": {"max_file_bytes": SITE_MAX_FILE_BYTES, "first_load_budget": SITE_FIRST_LOAD_BUDGET},
        "attribution": "Thank you to arXiv for use of its open access interoperability.",
    }
    manifest_bytes = _dumps(manifest)
    _write(SITE_DATA_DIR / "manifest.json", manifest_bytes, SITE_MAX_FILE_BYTES)

    first_load = recent_info["first_load_bytes"] + len(manifest_bytes)
    largest = max((p.stat().st_size, p) for p in SITE_DATA_DIR.rglob("*") if p.is_file())
    logger.info(
        "Site data: %s recent papers (%s days since %s), %s archive months, first load %.2f MB, largest file %.2f MB (%s)",
        recent_info["count"],
        days,
        cutoff,
        len(archive),
        first_load / 1e6,
        largest[0] / 1e6,
        largest[1].relative_to(SITE_DATA_DIR),
    )
    if first_load > SITE_FIRST_LOAD_BUDGET:
        logger.warning("First load %.2f MB exceeds the %.2f MB budget", first_load / 1e6, SITE_FIRST_LOAD_BUDGET / 1e6)
    return manifest


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    build()
