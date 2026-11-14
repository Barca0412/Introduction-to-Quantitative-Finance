"""Checks for rule-based tags and how LLM tags replace them.

Run from the repository root:

    python3 -m unittest scripts.arxiv_radar.tests.test_tags -v
"""

from __future__ import annotations

import unittest

from scripts.arxiv_radar import llm_processor as lp
from scripts.arxiv_radar.storage import merge_papers, refresh_rule_tags


def paper(pid="2611.00001", title="", abstract="", **extra):
    return {"id": pid, "title": title, "abstract": abstract, "published_date": "2026-11-12", **extra}


class RuleMatchingTest(unittest.TestCase):
    def test_whole_words_only(self):
        self.assertFalse(lp._has_any("we report the average storage leverage", ["rag"]))
        self.assertFalse(lp._has_any("capital and rapid growth", ["api"]))
        self.assertFalse(lp._has_any("data from scotland", ["cot"]))
        self.assertTrue(lp._has_any("a rag pipeline for finance", ["rag"]))
        self.assertTrue(lp._has_any("graph-rag retrieval", ["rag"]))

    def test_plurals_still_match(self):
        self.assertTrue(lp._has_any("predicting stocks and derivatives", ["stock"]))
        self.assertTrue(lp._has_any("apis for agents", ["api"]))

    def test_bare_retrieval_is_not_rag(self):
        p = paper(title="Dense retrieval for web search", abstract="We study neural retrieval models.")
        self.assertNotIn("rag", lp.fallback_tags_for_paper(p))
        p = paper(title="Retrieval-augmented generation for earnings calls", abstract="A RAG system for financial QA.")
        self.assertIn("rag", lp.fallback_tags_for_paper(p))


class MergeTest(unittest.TestCase):
    def test_llm_tags_replace_rule_tags(self):
        stored = paper(tags=["rag", "memory"], keywords=[], summary_zh="")
        enriched = paper(tags=["ai-finance"], keywords=["factor investing"], summary_zh="一篇关于因子投资的论文。")
        merged = merge_papers({"papers": [stored]}, [enriched])["papers"][0]
        self.assertEqual(merged["tags"], ["ai-finance"])
        self.assertEqual(merged["keywords"], ["factor investing"])
        self.assertEqual(merged["summary_zh"], "一篇关于因子投资的论文。")

    def test_two_llm_versions_are_merged(self):
        stored = paper(tags=["ai-finance"], keywords=["alpha"], summary_zh="旧摘要")
        incoming = paper(tags=["time-series"], keywords=["forecasting"], summary_zh="新摘要")
        merged = merge_papers({"papers": [stored]}, [incoming])["papers"][0]
        self.assertEqual(set(merged["tags"]), {"ai-finance", "time-series"})


class RefreshRuleTagsTest(unittest.TestCase):
    def test_only_papers_without_llm_summary_are_retagged(self):
        rule_tagged = paper(pid="2611.00001", title="Average storage costs", abstract="", tags=["rag"], summary_zh="")
        llm_tagged = paper(pid="2611.00002", title="Average storage costs", abstract="", tags=["rag"], summary_zh="已由大模型处理")
        changed = refresh_rule_tags([rule_tagged, llm_tagged], lp.fallback_tags_for_paper)
        self.assertEqual(changed, 1)
        self.assertNotIn("rag", rule_tagged["tags"])
        self.assertEqual(llm_tagged["tags"], ["rag"])


if __name__ == "__main__":
    unittest.main()
