"""Full-history storage for the arXiv Radar, kept outside git.

The daily job no longer commits data. Instead:

* ``restore``  pulls the full history into ``data/`` before fetching new papers
  (local files -> Hugging Face dataset -> GitHub Release -> legacy git branch).
* ``export``   writes the merged history as Parquet + a dataset card into
  ``data/export/`` and refuses to run if the history would shrink.
* ``push-hf``  uploads ``data/export/`` to the Hugging Face dataset named by
  ``HF_DATASET_REPO`` using ``HF_TOKEN``. Empty repo name = skip.

The GitHub Release mirror is uploaded by the workflow with ``gh release upload``.

Usage::

    python -m scripts.arxiv_radar.data_store restore
    python -m scripts.arxiv_radar.data_store export
    python -m scripts.arxiv_radar.data_store push-hf
"""

from __future__ import annotations

import argparse
import hashlib
import json
import logging
import os
import shutil
import subprocess
import sys
import tempfile
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple

from .config import (
    BASE_DIR,
    DATA_DIR,
    EMBEDDINGS_BIN,
    EMBEDDINGS_META,
    EXPORT_DIR,
    GITHUB_REPOSITORY,
    HF_DATASET_REPO,
    HF_TOKEN,
    PAPERS_FILE,
    RADAR_LEGACY_BRANCH,
    RADAR_LEGACY_GIT_REF,
    RADAR_RELEASE_BASE_URL,
    RADAR_RELEASE_TAG,
    STATS_FILE,
)
from .storage import write_atomically

logger = logging.getLogger("arxiv_radar.data_store")

PAPERS_PARQUET = "papers.parquet"
EMBEDDINGS_PARQUET = "embeddings.parquet"
EXPORT_INFO = "export_info.json"
RESTORE_RECORD = DATA_DIR / "restore_record.json"
DATASET_CARD_TEMPLATE = Path(__file__).with_name("dataset_card.md")
EMBEDDING_METADATA_KEY = b"radar_embeddings"


# --------------------------------------------------------------------------
# Parquet schema
# --------------------------------------------------------------------------

def _papers_schema():
    import pyarrow as pa

    strings = pa.list_(pa.string())
    return pa.schema(
        [
            ("id", pa.string()),
            ("title", pa.string()),
            ("abstract", pa.string()),
            ("authors", pa.list_(pa.struct([("name", pa.string()), ("affiliation", pa.string())]))),
            ("categories", strings),
            ("published_date", pa.string()),
            ("pdf_link", pa.string()),
            ("abs_link", pa.string()),
            ("tags", strings),
            ("keywords", strings),
            ("summary_zh", pa.string()),
            ("affiliation", pa.string()),
            ("affiliations", strings),
            (
                "focus",
                pa.struct(
                    [
                        ("score", pa.int32()),
                        ("is_focus", pa.bool_()),
                        ("primary_topic", pa.string()),
                        ("topics", strings),
                        ("labels", strings),
                        ("matched_tags", strings),
                        ("matched_categories", strings),
                        ("reasons", strings),
                    ]
                ),
            ),
        ]
    )


def _clean_paper_for_parquet(paper: Dict[str, Any]) -> Dict[str, Any]:
    focus = paper.get("focus") or {}
    return {
        "id": paper.get("id", ""),
        "title": paper.get("title", ""),
        "abstract": paper.get("abstract", ""),
        "authors": [
            {"name": str(a.get("name", "")), "affiliation": str(a.get("affiliation", ""))}
            for a in paper.get("authors", [])
            if isinstance(a, dict)
        ],
        "categories": list(paper.get("categories", [])),
        "published_date": paper.get("published_date", ""),
        "pdf_link": paper.get("pdf_link", ""),
        "abs_link": paper.get("abs_link", ""),
        "tags": list(paper.get("tags", [])),
        "keywords": list(paper.get("keywords", [])),
        "summary_zh": paper.get("summary_zh", ""),
        "affiliation": paper.get("affiliation", ""),
        "affiliations": list(paper.get("affiliations", [])),
        "focus": {
            "score": int(focus.get("score", 0) or 0),
            "is_focus": bool(focus.get("is_focus", False)),
            "primary_topic": focus.get("primary_topic"),
            "topics": list(focus.get("topics", [])),
            "labels": list(focus.get("labels", [])),
            "matched_tags": list(focus.get("matched_tags", [])),
            "matched_categories": list(focus.get("matched_categories", [])),
            "reasons": list(focus.get("reasons", [])),
        },
    }


