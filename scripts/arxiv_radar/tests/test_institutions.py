"""S6 authors and institutions: arXiv HTML parsing, OpenAlex parsing, merging.

    python3 -m unittest scripts.arxiv_radar.tests.test_institutions -v

No network. The HTML snippets copy the three LaTeXML layouts seen in November 2026.
"""

from __future__ import annotations

import unittest
from datetime import date

from scripts.arxiv_radar import institutions as inst
from scripts.arxiv_radar.storage import normalize_paper

# acmart: one ltx_contact per affiliation, city/country tagged separately.
HTML_ACM = """<div class="ltx_authors">
<span class="ltx_creator ltx_role_author"><span class="ltx_personname">Bingdian Zhang</span>
<span class="ltx_author_notes"><span class="ltx_author_notes_content">
<span class="ltx_contact ltx_role_affiliation"><span class="ltx_contact_name">Affiliation: </span>
<span class="ltx_text ltx_affiliation_institution">Institute of Computing Technology, Chinese Academy of Sciences</span>,
<span class="ltx_text ltx_affiliation_city">Beijing</span>, <span class="ltx_text ltx_affiliation_country">China</span></span>
<span class="ltx_contact ltx_role_email"><span class="ltx_contact_name">email: </span><a href="mailto:z@ict.ac.cn">z@ict.ac.cn</a></span>
</span></span></span>
<span class="ltx_author_before"> </span>
<span class="ltx_creator ltx_role_author"><span class="ltx_personname">Xueqi Cheng</span>
<span class="ltx_author_notes"><span class="ltx_author_notes_content">
<span class="ltx_contact ltx_role_affiliation"><span class="ltx_text ltx_affiliation_institution">University of Chinese Academy of Sciences</span></span>
</span></span></span></div><div class="ltx_abstract">Abstract text</div>"""

# \\thanks{} footnote with an e-mail address.
HTML_THANKS = """<div class="ltx_authors">
<span class="ltx_creator ltx_role_author"><span class="ltx_personname">Bin Chen</span>
<span class="ltx_note ltx_role_thanks"><sup class="ltx_note_mark">†</sup><span class="ltx_note_outer"><span class="ltx_note_content">
<sup class="ltx_note_mark">†</sup><span class="ltx_note_type">thanks: </span>University of Rochester. Email: binchen@rochester.edu</span></span></span></span>
</div>"""

# Plain article class: affiliation lines after <br> inside the person name.
HTML_BR = """<div class="ltx_authors">
<span class="ltx_creator ltx_role_author"><span class="ltx_personname">Ana Lee<br class="ltx_break"/>Department of Mathematics &amp; Statistics<br class="ltx_break"/>Texas Tech University<br class="ltx_break"/>Lubbock, TX 79409, USA</span></span>
<span class="ltx_creator ltx_role_author"><span class="ltx_personname">Tom Wu<br class="ltx_break"/>Carey Business School, Johns Hopkins University, Baltimore</span></span>
</div>"""

HTML_NONE = """<div class="ltx_authors"><span class="ltx_creator ltx_role_author"><span class="ltx_personname">Yuxuan Gu</span></span></div>"""


def openalex_work(*authors):
    return {"authorships": [
        {"author": {"display_name": name},
         "institutions": [{"display_name": i, "ror": f"https://ror.org/{i[:3].lower()}x", "country_code": "CN", "type": "education"} for i in insts],
         "raw_affiliation_strings": [f"Department of X, {i}" for i in insts]}
        for name, insts in authors
    ]}


class HtmlParseTest(unittest.TestCase):
    def test_acmart_layout(self):
        authors = inst.parse_arxiv_html(HTML_ACM)
        self.assertEqual([a["name"] for a in authors], ["Bingdian Zhang", "Xueqi Cheng"])
        self.assertEqual(authors[0]["institutions"], ["Institute of Computing Technology"])
        self.assertEqual(authors[1]["institutions"], ["University of Chinese Academy of Sciences"])

    def test_thanks_footnote_drops_email(self):
        self.assertEqual(inst.parse_arxiv_html(HTML_THANKS)[0]["institutions"], ["University of Rochester"])

    def test_br_layout_prefers_university_and_drops_address(self):
        authors = inst.parse_arxiv_html(HTML_BR)
        self.assertEqual(authors[0]["name"], "Ana Lee")
        self.assertEqual(authors[0]["institutions"], ["Texas Tech University"])
        self.assertEqual(authors[1]["institutions"], ["Johns Hopkins University"])
        self.assertIn("Department of Mathematics & Statistics", authors[0]["raw"])  # kept for team background

    def test_no_affiliation_in_page(self):
        self.assertEqual(inst.parse_arxiv_html(HTML_NONE), [{"name": "Yuxuan Gu", "institutions": [], "raw": []}])

    def test_cleanup_cases(self):
        cases = {
            "Nixtla, San Francisco, CA, United States": ["Nixtla"],
            "This work was done while the author was at Circle Research": ["Circle Research"],
            "Department of Finance": ["Department of Finance"],  # better than nothing
            "Ltd": [],
            "V. Acharya is an Independent Researcher": [],
        }
        for raw, want in cases.items():
            self.assertEqual(inst.split_raw_affiliations(raw), want, raw)


