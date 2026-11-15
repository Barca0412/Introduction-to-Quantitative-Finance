"""Focus flags use whole words, not substrings.

    python3 -m unittest scripts.arxiv_radar.tests.test_focus -v
"""

import unittest

from scripts.arxiv_radar.focus import build_focus_metadata


def paper(title, abstract="", categories=("cs.LG",), tags=()):
    return {"title": title, "abstract": abstract, "categories": list(categories), "tags": list(tags), "keywords": []}


class FocusWholeWordTest(unittest.TestCase):
    def test_substrings_no_longer_trigger_signals(self):
        meta = build_focus_metadata(paper(
            "A definition of reaction kinetics for marketing assets",
            "We study the risk of reagent misuse with alpha-blending.",
        ))
        self.assertNotIn("finance signal", meta["reasons"])
        self.assertNotIn("agent signal", meta["reasons"])
        self.assertEqual(meta["topics"], [])
        self.assertFalse(meta["is_focus"])

    def test_generic_ml_words_are_not_finance(self):
        meta = build_focus_metadata(paper(
            "Credit assignment for LLM agents",
            "We bound the excess risk of a large language model agent in a market of tools.",
        ))
        self.assertNotIn("finance signal", meta["reasons"])
        self.assertNotIn("ai-finance", meta["topics"])

    def test_real_finance_llm_paper_is_ai_finance(self):
        meta = build_focus_metadata(paper(
            "LLM agents for stock trading",
            "A large language model agent trades stocks and manages a portfolio.",
        ))
        self.assertIn("finance signal", meta["reasons"])
        self.assertIn("ai-finance", meta["topics"])
        self.assertTrue(meta["is_focus"])

    def test_same_finance_words_as_the_fetch_filter(self):
        off = build_focus_metadata(paper("Trading off accuracy and cost in LLM model portfolios",
                                         "A large language model router."))
        self.assertNotIn("ai-finance", off["topics"])
        on = build_focus_metadata(paper("LLM agents for insurance claims triage",
                                        "A large language model agent reviews insurance claims."))
        self.assertIn("ai-finance", on["topics"])

    def test_q_fin_category_still_counts_as_finance(self):
        meta = build_focus_metadata(paper("Rough volatility calibration", categories=("q-fin.MF",)))
        self.assertIn("finance signal", meta["reasons"])


if __name__ == "__main__":
    unittest.main()