# --------------------------------------------------------------------------
# Local working files <-> in-memory structures
# --------------------------------------------------------------------------

def load_local_embeddings() -> Tuple[Dict[str, Any], Any]:
    """Return (meta, float32 matrix) from data/embeddings.*; empty if absent."""
    import numpy as np

    if not (EMBEDDINGS_BIN.exists() and EMBEDDINGS_META.exists()):
        return {}, np.zeros((0, 0), dtype=np.float32)
    meta = json.loads(EMBEDDINGS_META.read_text(encoding="utf-8"))
    dim = int(meta.get("dimension") or 0)
    matrix = np.fromfile(EMBEDDINGS_BIN, dtype="<f4")
    if dim:
        matrix = matrix.reshape(-1, dim)
    if len(matrix) != len(meta.get("ids", [])):
        raise RuntimeError(
            f"Embedding matrix has {len(matrix)} rows but meta lists {len(meta.get('ids', []))} ids"
        )
    return meta, matrix


def save_local_embeddings(meta: Dict[str, Any], matrix) -> None:
    import numpy as np

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    matrix = np.ascontiguousarray(matrix, dtype="<f4")
    tmp = EMBEDDINGS_BIN.with_suffix(".f32.tmp")
    matrix.tofile(tmp)
    tmp.replace(EMBEDDINGS_BIN)
    meta = dict(meta)
    meta["dimension"] = int(matrix.shape[1]) if matrix.ndim == 2 and matrix.size else int(meta.get("dimension") or 0)
    write_atomically(EMBEDDINGS_META, meta)


def _write_papers_json(papers: List[Dict[str, Any]], last_updated: Optional[str] = None) -> None:
    write_atomically(
        PAPERS_FILE,
        {
            "last_updated": last_updated or datetime.now(timezone.utc).replace(tzinfo=None).isoformat(),
            "total_count": len(papers),
            "papers": papers,
        },
    )


# --------------------------------------------------------------------------
# Restore sources
# --------------------------------------------------------------------------
#
# Every source is turned into a Candidate first (cheap: only export_info.json is
# downloaded), then the newest one is imported. "Newest" = latest
# papers_last_updated, ties broken by paper count. This way a stale Hugging Face
# copy (e.g. its upload failed yesterday) never wins over a fresher Release copy.


@dataclass
class Candidate:
    name: str
    papers: int
    updated: str  # naive-UTC ISO timestamp, "" when unknown
    load: Callable[[], int] = field(repr=False)


def _normalize_timestamp(value: Any) -> str:
    if not value:
        return ""
    try:
        parsed = datetime.fromisoformat(str(value))
    except ValueError:
        return ""
    if parsed.tzinfo is not None:
        parsed = parsed.astimezone(timezone.utc).replace(tzinfo=None)
    return parsed.isoformat()


def _import_parquet_pair(
    papers_path: Path,
    embeddings_path: Optional[Path],
    stats_path: Optional[Path] = None,
    last_updated: Optional[str] = None,
) -> int:
    import numpy as np
    import pyarrow.parquet as pq

    papers = pq.read_table(papers_path).to_pylist()
    _write_papers_json(papers, last_updated or None)

    if stats_path and stats_path.exists():
        shutil.copy2(stats_path, STATS_FILE)

    if embeddings_path and embeddings_path.exists():
        table = pq.read_table(embeddings_path)
        raw_meta = (table.schema.metadata or {}).get(EMBEDDING_METADATA_KEY)
        meta = json.loads(raw_meta.decode("utf-8")) if raw_meta else {}
        ids = table.column("id").to_pylist()
        hashes = table.column("text_hash").to_pylist()
        vectors = table.column("vector").to_pylist()
        matrix = np.asarray(vectors, dtype=np.float32) if vectors else np.zeros((0, 0), dtype=np.float32)
        meta.update({"ids": ids, "text_hashes": hashes})
        save_local_embeddings(meta, matrix)
    return len(papers)


