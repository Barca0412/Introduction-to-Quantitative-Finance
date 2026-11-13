"""Build the light-weight Radar data served by the VitePress site.

Reads the full history from ``data/`` (papers.json, stats.json, embeddings.f32)
and writes ``docs/public/arxiv-data/``:

    manifest.json                    what exists, sizes, theme vectors, schema
    stats.json                       trend statistics (Trends / overview pages)
    recent/papers-N.json             last ~90 days, slim records (first load)
    recent/abstracts-N.json          {id: full abstract}, loaded on demand
    recent/vectors-N.i8              int8 embeddings, row-major, loaded on demand
    recent/vectors-N.json            {"ids": [...], "scales": [...]} for that .i8
    archive/YYYY-MM/...              same four kinds for older months, on demand

Constraints (see config.py): every file <= SITE_MAX_FILE_BYTES and the Papers
page's first load (manifest + recent/papers-*) <= SITE_FIRST_LOAD_BUDGET. If the
budget is exceeded the recent window shrinks week by week (not below
SITE_MIN_RECENT_DAYS). Only metadata and abstracts are published; no full text
or figures.

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
    SITE_ABSTRACT_SNIPPET_CHARS,
    SITE_DATA_DIR,
    SITE_FIRST_LOAD_BUDGET,
    SITE_MAX_AUTHORS,
    SITE_MAX_FILE_BYTES,
    SITE_MIN_RECENT_DAYS,
    SITE_RECENT_DAYS,
    PAPERS_FILE,
    STATS_FILE,
)
from .data_store import load_local_embeddings

logger = logging.getLogger("arxiv_radar.build_site_data")

SCHEMA = {
    "id": "arXiv id",
    "t": "title",
    "a": f"author names (first {SITE_MAX_AUTHORS})",
    "an": "total author count, only when authors were truncated",
    "c": "arXiv categories",
    "d": "published date YYYY-MM-DD",
    "g": "tags",
    "k": "keywords",
    "z": "Chinese summary",
    "f": "affiliations",
    "s": "abstract (snippet when 'ac' is present)",
    "ac": "index of the abstracts-N.json chunk holding the full abstract",
    "fo": "focus: s=score, f=is_focus(0/1), p=primary topic, t=topics, r=reasons",
}


def _dumps(payload: Any) -> bytes:
    return json.dumps(payload, ensure_ascii=False, separators=(",", ":")).encode("utf-8")


def _snippet(text: str, limit: int) -> Tuple[str, bool]:
    text = (text or "").strip()
    # Short abstracts are kept whole: a chunk lookup would cost more than it saves.
    if len(text) <= limit + 40:
        return text, False
    cut = text[:limit]
    space = cut.rfind(" ")
    if space > limit * 0.6:
        cut = cut[:space]
    return cut.rstrip(" ,.;:") + "…", True


def slim_paper(paper: Dict[str, Any]) -> Tuple[Dict[str, Any], Optional[str]]:
    """Return (slim record, full abstract or None if the snippet is the whole text)."""
    authors = [a.get("name", "") if isinstance(a, dict) else str(a) for a in paper.get("authors", [])]
    focus = paper.get("focus") or {}
    snippet, truncated = _snippet(paper.get("abstract", ""), SITE_ABSTRACT_SNIPPET_CHARS)

    record: Dict[str, Any] = {
        "id": paper["id"],
        "t": paper.get("title", ""),
        "a": authors[:SITE_MAX_AUTHORS],
        "c": paper.get("categories", []),
        "d": paper.get("published_date", ""),
        "g": paper.get("tags", []),
        "s": snippet,
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
    return record, (paper.get("abstract", "").strip() if truncated else None)


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


def build_group(
    name: str,
    papers: List[Dict[str, Any]],
    vectors_by_id: Dict[str, int],
    matrix,
    max_bytes: int,
) -> Dict[str, Any]:
    """Write papers/abstracts/vectors chunks for one group (recent or a month)."""
    import numpy as np

    slim_and_full = [slim_paper(p) for p in papers]

    # Abstract chunks first, so each slim record can point at its chunk.
    full_abstracts = [(rec["id"], full) for rec, full in slim_and_full if full]
    abstract_chunks = _chunk(full_abstracts, max_bytes)
    chunk_of: Dict[str, int] = {}
    abstract_files = []
    for index, chunk in enumerate(abstract_chunks):
        for paper_id, _ in chunk:
            chunk_of[paper_id] = index
        abstract_files.append(_write(SITE_DATA_DIR / name / f"abstracts-{index}.json", _dumps(dict(chunk)), max_bytes))

    records = []
    for record, _ in slim_and_full:
        if record["id"] in chunk_of:
            record["ac"] = chunk_of[record["id"]]
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
        "abstracts": abstract_files,
        "vectors": vector_files,
        "first_load_bytes": sum(f["bytes"] for f in paper_files),
    }


def _round_vector(values: List[float]) -> List[float]:
    return [round(float(v), 5) for v in values]


def build(today: Optional[date] = None) -> Dict[str, Any]:
    payload = json.loads(PAPERS_FILE.read_text(encoding="utf-8"))
    papers = [p for p in payload.get("papers", []) if p.get("id")]
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

    # Shrink the recent window until the first load fits the budget.
    days = SITE_RECENT_DAYS
    while True:
        cutoff = (anchor - timedelta(days=days - 1)).isoformat()
        recent = [p for p in papers if p.get("published_date", "") >= cutoff]
        recent_info = build_group("recent", recent, vectors_by_id, matrix, SITE_MAX_FILE_BYTES)
        if recent_info["first_load_bytes"] <= SITE_FIRST_LOAD_BUDGET - 200_000 or days <= SITE_MIN_RECENT_DAYS:
            break
        logger.warning(
            "Recent window of %s days needs %.2f MB on first load; shrinking by a week",
            days,
            recent_info["first_load_bytes"] / 1e6,
        )
        shutil.rmtree(SITE_DATA_DIR / "recent")
        days -= 7

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
        info = build_group(f"archive/{month}", by_month[month], vectors_by_id, matrix, SITE_MAX_FILE_BYTES)
        info.pop("first_load_bytes")
        archive.append({"month": month, **info})

    stats_info = None
    if STATS_FILE.exists():
        stats_info = _write(SITE_DATA_DIR / "stats.json", _dumps(json.loads(STATS_FILE.read_text(encoding="utf-8"))), SITE_MAX_FILE_BYTES)

    manifest = {
        "version": 2,
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "source_last_updated": payload.get("last_updated"),
        "total_papers": len(papers),
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
