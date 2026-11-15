"""Venue and discipline detection (vocab/venues.yaml, venues.py).

    python3 -m unittest scripts.arxiv_radar.tests.test_venues -v
"""

import unittest

from scripts.arxiv_radar import venues as V


class VenueTest(unittest.TestCase):
    def test_table_loads(self):
        self.assertGreater(len(V.venue_table()), 140)
        tops = {e["id"] for e in V.venue_table() if e.get("top")}
        self.assertTrue({"neurips", "icml", "iclr", "kdd", "acm-mm", "icaif", "jf", "jfe", "rfs"} <= tops)

    def test_comments_from_the_trials(self):
        cases = [
            ("Accepted by KDD '23, ADS track", "comment", ("KDD", "conference", "cs", "accepted", 2023)),
            ("Published at EMNLP 2024 (Main Conference)", "comment", ("EMNLP", "conference", "cs", "published", 2024)),
            ("Accepted by the FinLLM Symposium at IJCAI 2023", "comment", ("IJCAI", "workshop", "cs", "accepted", 2023)),
            ("IEEE Transactions on Signal Processing, Vol. 67, No. 11, June 1, 2019", "journal-ref",
             ("IEEE Transactions on Signal Processing", "journal", "other", "published", 2019)),
            ("Quantitative Finance, 2020", "journal-ref", ("Quantitative Finance", "journal", "interdisciplinary", "published", 2020)),
            ("35 pages, 26 figures, ICLR 2025", "comment", ("ICLR", "conference", "cs", "accepted", 2025)),
            ("North American Actuarial Journal 24(4)", "journal-ref", ("North American Actuarial Journal", "journal", "finance-econ", "published", None)),
        ]
        for text, source, want in cases:
            v = V.detect_venue(text, source)
            self.assertEqual((v["name"], v["kind"], v["discipline"], v["status"], v["year"]), want, text)

    def test_no_venue(self):
        for text in ["12 pages, 5 figures", "Code at https://www.github.com/x", ""]:
            self.assertIsNone(V.detect_venue(text, "comment"), text)

    def test_unknown_venue_is_kept_for_review(self):
        v = V.detect_venue("Accepted to the 2nd Workshop on LLMs for Finance", "comment")
        self.assertIsNone(v["id"])
        self.assertEqual((v["kind"], v["discipline"]), ("workshop", "unknown"))

    def test_discipline_from_venue_then_team(self):
        p = {"relevance": 3, "venue_mention": "ICLR 2025", "affiliation_raw": ["Department of Finance, X University"]}
        V.classify_paper(p)
        self.assertEqual((p["discipline"], p["discipline_basis"], p["team_background"]), ("cs", "venue", "finance-econ"))
        p = {"relevance": 3, "affiliation_raw": ["School of Computer Science, A", "Business School, B"]}
        V.classify_paper(p)
        self.assertEqual((p["discipline"], p["discipline_basis"], p["team_background"]), ("interdisciplinary", "team", "mixed"))
        p = {"relevance": 2, "institutions": [{"name": "Mathematical Institute"}]}
        V.classify_paper(p)
        self.assertEqual((p["discipline"], p["discipline_basis"]), ("unknown", "none"))

    def test_report_skips_unscored(self):
        report = V.classify_all([{"relevance": 2, "venue_mention": "KDD 2026"}, {"title": "old"}])
        self.assertEqual((report["papers"], report["with_venue"]), (1, 1))


if __name__ == "__main__":
    unittest.main()