def _hf_fetch(filename: str, workdir: Path) -> Optional[Path]:
    """Download one file of the Hugging Face dataset, or None."""
    if not HF_DATASET_REPO:
        return None
    try:
        from huggingface_hub import hf_hub_download

        return Path(
            hf_hub_download(HF_DATASET_REPO, filename, repo_type="dataset", token=HF_TOKEN or None, local_dir=workdir)
        )
    except Exception as exc:
        logger.info("Hugging Face %s: %s not available (%s)", HF_DATASET_REPO, filename, type(exc).__name__)
        return None


def _download(url: str, target: Path) -> bool:
    request = urllib.request.Request(url, headers={"User-Agent": "arxiv-radar-restore"})
    try:
        with urllib.request.urlopen(request, timeout=120) as response, open(target, "wb") as handle:
            shutil.copyfileobj(response, handle)
        return True
    except urllib.error.HTTPError as exc:
        logger.info("GET %s -> HTTP %s", url, exc.code)
    except urllib.error.URLError as exc:
        logger.warning("GET %s failed: %s", url, exc.reason)
    if target.exists():
        target.unlink()
    return False


def _release_fetch(filename: str, workdir: Path) -> Optional[Path]:
    """Download one asset of the GitHub Release mirror, or None."""
    base = RADAR_RELEASE_BASE_URL or (
        f"https://github.com/{GITHUB_REPOSITORY}/releases/download/{RADAR_RELEASE_TAG}"
        if GITHUB_REPOSITORY and RADAR_RELEASE_TAG
        else ""
    )
    if not base:
        return None
    target = workdir / filename
    url = f"{base}/{filename}"
    return target if _download(url, target) else None


def _remote_candidate(name: str, fetch: Callable[[str, Path], Optional[Path]], workdir: Path) -> Optional[Candidate]:
    sub = workdir / name
    sub.mkdir(parents=True, exist_ok=True)
    info_path = fetch(EXPORT_INFO, sub)
    papers_path: Optional[Path] = None
    if info_path:
        info = json.loads(info_path.read_text(encoding="utf-8"))
        papers = int(info.get("papers") or 0)
        updated = _normalize_timestamp(info.get("papers_last_updated") or info.get("generated_at"))
    else:
        papers_path = fetch(PAPERS_PARQUET, sub)
        if not papers_path:
            logger.info("%s: no data", name)
            return None
        import pyarrow.parquet as pq

        papers = pq.read_metadata(papers_path).num_rows
        updated = ""
    if papers <= 0:
        logger.info("%s: dataset is empty", name)
        return None

    def load() -> int:
        path = papers_path or fetch(PAPERS_PARQUET, sub)
        if not path:
            raise RuntimeError(f"{name}: export_info.json exists but {PAPERS_PARQUET} could not be downloaded")
        return _import_parquet_pair(
            path,
            fetch(EMBEDDINGS_PARQUET, sub),
            fetch("stats.json", sub),
            updated,
        )

    logger.info("%s: %s papers, updated %s", name, papers, updated or "unknown")
    return Candidate(name, papers, updated, load)


def _local_candidate() -> Optional[Candidate]:
    if not PAPERS_FILE.exists():
        return None
    payload = json.loads(PAPERS_FILE.read_text(encoding="utf-8"))
    papers = len(payload.get("papers", []))
    if papers <= 0:
        return None
    updated = _normalize_timestamp(payload.get("last_updated"))
    logger.info("local: %s papers, updated %s", papers, updated or "unknown")
    # Already in place: nothing to import.
    return Candidate("local", papers, updated, lambda: papers)