class CombineTest(unittest.TestCase):
    paper = {"id": "2611.00001", "authors": [{"name": "Wang Hao"}, {"name": "Li Na"}, {"name": "Tom Wu"}],
             "relevance": 2, "published_date": "2026-11-10"}

    def test_openalex_first_html_fills_gaps(self):
        openalex = inst.parse_openalex(openalex_work(("Hao Wang", ["Tsinghua University"]), ("Na Li", []), ("Tom Wu", ["Tsinghua University"])))
        html = [{"name": "Hao Wang", "institutions": ["Wrong U"], "raw": []},
                {"name": "Na Li", "institutions": ["Ant Group"], "raw": ["Ant Group, Hangzhou"]},
                {"name": "Tom Wu", "institutions": [], "raw": []}]
        out = inst.combine(self.paper, openalex, html)
        self.assertEqual([i["name"] for i in out["institutions"]], ["Tsinghua University", "Ant Group"])
        self.assertEqual(out["author_affiliations"], [[0], [1], [0]])  # same institution shared, not duplicated
        self.assertEqual(out["institutions"][0]["source"], "openalex")
        self.assertEqual(out["institutions"][1]["confidence"], "medium")
        self.assertEqual(out["affiliation_source"], "openalex+html")
        self.assertIn("Ant Group, Hangzhou", out["affiliation_raw"])

    def test_nothing_found(self):
        out = inst.combine(self.paper, [], None)
        self.assertEqual(out["affiliation_source"], "none")
        self.assertEqual(out["author_affiliations"], [[], [], []])

    def test_name_matching(self):
        self.assertTrue(inst.names_match("Hao Wang", "Wang Hao"))
        self.assertTrue(inst.names_match("J. Smith", "John Smith"))
        self.assertTrue(inst.names_match("José Núñez", "Jose Nunez"))
        self.assertFalse(inst.names_match("Hao Wang", "Hao Li"))

    def test_storage_keeps_names_with_commas(self):
        out = inst.combine(self.paper, inst.parse_openalex(openalex_work(
            ("Hao Wang", ["Agency for Science, Technology and Research"]))), None)
        paper = normalize_paper({**self.paper, **out, "title": "t", "abstract": "a"})
        self.assertEqual(paper["affiliations"], ["Agency for Science, Technology and Research"])
        self.assertEqual(paper["author_affiliations"][0], [0])


class NeedsLookupTest(unittest.TestCase):
    today = date(2026, 11, 20)

    def paper(self, **kw):
        return {"relevance": 2, "published_date": "2026-11-15", **kw}

    def test_rules(self):
        self.assertTrue(inst.needs_lookup(self.paper(), self.today))
        self.assertFalse(inst.needs_lookup(self.paper(relevance=0), self.today))
        self.assertFalse(inst.needs_lookup({"published_date": "2026-11-15"}, self.today))  # never scored
        complete = self.paper(affiliation_checked_at="2026-11-16", affiliation_source="openalex", author_affiliations=[[0], [1]])
        self.assertFalse(inst.needs_lookup(complete, self.today))
        partial = self.paper(affiliation_checked_at="2026-11-16", affiliation_source="html", author_affiliations=[[0], []])
        self.assertTrue(inst.needs_lookup(partial, self.today))  # young: ask OpenAlex again
        self.assertFalse(inst.needs_lookup(partial, date(2026, 12, 20)))  # older than 14 days: stop
        self.assertFalse(inst.needs_lookup({**partial, "affiliation_checked_at": "2026-11-20"}, self.today))  # once a day


if __name__ == "__main__":
    unittest.main()
