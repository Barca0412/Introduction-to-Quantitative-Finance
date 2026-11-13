"""Reproducible checks for Radar history restore and the site-only path.

Run from the repository root:

    python3 -m unittest scripts.arxiv_radar.tests.test_restore -v

No network: Hugging Face, the GitHub Release and git are replaced by local fakes.
Covers:
  1. a stale Hugging Face copy must lose to a newer Release copy (and vice versa),
     and an empty Hugging Face dataset must not block the Release;
  2. first run: Hugging Face configured but empty + no Release -> restore fetches
     the legacy branch by itself;
  3. stats.json is restored with the data (or recomputed), so a site-only build
     publishes arxiv-data/stats.json.
"""

from __future__ import annotations

import contextlib
import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path
from typing import Dict, List, Optional
from unittest import mock

import numpy as np

from scripts.arxiv_radar import build_site_data, data_store, storage


def make_papers(count: int, latest_day: int = 10) -> List[Dict]:
    return [
        {
            "id": f"2611.{index:05d}",
            "title": f"Paper {index}",
            "abstract": "word " * (60 + index),
            "authors": [{"name": f"Author {index}", "affiliation": ""}],
            "categories": ["q-fin.PM"],
            "published_date": f"2026-11-{max(1, latest_day - index % 5):02d}",
            "tags": ["ai-finance"],
            "keywords": [],
            "summary_zh": "",
            "affiliation": "",
            "affiliations": [],
            "focus": {"score": 12, "is_focus": True, "primary_topic": "ai-finance", "topics": ["ai-finance"],
                      "labels": ["AI + Finance"], "matched_tags": ["ai-finance"], "matched_categories": [], "reasons": []},
        }
        for index in range(count)
    ]


STATS = {"last_updated": "2026-11-10T00:00:00", "tag_stats": {"_all": {}}, "keyword_stats": {"_all": {}},
         "summary": {"total_papers": 0, "latest_published_date": ""}}


class RadarSandbox:
    """Points every module-level path at a temporary directory."""

    def __init__(self, root: Path) -> None:
        self.root = root
        self.data = root / "data"
        self.site = root / "site" / "arxiv-data"
        self.data.mkdir(parents=True)

    @contextlib.contextmanager
    def patched(self):
        paths = {
            "DATA_DIR": self.data,
            "PAPERS_FILE": self.data / "papers.json",
            "STATS_FILE": self.data / "stats.json",
            "EMBEDDINGS_BIN": self.data / "embeddings.f32",
            "EMBEDDINGS_META": self.data / "embeddings.meta.json",
            "EXPORT_DIR": self.data / "export",
            "RESTORE_RECORD": self.data / "restore_record.json",
        }
        with contextlib.ExitStack() as stack:
            for name, value in paths.items():
                stack.enter_context(mock.patch.object(data_store, name, value))
            for name in ("PAPERS_FILE", "STATS_FILE"):
                stack.enter_context(mock.patch.object(storage, name, paths[name]))
                stack.enter_context(mock.patch.object(build_site_data, name, paths[name]))
            stack.enter_context(mock.patch.object(build_site_data, "SITE_DATA_DIR", self.site))
            yield

    def make_export(self, name: str, papers: List[Dict], last_updated: str, with_stats: bool = True) -> Path:
        """Produce a real `data_store.export()` snapshot in root/<name>/."""
        work = RadarSandbox(self.root / f"_work_{name}")
        with work.patched():
            data_store._write_papers_json(papers, last_updated)
            if with_stats:
                storage.write_atomically(work.data / "stats.json", {**STATS, "last_updated": last_updated})
            ids = [p["id"] for p in papers]
            matrix = np.random.default_rng(len(ids)).standard_normal((len(ids), 8)).astype(np.float32)
            data_store.save_local_embeddings({"model": "test", "ids": ids, "text_hashes": [""] * len(ids)}, matrix)
            data_store.export()
        target = self.root / name
        shutil.copytree(work.data / "export", target)
        return target


def fetcher_for(directory: Optional[Path]):
    """Stand-in for _hf_fetch / _release_fetch serving files from a directory."""

    def fetch(filename: str, workdir: Path) -> Optional[Path]:
        if directory is None or not (directory / filename).exists():
            return None
        workdir.mkdir(parents=True, exist_ok=True)
        return Path(shutil.copy2(directory / filename, workdir / filename))

    return fetch


