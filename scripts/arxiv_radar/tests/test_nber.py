import unittest

from scripts.arxiv_radar import nber

PAGE = """<html><head>
<meta name="citation_title" content="AI and Asset Prices &amp; Returns">
<meta name="citation_author" content="Ann Lee">
<meta name="citation_author" content="Bo Wu">
<meta name="citation_publication_date" content="2026/11/09">
<meta name="citation_doi" content="10.3386/W35990">
<meta name="citation_technical_report_number" content="w35990">
</head><body>
<nav><a href="/programs-projects/programs-working-groups/labor-studies">Labor Studies</a></nav>
<div class="page-header__intro-inner">
  <p>We use <em>machine learning</em> to predict
  stock returns.</p></div>
<a href="/programs-projects/programs-working-groups/asset-pricing" class="x">Asset Pricing</a>
</body></html>"""


class NberTest(unittest.TestCase):
    def test_parse_page(self):
        page = nber.parse_page(PAGE)
        self.assertEqual(page["title"], "AI and Asset Prices & Returns")
        self.assertEqual(page["authors"], ["Ann Lee", "Bo Wu"])
        self.assertEqual(page["date"], "2026-11-09")
        self.assertEqual(page["doi"], "10.3386/w35990")
        self.assertEqual(page["abstract"], "We use machine learning to predict stock returns.")
        self.assertEqual(page["programs"], ["Asset Pricing"])  # the menu above the abstract is ignored

    def test_record_and_month(self):
        self.assertEqual(nber._month_start("November 2026"), "2026-11-01")
        self.assertIsNone(nber._month_start("soon"))
        rec = nber.to_record("w35990", nber.parse_page(PAGE), "2026-11-01")
        self.assertEqual(rec["id"], "nber:w35990")
        self.assertEqual(rec["source"], "nber")
        self.assertEqual(rec["pdf_link"], "")
        self.assertEqual(rec["journal_ref"], "NBER Working Paper w35990")

    def test_journal_ref_gives_working_paper_venue(self):
        from scripts.arxiv_radar.venues import detect_venue
        venue = detect_venue("NBER Working Paper w35990", "journal-ref")
        self.assertEqual(venue["id"], "nber")
        self.assertEqual(venue["status"], "working-paper")
        self.assertEqual(venue["discipline"], "finance-econ")


if __name__ == "__main__":
    unittest.main()