def _git(*args: str, stdout=subprocess.PIPE) -> subprocess.CompletedProcess:
    return subprocess.run(["git", *args], cwd=BASE_DIR, stdout=stdout, stderr=subprocess.PIPE)


def _git_show(ref_path: str, target: Path) -> bool:
    with open(target, "wb") as handle:
        result = _git("show", ref_path, stdout=handle)
    if result.returncode != 0:
        logger.info("git show %s failed: %s", ref_path, result.stderr.decode(errors="ignore").strip())
        return False
    return True


def _ensure_legacy_ref() -> bool:
    """Make RADAR_LEGACY_GIT_REF available, fetching the legacy branch if needed."""
    if not RADAR_LEGACY_GIT_REF:
        return False
    if _git("rev-parse", "--verify", "--quiet", RADAR_LEGACY_GIT_REF).returncode == 0:
        return True
    if not RADAR_LEGACY_BRANCH or not RADAR_LEGACY_GIT_REF.startswith("refs/"):
        return False
    logger.info("Fetching legacy branch %s into %s", RADAR_LEGACY_BRANCH, RADAR_LEGACY_GIT_REF)
    result = _git("fetch", "--no-tags", "--depth=1", "origin", f"+{RADAR_LEGACY_BRANCH}:{RADAR_LEGACY_GIT_REF}")
    if result.returncode != 0:
        logger.info("Legacy branch not available: %s", result.stderr.decode(errors="ignore").strip())
        return False
    return True


def import_legacy_json(
    papers_json: Path,
    embeddings_json: Optional[Path],
    stats_json: Optional[Path] = None,
) -> int:
    """Convert the old in-git JSON files (indent=2, float lists) to the new layout."""
    import numpy as np

    payload = json.loads(papers_json.read_text(encoding="utf-8"))
    papers = payload.get("papers", [])
    _write_papers_json(papers, payload.get("last_updated"))

    if stats_json and stats_json.exists():
        write_atomically(STATS_FILE, json.loads(stats_json.read_text(encoding="utf-8")))

    if embeddings_json and embeddings_json.exists():
        legacy = json.loads(embeddings_json.read_text(encoding="utf-8"))
        rows = [row for row in legacy.get("papers", []) if row.get("vector")]
        matrix = np.asarray([row["vector"] for row in rows], dtype=np.float32)
        meta = {
            "model": legacy.get("model"),
            "generated_at": legacy.get("generated_at"),
            "theme_queries": legacy.get("theme_queries", {}),
            "theme_vectors": legacy.get("theme_vectors", {}),
            "ids": [row["id"] for row in rows],
            # Empty hash = built with the old text recipe; generate_embeddings.mjs
            # reuses these vectors and refreshes them gradually.
            "text_hashes": [""] * len(rows),
        }
        save_local_embeddings(meta, matrix)
    return len(papers)


def _legacy_candidate(workdir: Path) -> Optional[Candidate]:
    if not _ensure_legacy_ref():
        return None
    papers_path = workdir / "legacy_papers.json"
    if not _git_show(f"{RADAR_LEGACY_GIT_REF}:data/papers.json", papers_path):
        return None
    payload = json.loads(papers_path.read_text(encoding="utf-8"))
    papers = len(payload.get("papers", []))
    if papers <= 0:
        return None

    def load() -> int:
        emb_path = workdir / "legacy_embeddings_index.json"
        stats_path = workdir / "legacy_stats.json"
        return import_legacy_json(
            papers_path,
            emb_path if _git_show(f"{RADAR_LEGACY_GIT_REF}:data/embeddings_index.json", emb_path) else None,
            stats_path if _git_show(f"{RADAR_LEGACY_GIT_REF}:data/stats.json", stats_path) else None,
        )

    updated = _normalize_timestamp(payload.get("last_updated"))
    logger.info("legacy-git: %s papers, updated %s", papers, updated or "unknown")
    return Candidate("legacy-git", papers, updated, load)