class RestoreTests(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.box = RadarSandbox(Path(self._tmp.name))

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def restore_with(self, hf: Optional[Path], release: Optional[Path], **extra):
        with self.box.patched(), \
                mock.patch.object(data_store, "_hf_fetch", fetcher_for(hf)), \
                mock.patch.object(data_store, "_release_fetch", fetcher_for(release)), \
                mock.patch.object(data_store, "_legacy_candidate", extra.get("legacy", lambda workdir: None)):
            record = data_store.restore("auto")
            papers = json.loads((self.box.data / "papers.json").read_text())["papers"]
        return record, papers

    # -- 1. newest copy wins ------------------------------------------------
    def test_stale_hf_loses_to_newer_release(self):
        hf = self.box.make_export("hf", make_papers(3), "2026-11-01T00:00:00")
        release = self.box.make_export("release", make_papers(5), "2026-11-10T00:00:00")
        record, papers = self.restore_with(hf, release)
        self.assertEqual(record["source"], "release")
        self.assertEqual(len(papers), 5)
        self.assertEqual({c["source"] for c in record["considered"]}, {"hf", "release"})

    def test_stale_release_loses_to_newer_hf(self):
        hf = self.box.make_export("hf", make_papers(5), "2026-11-10T00:00:00")
        release = self.box.make_export("release", make_papers(3), "2026-11-01T00:00:00")
        record, papers = self.restore_with(hf, release)
        self.assertEqual(record["source"], "hf")
        self.assertEqual(len(papers), 5)

    def test_empty_hf_dataset_does_not_block_release(self):
        empty_hf = self.box.root / "hf_empty"
        empty_hf.mkdir()
        release = self.box.make_export("release", make_papers(4), "2026-11-10T00:00:00")
        record, papers = self.restore_with(empty_hf, release)
        self.assertEqual(record["source"], "release")
        self.assertEqual(len(papers), 4)

    def test_restored_snapshot_replaces_older_local_copy(self):
        with self.box.patched():
            data_store._write_papers_json(make_papers(2), "2026-10-01T00:00:00")
        release = self.box.make_export("release", make_papers(6), "2026-11-10T00:00:00")
        record, papers = self.restore_with(None, release)
        self.assertEqual(record["source"], "release")
        self.assertEqual(len(papers), 6)

    # -- 2. first run bootstraps from the legacy branch ----------------------
    def test_first_run_fetches_legacy_branch_when_hf_and_release_are_empty(self):
        legacy_dir = self.box.root / "legacy"
        legacy_dir.mkdir()
        (legacy_dir / "papers.json").write_text(json.dumps({"last_updated": "2026-11-06T00:00:00",
                                                            "papers": make_papers(7)}))
        (legacy_dir / "stats.json").write_text(json.dumps(STATS))
        calls: List[List[str]] = []
        fetched = {"done": False}

        def fake_git(*args, stdout=subprocess.PIPE):
            calls.append(list(args))
            if args[0] == "rev-parse":
                return subprocess.CompletedProcess(args, 0 if fetched["done"] else 1, b"", b"")
            if args[0] == "fetch":
                fetched["done"] = True
                return subprocess.CompletedProcess(args, 0, b"", b"")
            if args[0] == "show":
                if not fetched["done"]:
                    return subprocess.CompletedProcess(args, 128, b"", b"unknown ref")
                path = legacy_dir / args[1].split(":data/")[1]
                if not path.exists():
                    return subprocess.CompletedProcess(args, 128, b"", b"missing")
                stdout.write(path.read_bytes())
                return subprocess.CompletedProcess(args, 0, b"", b"")
            raise AssertionError(args)

        with self.box.patched(), \
                mock.patch.object(data_store, "HF_DATASET_REPO", "someone/configured-but-empty"), \
                mock.patch.object(data_store, "_hf_fetch", fetcher_for(None)), \
                mock.patch.object(data_store, "_release_fetch", fetcher_for(None)), \
                mock.patch.object(data_store, "_git", fake_git):
            record = data_store.restore("auto")
            stats_exists = (self.box.data / "stats.json").exists()

        self.assertEqual(record["source"], "legacy-git")
        self.assertEqual(record["papers"], 7)
        self.assertTrue(any(c[0] == "fetch" for c in calls), "legacy branch was not fetched")
        self.assertTrue(stats_exists)

    def test_refuses_when_no_source_has_data(self):
        with self.assertRaises(SystemExit):
            self.restore_with(None, None)

    # -- 3. stats.json always comes back -------------------------------------
    def test_stats_restored_from_snapshot(self):
        release = self.box.make_export("release", make_papers(4), "2026-11-10T00:00:00")
        self.restore_with(None, release)
        stats = json.loads((self.box.data / "stats.json").read_text())
        self.assertEqual(stats["last_updated"], "2026-11-10T00:00:00")

    def test_stats_recomputed_when_snapshot_has_none(self):
        release = self.box.make_export("release", make_papers(4), "2026-11-10T00:00:00", with_stats=False)
        self.restore_with(None, release)
        stats = json.loads((self.box.data / "stats.json").read_text())
        self.assertEqual(stats["summary"]["total_papers"], 4)

    def test_site_only_build_publishes_stats(self):
        """push-to-main path: restore -> build_site_data, no arXiv fetch."""
        release = self.box.make_export("release", make_papers(9), "2026-11-10T00:00:00")
        self.restore_with(None, release)
        with self.box.patched():
            manifest = build_site_data.build()
        self.assertTrue((self.box.site / "stats.json").exists())
        self.assertTrue((self.box.site / "manifest.json").exists())
        self.assertEqual(manifest["total_papers"], 9)
        self.assertIsNotNone(manifest["stats"])


if __name__ == "__main__":
    unittest.main()
