"""S5 keyword normalisation against vocab/keywords.yaml.

    python3 -m unittest scripts.arxiv_radar.tests.test_keywords -v
"""

import unittest

from scripts.arxiv_radar import keywords as K


class KeywordTest(unittest.TestCase):
    def test_vocabulary_loads_and_ids_are_unique(self):
        ids = [e["id"] for e in K.vocabulary()]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertGreater(len(ids), 60)

    def test_spelling_variants_meet(self):
        for raw, want in [
            ("LLM-based agents", "LLM agents"), ("tool-using LLM agents", "LLM agents"),
            ("Limit Order Book (LOB)", "limit order book"), ("price impact", "market impact"),
            ("stock price forecasting", "return prediction"), ("anti-money laundering", "anti-money laundering"),
            ("gradient-boosted decision trees", "gradient boosting and trees"), ("DeFi lending", "cryptocurrency and DeFi"),
            ("multi-agent reinforcement learning", "multi-agent reinforcement learning"),
            ("agent-based model", "agent-based models"), ("earnings calls", "financial sentiment analysis"),
        ]:
            entry, _ = K.match(raw)
            self.assertIsNotNone(entry, raw)
            self.assertEqual(entry["en"], want, raw)

    def test_no_false_matches_seen_in_the_november_data(self):
        for raw in ["local definitions", "tokenization", "Arabic social media corpus", "codebook audit",
                    "bitemporal inventory simulation", "consumer task automation"]:
            entry, _ = K.match(raw)
            self.assertIsNone(entry, f"{raw} -> {entry and entry['en']}")

    def test_paper_normalisation(self):
        paper = {"keywords_raw": [
            {"text": "LLM agents", "kind": "tech"}, {"text": "LLM-based agent", "kind": "tech"},
            {"text": "Fuzzy cognitive maps", "kind": "tech"}, {"text": "credit scoring", "kind": "finance"}]}
        self.assertTrue(K.normalize_paper_keywords(paper))
        self.assertEqual(paper["keywords"], ["LLM agents", "fuzzy cognitive maps", "credit scoring"])
        self.assertEqual([k["new"] for k in paper["keywords_norm"]], [False, True, False])
        self.assertEqual(paper["keywords_norm"][2]["zh"], "信用评分")
        self.assertFalse(K.normalize_paper_keywords(paper))  # idempotent

    def test_report(self):
        papers = [{"keywords_raw": [{"text": "LLM agents"}, {"text": "fuzzy maps"}]}, {"title": "no v2"}]
        report = K.normalize_all(papers)
        self.assertEqual((report["keywords"], report["matched"]), (2, 1))
        self.assertEqual(report["top_new_terms"], [("fuzzy maps", 1)])


if __name__ == "__main__":
    unittest.main()