def _ensure_stats() -> None:
    """The site needs stats.json; recompute it when the source did not carry one."""
    if STATS_FILE.exists():
        return
    from .compute_stats import compute_and_save_stats

    papers = json.loads(PAPERS_FILE.read_text(encoding="utf-8")).get("papers", [])
    logger.info("No stats.json in the restored data; recomputing from %s papers", len(papers))
    compute_and_save_stats(papers)


def restore(source: str = "auto") -> Dict[str, Any]:
    """Make sure data/ holds the newest full history (and its stats) before a run."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    fetchers = {"hf": _hf_fetch, "release": _release_fetch}

    with tempfile.TemporaryDirectory() as tmp:
        workdir = Path(tmp)
        candidates: List[Candidate] = []
        if source in ("auto", "local"):
            local = _local_candidate()
            if local:
                candidates.append(local)
        for name in ("hf", "release"):
            if source in ("auto", name):
                candidate = _remote_candidate(name, fetchers[name], workdir)
                if candidate:
                    candidates.append(candidate)
        # The legacy branch is only a bootstrap: used when nothing else has data.
        if source == "legacy-git" or (source == "auto" and not candidates):
            legacy = _legacy_candidate(workdir)
            if legacy:
                candidates.append(legacy)

        if candidates:
            chosen = max(candidates, key=lambda c: (c.updated, c.papers))
            if chosen.name != "local":
                # Drop stats that belong to a different snapshot.
                STATS_FILE.unlink(missing_ok=True)
            count = chosen.load()
            record = {
                "source": chosen.name,
                "papers": count,
                "updated": chosen.updated,
                "considered": [{"source": c.name, "papers": c.papers, "updated": c.updated} for c in candidates],
            }
        elif os.getenv("RADAR_ALLOW_EMPTY_HISTORY") == "1":
            logger.warning("No history found anywhere; starting from an empty dataset (RADAR_ALLOW_EMPTY_HISTORY=1)")
            _write_papers_json([])
            STATS_FILE.unlink(missing_ok=True)
            record = {"source": "empty", "papers": 0, "considered": []}
        else:
            raise SystemExit(
                "Could not restore Radar history from local files, Hugging Face, GitHub Release "
                "or the legacy git branch. Refusing to continue, because publishing now would "
                "overwrite the full history with a 7-day window. Set RADAR_ALLOW_EMPTY_HISTORY=1 "
                "only if you really want to start over."
            )

    _ensure_stats()
    record["restored_at"] = datetime.now(timezone.utc).isoformat()
    write_atomically(RESTORE_RECORD, record)
    logger.info("Restored %s papers from %s", record["papers"], record["source"])
    return record


# --------------------------------------------------------------------------
# Export + push
# --------------------------------------------------------------------------

def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _render_dataset_card(info: Dict[str, Any]) -> str:
    template = DATASET_CARD_TEMPLATE.read_text(encoding="utf-8")
    for key, value in info.items():
        template = template.replace("{{" + key + "}}", str(value))
    return template


def export() -> Dict[str, Any]:
    import pyarrow as pa
    import pyarrow.parquet as pq

    payload = json.loads(PAPERS_FILE.read_text(encoding="utf-8"))
    papers = payload.get("papers", [])

    if RESTORE_RECORD.exists():
        restored = json.loads(RESTORE_RECORD.read_text(encoding="utf-8")).get("papers", 0)
        if len(papers) < restored:
            raise SystemExit(
                f"History shrank from {restored} to {len(papers)} papers; refusing to export."
            )

    EXPORT_DIR.mkdir(parents=True, exist_ok=True)
    papers_table = pa.Table.from_pylist([_clean_paper_for_parquet(p) for p in papers], schema=_papers_schema())
    pq.write_table(papers_table, EXPORT_DIR / PAPERS_PARQUET, compression="zstd")

    meta, matrix = load_local_embeddings()
    if meta.get("ids"):
        dim = int(matrix.shape[1])
        emb_meta = {k: v for k, v in meta.items() if k not in ("ids", "text_hashes")}
        schema = pa.schema(
            [("id", pa.string()), ("text_hash", pa.string()), ("vector", pa.list_(pa.float32(), dim))],
            metadata={EMBEDDING_METADATA_KEY: json.dumps(emb_meta, ensure_ascii=False).encode("utf-8")},
        )
        flat = pa.array(matrix.reshape(-1), type=pa.float32())
        table = pa.Table.from_arrays(
            [
                pa.array(meta["ids"], type=pa.string()),
                pa.array(meta.get("text_hashes") or [""] * len(meta["ids"]), type=pa.string()),
                pa.FixedSizeListArray.from_arrays(flat, dim),
            ],
            schema=schema,
        )
        pq.write_table(table, EXPORT_DIR / EMBEDDINGS_PARQUET, compression="zstd")

    if STATS_FILE.exists():
        shutil.copy2(STATS_FILE, EXPORT_DIR / "stats.json")

    dates = sorted(p.get("published_date", "") for p in papers if p.get("published_date"))
    info = {
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        # restore() compares this across Hugging Face / Release to pick the newest copy.
        "papers_last_updated": payload.get("last_updated"),
        "papers": len(papers),
        "embedded_papers": len(meta.get("ids", [])),
        "embedding_model": meta.get("model") or "Xenova/all-MiniLM-L6-v2",
        "first_date": dates[0] if dates else "N/A",
        "last_date": dates[-1] if dates else "N/A",
        "files": {},
    }
    for name in (PAPERS_PARQUET, EMBEDDINGS_PARQUET, "stats.json"):
        path = EXPORT_DIR / name
        if path.exists():
            info["files"][name] = {"bytes": path.stat().st_size, "sha256": _sha256(path)}

    (EXPORT_DIR / "README.md").write_text(_render_dataset_card(info), encoding="utf-8")
    write_atomically(EXPORT_DIR / EXPORT_INFO, info)
    logger.info("Exported %s papers to %s", len(papers), EXPORT_DIR)
    return info


def push_hf() -> None:
    if not HF_DATASET_REPO:
        logger.info("HF_DATASET_REPO is empty; skipping Hugging Face upload")
        return
    if not HF_TOKEN:
        raise SystemExit("HF_DATASET_REPO is set but HF_TOKEN is missing")
    if not (EXPORT_DIR / PAPERS_PARQUET).exists():
        raise SystemExit("Nothing to upload; run `data_store export` first")

    from huggingface_hub import HfApi

    api = HfApi(token=HF_TOKEN)
    api.upload_folder(
        repo_id=HF_DATASET_REPO,
        repo_type="dataset",
        folder_path=str(EXPORT_DIR),
        commit_message=f"Radar data update {datetime.now(timezone.utc).date().isoformat()}",
    )
    logger.info("Uploaded %s to https://huggingface.co/datasets/%s", EXPORT_DIR, HF_DATASET_REPO)


def main(argv: Optional[List[str]] = None) -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)
    restore_parser = sub.add_parser("restore", help="pull full history into data/")
    restore_parser.add_argument("--source", default="auto", choices=["auto", "local", "hf", "release", "legacy-git"])
    sub.add_parser("export", help="write data/export/*.parquet + dataset card")
    sub.add_parser("push-hf", help="upload data/export/ to the Hugging Face dataset")
    legacy = sub.add_parser("import-legacy", help="convert old papers.json / embeddings_index.json")
    legacy.add_argument("papers_json", type=Path)
    legacy.add_argument("embeddings_json", type=Path, nargs="?")
    legacy.add_argument("stats_json", type=Path, nargs="?")
    args = parser.parse_args(argv)

    if args.command == "restore":
        restore(args.source)
    elif args.command == "export":
        export()
    elif args.command == "push-hf":
        push_hf()
    elif args.command == "import-legacy":
        count = import_legacy_json(args.papers_json, args.embeddings_json, args.stats_json)
        write_atomically(RESTORE_RECORD, {"source": "import-legacy", "papers": count})
        logger.info("Imported %s legacy papers", count)


if __name__ == "__main__":
    main(sys.argv[1:])
