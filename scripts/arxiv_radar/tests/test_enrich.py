"""S3 enrichment v2: prompt, validation, retries, storage and export of the new fields.

    python3 -m unittest scripts.arxiv_radar.tests.test_enrich -v

No network: the LLM client is a local fake.
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
from scripts.arxiv_radar.focus import build_focus_metadata
from scripts.arxiv_radar.storage import merge_papers, normalize_paper

PAPER = {
    "id": "2306.12964",
    "title": "Generating Synergistic Formulaic Alpha Collections via Reinforcement Learning",
    "abstract": "We use reinforcement learning to mine formulaic alpha factors on Chinese stocks.",
    "categories": ["q-fin.ST", "cs.LG"],
    "published_date": "2023-06-22",
    "comment": "Accepted by KDD '23, ADS track",
}

GOOD = {
    "relevance": 3,
    "relevance_reason_zh": "核心是因子挖掘这一金融问题。",
    "paper_type": "method",
    "task_types": ["signal-mining"],
    "finance_domains": ["asset-pricing"],
    "methods": ["rl"],
    "tags": ["ai-finance"],
    "keywords": [{"text": "formulaic alpha", "kind": "finance"}, {"text": "reinforcement learning", "kind": "tech"}],
    "data_market": ["a-share"],
    "reproducibility": {"code": None, "data_public": None},
    "tldr_zh": "用强化学习生成一组相互配合的公式化因子，在A股上组合效果优于单独挖掘的因子。",
    "points_zh": {"problem": "单个因子难以组合。", "method": "以组合表现为奖励训练生成器。", "result": "IC 更高。", "limitation": "摘要未说明"},
    "venue_mention": "Accepted by KDD '23, ADS track",
    "withdrawn": False,
}


def answer(**changes):
    return json.dumps({**GOOD, **changes}, ensure_ascii=False)


class TaxonomyAndPromptTest(unittest.TestCase):
    def test_prompt_lists_every_id_and_rule(self):
        text = enrich.build_messages(PAPER)[1]["content"]
        for key in ("paper_types", "task_types", "finance_domains", "methods", "data_markets"):
            for item_id in enrich.ids(key):
                self.assertIn(f'"{item_id}"', text, (key, item_id))
        for rule in enrich.taxonomy()["rules"]:
            self.assertIn(rule, text)
        self.assertIn("arXiv comment: Accepted by KDD", text)

    def test_final_taxonomy_from_the_trials(self):
        self.assertEqual(len(enrich.ids("paper_types")), 6)
        self.assertIn("theory", enrich.ids("paper_types"))
        self.assertEqual(len(enrich.ids("task_types")), 9)
        self.assertIn("pricing", enrich.ids("task_types"))
        self.assertEqual(len(enrich.ids("finance_domains")), 12)
        self.assertEqual(len(enrich.ids("methods")), 9)

    def test_error_hint_is_sent_back(self):
        text = enrich.build_messages(PAPER, "paper_type must be one of ...")[1]["content"]
        self.assertIn("previous answer was rejected: paper_type must be one of", text)


class ValidateTest(unittest.TestCase):
    def check(self, **changes):
        return enrich.validate(enrich.extract_json(answer(**changes)), PAPER)

    def test_good_answer(self):
        result, warnings = self.check()
        self.assertEqual(warnings, [])
        self.assertEqual(result["relevance"], 3)
        self.assertEqual(result["keywords_raw"][0], {"text": "formulaic alpha", "kind": "finance"})

    def test_hard_errors(self):
        for changes, message in [
            ({"relevance": 5}, "relevance"),
            ({"relevance": "high"}, "relevance"),
            ({"paper_type": "position paper"}, "paper_type"),
            ({"tldr_zh": ""}, "tldr_zh"),
            ({"task_types": []}, "task_types"),
        ]:
            with self.assertRaises(enrich.EnrichError) as ctx:
                self.check(**changes)
            self.assertIn(message, str(ctx.exception))
        with self.assertRaises(enrich.EnrichError):
            enrich.extract_json("I think it is about finance.")

    def test_soft_fixes(self):
        result, warnings = self.check(
            finance_domains=["general", "asset-pricing", "astrology"],
            methods=[],
            task_types=["forecasting", "pricing", "decision"],
            data_market=["none", "us"],
        )
        self.assertEqual(result["finance_domains"], ["asset-pricing"])
        self.assertEqual(result["methods"], ["other"])
        self.assertEqual(result["task_types"], ["forecasting", "pricing"])
        self.assertEqual(result["data_market"], ["us"])
        self.assertTrue(any("astrology" in w for w in warnings))

    def test_relevance_zero_clears_domains_and_ai_finance_tag(self):
        result, _ = self.check(relevance=0, task_types=[], finance_domains=["trading"], tags=["ai-finance", "time-series"])
        self.assertEqual(result["finance_domains"], [])
        self.assertEqual(result["tags"], ["time-series"])

    def test_relevant_paper_always_gets_ai_finance_tag(self):
        result, _ = self.check(tags=["rag"])
        self.assertEqual(result["tags"][0], "ai-finance")

    def test_withdrawn_from_comment_even_if_model_misses_it(self):
        paper = {**PAPER, "comment": "We have temporarily withdrawn the working paper from circulation."}
        result, _ = enrich.validate(enrich.extract_json(answer(withdrawn=False)), paper)
        self.assertTrue(result["withdrawn"])

    def test_tolerates_fences_and_python_literals(self):
        raw = enrich.extract_json("```json\n" + answer().replace("null", "None") + "\n```")
        self.assertEqual(raw["relevance"], 3)


class ApplyAndVersionTest(unittest.TestCase):
    def test_apply_sets_legacy_fields_and_version(self):
        paper = dict(PAPER)
        result, warnings = enrich.validate(enrich.extract_json(answer()), paper)
        enrich.apply_result(paper, result, warnings)
        self.assertEqual(paper["keywords"], ["formulaic alpha", "reinforcement learning"])
        self.assertTrue(paper["summary_zh"].startswith("用强化学习"))
        self.assertIn("问题：", paper["summary_zh"])
        self.assertNotIn("摘要未说明", paper["summary_zh"])
        self.assertEqual(paper["stage_versions"]["enrich"], enrich.ENRICH_VERSION)
        self.assertFalse(enrich.needs_enrich(paper))

    def test_failures_are_counted_per_version(self):
        paper = {"id": "1", "stage_versions": {"enrich": "s3-v1"}, "attempts": {"enrich": 7, "enrich_version": "s3-v1"}}
        self.assertTrue(enrich.needs_enrich(paper))
        for _ in range(enrich.MAX_ENRICH_ATTEMPTS):
            enrich.record_failure(paper, "boom")
        self.assertEqual(paper["attempts"], {"enrich": 3, "enrich_version": enrich.ENRICH_VERSION})
        self.assertFalse(enrich.needs_enrich(paper))

    def test_consistency_flags(self):
        flags = enrich.consistency_flags({"relevance": 0, "categories": ["q-fin.TR"]})
        self.assertEqual(flags, ["q-fin-but-irrelevant"])
        flags = enrich.consistency_flags({"relevance": 3, "finance_domains": [], "keywords_raw": [{"text": "x", "kind": "tech"}]})
        self.assertEqual(flags, ["relevant-without-domain", "relevant-without-finance-keyword"])


class FakeClient:
    def __init__(self, replies):
        self.replies = list(replies)
        self.messages = []

    async def call_llm(self, messages):
        self.messages.append(messages)
        reply = self.replies.pop(0)
        if isinstance(reply, Exception):
            raise reply
        return reply


class ProcessPaperTest(unittest.TestCase):
    def test_retries_with_reason_then_succeeds(self):
        client = FakeClient([answer(paper_type="essay"), answer()])
        paper = asyncio.run(lp.process_paper(dict(PAPER), client))
        self.assertEqual(paper["relevance"], 3)
        self.assertEqual(len(client.messages), 2)
        self.assertIn("previous answer was rejected", client.messages[1][1]["content"])

    def test_failure_keeps_old_enrichment_and_counts(self):
        old = {**PAPER, "summary_zh": "旧摘要", "tags": ["ai-finance"], "keywords": ["alpha"]}
        client = FakeClient([answer(relevance=9)] * 3)
        paper = asyncio.run(lp.process_paper(old, client))
        self.assertEqual(paper["summary_zh"], "旧摘要")
        self.assertEqual(paper["tags"], ["ai-finance"])
        self.assertEqual(paper["attempts"]["enrich"], 1)
        self.assertIn("relevance", paper["last_error"])
        self.assertEqual(len(client.messages), lp.VALIDATION_RETRIES + 1)

    def test_http_failure_is_not_retried_here(self):
        client = FakeClient([RuntimeError("API error 500")])
        paper = asyncio.run(lp.process_paper(dict(PAPER), client))
        self.assertEqual(len(client.messages), 1)
        self.assertIn("API error 500", paper["last_error"])
        self.assertTrue(paper["tags"])  # rule-based fallback


class StorageAndPipelineTest(unittest.TestCase):
    def enriched(self, **changes):
        paper = dict(PAPER)
        result, warnings = enrich.validate(enrich.extract_json(answer(**changes)), paper)
        return enrich.apply_result(paper, result, warnings)

    def test_normalize_keeps_v2_fields(self):
        paper = normalize_paper(self.enriched())
        self.assertEqual(paper["finance_domains"], ["asset-pricing"])
        self.assertEqual(paper["comment"], "Accepted by KDD '23, ADS track")
        self.assertTrue(paper["focus"]["is_focus"])

    def test_v2_replaces_v1_instead_of_merging(self):
        v1 = {**PAPER, "summary_zh": "旧摘要", "tags": ["ai-finance", "rag", "memory"], "keywords": ["old"]}
        merged = merge_papers({"papers": [v1]}, [self.enriched(tags=["time-series"])])["papers"][0]
        self.assertEqual(merged["keywords"], ["formulaic alpha", "reinforcement learning"])
        self.assertNotIn("rag", merged["tags"])
        self.assertTrue(merged["summary_zh"].startswith("用强化学习"))

    def test_older_record_does_not_overwrite_v2(self):
        v1 = {**PAPER, "summary_zh": "旧摘要", "tags": ["rag"]}
        merged = merge_papers({"papers": [self.enriched()]}, [v1])["papers"][0]
        self.assertEqual(merged["relevance"], 3)
        self.assertEqual(merged["stage_versions"]["enrich"], enrich.ENRICH_VERSION)

    def test_needs_enrichment_resumes_from_the_stored_record(self):
        stored_v1 = {**PAPER, "summary_zh": "旧摘要", "attempts": {"enrich": 2, "enrich_version": enrich.ENRICH_VERSION}}
        stored_v2 = self.enriched()
        stored_v2["id"] = "2306.00002"
        fetched = [
            {"id": PAPER["id"], "title": PAPER["title"], "summary_zh": "", "tags": [], "comment": "v2 comment"},
            {"id": "2306.00002", "title": "x"},
            {"id": "2611.00001", "title": "new"},
        ]
        todo = fp.needs_enrichment(fetched, {"papers": [stored_v1, stored_v2]})
        self.assertEqual([p["id"] for p in todo], [PAPER["id"], "2611.00001"])
        self.assertEqual(todo[0]["summary_zh"], "旧摘要")
        self.assertEqual(todo[0]["attempts"]["enrich"], 2)
        self.assertEqual(todo[0]["comment"], "v2 comment")

    def test_withdrawn_is_never_focus(self):
        meta = build_focus_metadata({**self.enriched(), "withdrawn": True})
        self.assertFalse(meta["is_focus"])
        self.assertEqual(meta["reasons"][0], "withdrawn")
        meta = build_focus_metadata(self.enriched(relevance=1, task_types=[]))
        self.assertFalse(meta["is_focus"])
        self.assertNotIn("ai-finance", meta["topics"])

    def test_parquet_round_trip(self):
        import pyarrow as pa
        import pyarrow.parquet as pq

        from scripts.arxiv_radar import data_store as ds

        papers = [normalize_paper(self.enriched()), normalize_paper({"id": "2611.00001", "title": "old", "abstract": "a"})]
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "papers.parquet"
            table = pa.Table.from_pylist([ds._clean_paper_for_parquet(p) for p in papers], schema=ds._papers_schema())
            pq.write_table(table, path)
            back = [normalize_paper(p) for p in pq.read_table(path).to_pylist()]
        self.assertEqual(back[0]["points_zh"], papers[0]["points_zh"])
        self.assertEqual(back[0]["keywords_raw"], papers[0]["keywords_raw"])
        self.assertEqual(back[0]["stage_versions"]["enrich"], enrich.ENRICH_VERSION)
        self.assertNotIn("relevance", back[1])
        self.assertTrue(enrich.needs_enrich(back[1]))

    def test_job_summary(self):
        done = self.enriched()
        failed = enrich.record_failure(dict(PAPER, id="2"), "boom")
        with mock.patch.dict("os.environ", {"GITHUB_STEP_SUMMARY": ""}):
            summary = fp.report_enrichment([done, failed])
        self.assertEqual((summary["succeeded"], summary["failed"]), (1, 1))
        self.assertEqual(summary["relevance"]["3"], 1)


if __name__ == "__main__":
    unittest.main()


class TrialFixtureTest(unittest.TestCase):
    def test_labels_use_taxonomy_ids(self):
        from scripts.arxiv_radar import enrich_trial

        labels = enrich_trial.load_labels()
        self.assertEqual(len(labels), 46)
        self.assertEqual(len({l["id"] for l in labels}), 46)
        for label in labels:
            self.assertIn(label["paper_type"], enrich.ids("paper_types"), label["name"])
            for field, key in (("task_types", "task_types"), ("finance_domains", "finance_domains"), ("methods", "methods")):
                for item in label[field]:
                    self.assertIn(item, enrich.ids(key), (label["name"], field))
            self.assertTrue(set(label["relevance"]) <= {0, 1, 2, 3})

    def test_compare_and_report(self):
        from scripts.arxiv_radar import enrich_trial

        label = {"id": PAPER["id"], "name": "AlphaGen", "relevance": [3], "paper_type": "method",
                 "task_types": ["signal-mining"], "finance_domains": ["asset-pricing"], "methods": ["rl", "llm"]}
        paper = dict(PAPER)
        result, warnings = enrich.validate(enrich.extract_json(answer(paper_type="system")), paper)
        enrich.apply_result(paper, result, warnings)
        check = enrich_trial.compare(label, paper)
        self.assertEqual(check, {"failed": False, "relevance": True, "paper_type": False,
                                 "task_types": True, "finance_domains": True, "methods": True})
        failed = enrich.record_failure(dict(PAPER), "boom")
        rows = [{"label": label, "paper": paper, "check": check},
                {"label": {**label, "name": "Broken"}, "paper": failed, "check": enrich_trial.compare(label, failed)}]
        with mock.patch.dict("os.environ", {"GITHUB_STEP_SUMMARY": ""}):
            report = enrich_trial.build_report(rows)
        self.assertIn("| paper_type | 0/1 (0/1) | 0% |", report)
        self.assertIn("| AlphaGen | paper_type | method | system |", report)
        self.assertIn("| Broken | failed |", report)
