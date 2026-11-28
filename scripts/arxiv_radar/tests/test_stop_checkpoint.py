"""Stop on HTTP 401/402/403 and save progress every N papers.

    python3 -m unittest scripts.arxiv_radar.tests.test_stop_checkpoint -v

No network: the LLM client and arXiv fetch are fakes.
"""

from __future__ import annotations

import asyncio
import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from scripts.arxiv_radar import enrich
from scripts.arxiv_radar import fetch_papers as fp
from scripts.arxiv_radar import llm_processor as lp
from scripts.arxiv_radar import storage
from scripts.arxiv_radar.tests.test_enrich import GOOD


def paper(i):
    return {"id": f"2611.{i:05d}", "title": f"Paper {i}", "abstract": "A stock trading agent.",
            "categories": ["q-fin.TR"], "published_date": "2026-11-13", "tags": [], "keywords": [], "summary_zh": ""}


class FakeClient:
    """Answers well for the first `ok` calls, then every call gets HTTP 402."""
    calls = 0

    def __init__(self, *args, ok=5, **kwargs):
        self.ok = ok

    async def __aenter__(self):
        return self

    async def __aexit__(self, *exc):
        return False

    async def call_llm(self, messages):
        type(self).calls += 1
        refused = type(self).calls > self.ok
        await asyncio.sleep(0)  # let other papers run, like a real HTTP call
        if refused:
            raise lp.FatalLLMError('API error 402: {"error":{"message":"Insufficient Balance"}}')
        return json.dumps(GOOD, ensure_ascii=False)


class RetryTest(unittest.TestCase):
    def test_fatal_errors_are_not_retried(self):
        calls = []

        @lp.async_retry(max_retries=3, base_delay=0)
        async def call():
            calls.append(1)
            raise lp.FatalLLMError("API error 402")

        with self.assertRaises(lp.FatalLLMError):
            asyncio.run(call())
        self.assertEqual(len(calls), 1)


class BatchStopTest(unittest.TestCase):
    def setUp(self):
        FakeClient.calls = 0
        patches = [
            mock.patch.object(lp, "LLMClient", lambda *a, **k: FakeClient(ok=5)),
            mock.patch.object(lp, "LLM_API_KEY", "fake"),
        ]
        for p in patches:
            p.start()
            self.addCleanup(p.stop)

    def test_stops_and_reports_finished_papers(self):
        papers = [paper(i) for i in range(40)]
        with self.assertRaises(lp.LLMBudgetExhausted) as ctx:
            asyncio.run(lp.process_papers_batch(papers, concurrency=4))
        finished = ctx.exception.papers
        self.assertEqual(len(finished), 5)
        self.assertTrue(all((p.get("stage_versions") or {}).get("enrich") == enrich.ENRICH_VERSION for p in finished))
        self.assertIn("402", str(ctx.exception))
        # Far fewer calls than 40 papers x 3 tries: the batch stopped at once.
        self.assertLess(FakeClient.calls, 15)
        # Input papers were copied, never marked as failed.
        self.assertTrue(all("attempts" not in p for p in papers))

    def test_checkpoint_every_n(self):
        saved = []

        async def checkpoint(done):
            saved.append(len(done))

        with mock.patch.object(lp, "LLMClient", lambda *a, **k: FakeClient(ok=1000)):
            out = asyncio.run(lp.process_papers_batch([paper(i) for i in range(25)], 4, checkpoint, 10))
        self.assertEqual(saved, [10, 20])
        self.assertEqual([p["id"] for p in out], [paper(i)["id"] for i in range(25)])


class PipelineStopTest(unittest.TestCase):
    def run_pipeline(self, existing, fetched, ok, checkpoint_file, every=4):
        saved = []

        async def fake_fetch(categories):
            return fetched, [{"category": "q-fin.TR", "papers": len(fetched), "error": None}]

        with mock.patch.object(fp, "fetch_all_categories", fake_fetch), \
             mock.patch.object(fp, "report_fetch", lambda r: None), \
             mock.patch.object(fp, "load_papers", lambda: existing), \
             mock.patch.object(fp, "save_papers", lambda data: saved.append(data)), \
             mock.patch.object(fp, "enrich_institutions", self.no_institutions), \
             mock.patch.object(fp, "compute_and_save_stats", lambda papers, **_: {"tag_stats": {"_all": {"daily": {}}}}), \
             mock.patch.object(fp, "generate_all_charts", lambda stats: None), \
             mock.patch.object(fp, "generate_combined_chart", lambda stats: None), \
             mock.patch.object(storage, "ENRICH_CHECKPOINT_FILE", checkpoint_file), \
             mock.patch.object(fp, "LLM_API_KEY", "fake"), \
             mock.patch.object(lp, "LLM_API_KEY", "fake"), \
             mock.patch.object(lp, "CHECKPOINT_EVERY", every), \
             mock.patch.object(lp, "LLMClient", lambda *a, **k: FakeClient(ok=ok)), \
             mock.patch.dict("os.environ", {"GITHUB_STEP_SUMMARY": ""}):
            try:
                asyncio.run(fp.run_pipeline())
                error = None
            except SystemExit as exc:
                error = str(exc)
        return saved, error

    @staticmethod
    async def no_institutions(papers):
        return {"looked_up": 0}

    def setUp(self):
        FakeClient.calls = 0
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.checkpoint = Path(self.tmp.name) / "enrich_checkpoint.jsonl"

    def enriched(self, ids):
        return [p for p in ids if (p.get("stage_versions") or {}).get("enrich") == enrich.ENRICH_VERSION]

    def test_saves_progress_then_exits_on_402(self):
        existing = {"papers": [{**paper(99), "summary_zh": "旧摘要"}]}
        saved, error = self.run_pipeline(existing, [paper(i) for i in range(30)], ok=9, checkpoint_file=self.checkpoint)
        self.assertIn("Saved 9 finished papers", error)
        self.assertIn("21 were not attempted", error)
        self.assertEqual(len(saved), 1)
        final = saved[-1]["papers"]
        self.assertIn(paper(99)["id"], {p["id"] for p in final})
        self.assertEqual(len(self.enriched(final)), 9)
        self.assertFalse(self.checkpoint.exists())  # everything is in the saved history now

    def test_checkpoint_is_recovered_after_a_crash(self):
        # A crash (Ctrl+C, power cut) after 8 papers: only the checkpoint file survives.
        FakeClient.calls = 0
        crashed = [p for p in asyncio.run(self.enrich_some(8))]
        storage_file = self.checkpoint
        with mock.patch.object(storage, "ENRICH_CHECKPOINT_FILE", storage_file):
            storage.append_checkpoint(crashed)
            with open(storage_file, "a", encoding="utf-8") as fh:
                fh.write('{"id": "2611.0')  # torn last line
        FakeClient.calls = 0
        saved, error = self.run_pipeline({"papers": []}, [paper(i) for i in range(12)], ok=1000,
                                         checkpoint_file=storage_file)
        self.assertIsNone(error)
        self.assertEqual(FakeClient.calls, 4)  # only the 4 papers the crashed run had not done
        self.assertEqual(len(self.enriched(saved[-1]["papers"])), 12)
        self.assertFalse(storage_file.exists())

    async def enrich_some(self, n):
        with mock.patch.object(lp, "LLMClient", lambda *a, **k: FakeClient(ok=1000)), \
             mock.patch.object(lp, "LLM_API_KEY", "fake"):
            return await lp.process_papers_batch([paper(i) for i in range(n)], 4)


if __name__ == "__main__":
    unittest.main()
