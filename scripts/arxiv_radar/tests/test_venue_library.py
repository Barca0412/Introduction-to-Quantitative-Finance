"""S11 top-venue library: records, matching radar papers, venue precedence, missed papers.

    python3 -m unittest scripts.arxiv_radar.tests.test_venue_library -v

No network: adapters are not called; parsing helpers get local text.
"""

import tempfile
import unittest
from pathlib import Path
from unittest import mock

from scripts.arxiv_radar import venue_library as L
from scripts.arxiv_radar import venues as V


def row(venue, year, title, authors, **kw):
    return L.make_record(venue, year, "test", title, authors, kw.pop("abstract", ""), **kw)


LIB = [
    row("neurips", 2026, "Towards Financial World Modeling", ["Ana Lee", "Bo Chen"], track="main", decision="Accept (spotlight)"),
    row("kdd", 2023, "Generating Synergistic Formulaic Alpha Collections via Reinforcement Learning", ["Shuo Yu", "Hongyan Xue"], arxiv_id="2306.12964"),
    row("iclr", 2025, "A Totally Unrelated Vision Paper About Cats", ["Zed Q"]),
    row("jfe", 2025, "Machine Learning and the Cross-Section of Bond Returns", ["Kim Ng"]),
    row("jfe", 2025, "Dividend Policy and Taxes", ["Kim Ng"]),
]


class RecordTest(unittest.TestCase):
    def test_flags(self):
        self.assertTrue(LIB[0]["fin_flag"])
        self.assertFalse(LIB[2]["fin_flag"])
        self.assertTrue(LIB[3]["fin_flag"] and LIB[3]["ai_flag"])
        self.assertTrue(LIB[4]["fin_flag"] and not LIB[4]["ai_flag"])
        self.assertEqual(L.title_key("Towards Financial World-Modeling!"), "towardsfinancialworldmodeling")

    def test_acl_bib_parsing(self):
        bib = '''@inproceedings{wei-2024,
    title = "Are {LLM}s Good Annotators for Stock Market News?",
    author = "Wei, Kangda  and
      Huang, Ruihong",
    url = "https://aclanthology.org/2024.findings-emnlp.1/",
    doi = "10.18653/v1/2024.findings-emnlp.1",
    pages = "1--19"
}'''
        with mock.patch.object(L, "_get", lambda url, **kw: bib.encode() if "findings" in url else None):
            out = L.fetch_acl_anthology("emnlp", 2024, L.SOURCES["emnlp"])
        self.assertEqual(len(out), 1)
        self.assertEqual(out[0]["title"], "Are LLMs Good Annotators for Stock Market News?")
        self.assertEqual(out[0]["authors"], ["Kangda Wei", "Ruihong Huang"])
        self.assertEqual(out[0]["track"], "findings")
        self.assertTrue(out[0]["fin_flag"])

    def test_storage_round_trip(self):
        with tempfile.TemporaryDirectory() as tmp, mock.patch.object(L, "LIBRARY_DIR", Path(tmp)):
            L.save("neurips", 2026, LIB[:1])
            back = L.load_all()
        self.assertEqual(back[0]["title"], "Towards Financial World Modeling")
        self.assertNotIn("abstract", back[0])  # abstracts are never stored


class MatchTest(unittest.TestCase):
    index = L.LibraryIndex(LIB)

    def test_by_arxiv_id_then_title(self):
        hit = self.index.match({"id": "2306.12964v2", "title": "Different title"})
        self.assertEqual((hit["venue_id"], hit["match_method"]), ("kdd", "arxiv_id"))
        hit = self.index.match({"id": "2610.09048", "title": "Towards Financial World Modeling"})
        self.assertEqual((hit["venue_id"], hit["match_method"]), ("neurips", "title_exact"))

    def test_fuzzy_needs_a_shared_author(self):
        paper = {"id": "1", "title": "Towards a Financial World Modeling", "authors": [{"name": "B. Chen"}]}
        self.assertEqual(self.index.match(paper)["match_method"], "title_fuzzy")
        paper["authors"] = [{"name": "Someone Else"}]
        self.assertIsNone(self.index.match(paper))

    def test_tagging_and_venue_precedence(self):
        papers = [{"id": "2610.09048", "title": "Towards Financial World Modeling", "relevance": 3,
                   "venue_mention": "Accepted at ICLR 2026"}, {"id": "x", "title": "old, never scored"}]
        report = L.tag_papers(papers, LIB)
        self.assertEqual(report["matched"], 1)
        self.assertNotIn("venue_list", papers[1])
        V.classify_paper(papers[0])
        v = papers[0]["venue"]
        self.assertEqual((v["name"], v["source"], v["status"], v["year"]), ("NeurIPS", "venue_list", "accepted", 2026))
        self.assertEqual(papers[0]["discipline_basis"], "venue")

    def test_missed_finance_papers(self):
        radar = [{"title": "Towards Financial World Modeling"}]
        missed = L.missed_finance_papers(radar, LIB, since_year=2025)
        self.assertEqual([r["title"] for r in missed], ["Machine Learning and the Cross-Section of Bond Returns"])


if __name__ == "__main__":
    unittest.main()


class OpenAlexKeyTest(unittest.TestCase):
    def test_key_added_and_redacted(self):
        from scripts.arxiv_radar import config

        with mock.patch.object(config, "OPENALEX_API_KEY", "SECRET123"):
            self.assertEqual(config.openalex_url("https://api.openalex.org/works?x=1"),
                             "https://api.openalex.org/works?x=1&api_key=SECRET123")
            self.assertEqual(config.openalex_url("https://api.openalex.org/works/doi:1"),
                             "https://api.openalex.org/works/doi:1?api_key=SECRET123")
            self.assertNotIn("SECRET123", config.redact("Giving up on https://x?api_key=SECRET123"))
        with mock.patch.object(config, "OPENALEX_API_KEY", ""):
            self.assertEqual(config.openalex_url("https://a?b=1"), "https://a?b=1")
