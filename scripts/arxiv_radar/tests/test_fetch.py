"""Checks for the arXiv fetch step: retries on HTTP 429, failure reporting, and
skipping papers that already have an LLM summary.

Run from the repository root:

    python3 -m unittest scripts.arxiv_radar.tests.test_fetch -v

No network: the arXiv client is a local fake.
"""

from __future__ import annotations

import asyncio
import io
import os
import tempfile
import unittest
from contextlib import redirect_stdout
from unittest import mock

import arxiv

from scripts.arxiv_radar import fetch_papers as fp

DATES = ["2026-11-12", "2026-11-13"]


def paper(pid: str, date: str = "2026-11-13", **extra):
    return {"id": pid, "published_date": date, **extra}


class FakeClient:
    """Yields the given pages; raises HTTP 429 for the first `fail_times` calls."""

    def __init__(self, results, fail_times=0, fail_after=0):
        self.results_list = results
        self.fail_times = fail_times
        self.fail_after = fail_after  # yield this many results before failing
        self.calls = 0

    def results(self, search):
        self.calls += 1
        if self.calls <= self.fail_times:
            for r in self.results_list[: self.fail_after]:
                yield r
            raise arxiv.HTTPError("https://export.arxiv.org/api/query", 3, 429)
        yield from self.results_list


class FetchCategoryTest(unittest.TestCase):
    def setUp(self):
        # Fake results are already paper dicts.
        patcher = mock.patch.object(fp, "build_paper_record", side_effect=lambda r: r)
        patcher.start()
        self.addCleanup(patcher.stop)

    def test_retries_after_429_then_succeeds(self):
        client = FakeClient([paper("2611.00001"), paper("2611.00002")], fail_times=2)
        sleeps = []
        papers, error = fp.fetch_category_papers("cs.CL", DATES, 3000, client, (30, 90, 180), sleeps.append)
        self.assertIsNone(error)
        self.assertEqual([p["id"] for p in papers], ["2611.00001", "2611.00002"])
        self.assertEqual(sleeps, [30, 90])

    def test_gives_up_and_keeps_best_partial_result(self):
        results = [paper(f"2611.0000{i}") for i in range(5)]
        client = FakeClient(results, fail_times=10, fail_after=3)
        sleeps = []
        papers, error = fp.fetch_category_papers("cs.MA", DATES, 3000, client, (1, 2), sleeps.append)
        self.assertIn("429", error)
        self.assertEqual(len(papers), 3)
        self.assertEqual(sleeps, [1, 2])
        self.assertEqual(client.calls, 3)

    def test_filters_to_target_dates(self):
        client = FakeClient([paper("2611.00001"), paper("2611.00002", date="2026-11-01")])
        papers, error = fp.fetch_category_papers("q-fin.ST", DATES, 3000, client, (), lambda s: None)
        self.assertIsNone(error)
        self.assertEqual([p["id"] for p in papers], ["2611.00001"])

    def test_fetch_all_reports_each_category(self):
        class PerCategory(FakeClient):
            def results(self, search):
                if "cs.CL" in search.query:
                    raise arxiv.HTTPError("u", 3, 429)
                yield paper("2611.00001")

        with mock.patch.object(fp, "get_target_dates", return_value=DATES):
            papers, report = asyncio.run(
                fp.fetch_all_categories(["cs.AI", "cs.CL"], client=PerCategory([]), backoff=(0,), sleep=lambda s: None)
            )
        self.assertEqual(len(papers), 1)
        self.assertEqual([r["category"] for r in report], ["cs.AI", "cs.CL"])
        self.assertIsNone(report[0]["error"])
        self.assertIn("429", report[1]["error"])


class ReportTest(unittest.TestCase):
    def test_failures_become_warnings_and_summary_rows(self):
        report = [
            {"category": "cs.AI", "papers": 788, "error": None},
            {"category": "cs.CL", "papers": 0, "error": "HTTPError: 429"},
        ]
        with tempfile.NamedTemporaryFile("r", suffix=".md", delete=False) as fh:
            path = fh.name
        try:
            out = io.StringIO()
            with mock.patch.dict(os.environ, {"GITHUB_STEP_SUMMARY": path}), redirect_stdout(out):
                fp.report_fetch(report)
            self.assertIn("::warning title=arXiv fetch cs.CL::failed: HTTPError: 429", out.getvalue())
            self.assertNotIn("cs.AI", out.getvalue())
            summary = open(path, encoding="utf-8").read()
            self.assertIn("| cs.AI | 788 | ok |", summary)
            self.assertIn("| cs.CL | 0 | failed: HTTPError: 429 |", summary)
        finally:
            os.unlink(path)


class NeedsEnrichmentTest(unittest.TestCase):
    def test_skips_only_papers_with_a_stored_summary(self):
        existing = {
            "papers": [
                {"id": "2611.00001", "summary_zh": "已有摘要"},
                {"id": "2611.00002v2", "summary_zh": "带版本号也算同一篇"},
                {"id": "2611.00003", "summary_zh": ""},  # earlier LLM failure: retry
            ]
        }
        fetched = [paper("2611.00001"), paper("2611.00002"), paper("2611.00003"), paper("2611.00004")]
        todo = fp.needs_enrichment(fetched, existing)
        self.assertEqual([p["id"] for p in todo], ["2611.00003", "2611.00004"])


if __name__ == "__main__":
    unittest.main()
