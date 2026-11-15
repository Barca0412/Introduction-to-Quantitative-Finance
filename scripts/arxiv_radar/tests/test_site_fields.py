"""Site data carries the S3 v2 / P2 fields the redesigned radar pages read.

    python3 -m unittest scripts.arxiv_radar.tests.test_site_fields -v
"""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from scripts.arxiv_radar import build_site_data as bsd
from scripts.arxiv_radar import enrich
from scripts.arxiv_radar.compute_stats import build_stats, compute_facet_stats
from scripts.arxiv_radar.tests.test_restore import RadarSandbox, make_papers


def enriched(index: int = 0, **changes):
    paper = make_papers(1)[0]
    paper.update({
        "id": f"2611.1{index:04d}",
        "published_date": "2026-11-10",
        "relevance": 3,
        "relevance_reason_zh": "核心是因子挖掘。",
        "paper_type": "method",
        "task_types": ["signal-mining", "forecasting"],
        "finance_domains": ["asset-pricing"],
        "methods": ["llm-agent"],
        "data_market": ["a-share"],
        "tldr_zh": "用多智能体挖因子。",
        "points_zh": {"problem": "问题。", "method": "方法。", "result": "结果。", "limitation": "摘要未说明"},
        "keywords_norm": [
            {"id": "alpha-factor-mining", "en": "alpha factor mining", "zh": "因子挖掘", "kind": "finance", "raw": "alpha mining", "new": False},
            {"id": "new-term", "en": "new term", "zh": "", "kind": "tech", "raw": "new term", "new": True},
        ],
        "venue": {"id": "kdd", "name": "KDD", "kind": "conference", "discipline": "cs", "status": "accepted", "year": 2026},
        "venue_mention": "Accepted by KDD 2026",
        "discipline": "cs",
        "reproducibility": {"code": True, "data_public": None},
        "institutions": [{"name": "Tsinghua University", "ror": "x", "country": "CN", "type": "education", "source": "openalex"}],
        "author_affiliations": [[0]],
    })
    paper.update(changes)
    return paper


class ListFieldsTest(unittest.TestCase):
    def test_slim_record_has_the_new_fields(self):
        record, _ = bsd.slim_paper(enriched())
        self.assertEqual(record["r"], 3)
        self.assertEqual(record["pt"], "method")
        self.assertEqual(record["tt"], ["signal-mining", "forecasting"])
        self.assertEqual(record["fd"], ["asset-pricing"])
        self.assertEqual(record["m"], ["llm-agent"])
        self.assertEqual(record["dm"], ["a-share"])
        self.assertEqual(record["tl"], "用多智能体挖因子。")
        self.assertEqual(record["kn"], [["alpha-factor-mining", "因子挖掘", "f"], ["new-term", "new term", "t"]])
        self.assertEqual(record["v"], {"n": "KDD", "k": "conference", "s": "accepted", "y": 2026})
        self.assertNotIn("vm", record)
        self.assertEqual(record["ds"], "cs")
        self.assertEqual(record["cd"], 1)
        for key in record:
            self.assertIn(key, bsd.SCHEMA, key)

    def test_empty_values_are_left_out(self):
        record, _ = bsd.slim_paper(enriched(
            data_market=["none"], venue=None, venue_mention="NeurIPS workshop on X", discipline="unknown",
            reproducibility={"code": None}, keywords_norm=[],
        ))
        for key in ("dm", "v", "ds", "cd", "kn"):
            self.assertNotIn(key, record)
        self.assertEqual(record["vm"], "NeurIPS workshop on X")

    def test_paper_not_on_arxiv_keeps_its_own_link(self):
        paper = enriched(
            id="doi:10.1145/3711896.3737000", abs_link="https://doi.org/10.1145/3711896.3737000", pdf_link="",
            venue={"id": "kdd", "name": "KDD", "kind": "conference", "discipline": "cs", "status": "accepted",
                   "year": 2026, "source": "venue_list", "text": "ADS, oral"},
        )
        record, _ = bsd.slim_paper(paper)
        self.assertEqual(record["u"], "https://doi.org/10.1145/3711896.3737000")
        self.assertEqual(record["v"], {"n": "KDD", "k": "conference", "s": "accepted", "y": 2026, "o": 1, "t": "ADS, oral"})
        self.assertEqual(record["r"], 3)
        arxiv_record, _ = bsd.slim_paper(enriched())
        self.assertEqual(arxiv_record["u"], "https://arxiv.org/abs/2611.10000")
        self.assertEqual(arxiv_record["ar"], 1)
        self.assertNotIn("o", arxiv_record["v"])

    def test_old_format_paper_gets_no_v2_keys(self):
        record, _ = bsd.slim_paper(make_papers(1)[0])
        self.assertFalse({"r", "pt", "tt", "fd", "m", "tl"} & set(record))

    def test_detail(self):
        detail = bsd.paper_detail(enriched())
        self.assertEqual(detail["pz"]["problem"], "问题。")
        self.assertEqual(detail["rr"], "核心是因子挖掘。")
        self.assertEqual(detail["ins"], [{"n": "Tsinghua University", "c": "CN", "t": "education"}])
        self.assertEqual(detail["aa"], [[0]])
        self.assertEqual(bsd.paper_detail(make_papers(1)[0]), {})
        for key in detail:
            self.assertIn(key, bsd.DETAIL_SCHEMA)


class TaxonomyFileTest(unittest.TestCase):
    def test_every_id_has_a_chinese_name(self):
        tax = bsd.site_taxonomy()
        for key in ("paper_types", "task_types", "finance_domains", "methods", "data_markets"):
            self.assertEqual([item["id"] for item in tax[key]], enrich.ids(key))
            self.assertTrue(all(item["zh"] for item in tax[key]))
        self.assertEqual(tax["relevance"]["3"], "核心")


class FacetStatsTest(unittest.TestCase):
    def test_counts_series_and_grid(self):
        papers = [
            enriched(0),                                                         # Tue 11-10
            enriched(1, published_date="2026-11-09", relevance=2, finance_domains=["trading", "asset-pricing"],
                     task_types=["decision"], methods=["rl"]),                  # Mon 11-09, same week
            enriched(2, published_date="2026-11-01", paper_type="benchmark"),   # Sun 11-01, week of 10-26
            make_papers(1)[0],                                                   # old format: not counted
        ]
        facets = compute_facet_stats(papers)
        self.assertEqual(facets["papers"], 3)
        self.assertEqual(facets["dates"], ["2026-11-01", "2026-11-09", "2026-11-10"])
        self.assertEqual(facets["weeks"], ["2026-10-26", "2026-11-09"])
        self.assertEqual(facets["total"], {"daily": [1, 1, 1], "weekly": [1, 2]})
        self.assertEqual(facets["core"], {"daily": [1, 0, 1], "weekly": [1, 1]})
        domains = facets["dims"]["finance_domains"]
        self.assertEqual(domains["total"], {"asset-pricing": 3, "trading": 1})
        self.assertEqual(domains["weekly"]["asset-pricing"], [1, 2])
        self.assertEqual(facets["dims"]["paper_types"]["total"], {"method": 2, "benchmark": 1})
        grid = facets["grid"]
        self.assertEqual(grid["rows"], enrich.ids("finance_domains"))
        self.assertEqual(grid["cols"], enrich.ids("task_types"))
        row = grid["cells"][grid["rows"].index("asset-pricing")]
        self.assertEqual(row[grid["cols"].index("signal-mining")], 2)
        self.assertEqual(row[grid["cols"].index("decision")], 1)
        self.assertEqual(sum(map(sum, grid["cells"])), 2 + 2 + 2)

    def test_build_stats_includes_facets(self):
        self.assertEqual(build_stats([enriched()])["facets"]["papers"], 1)


class BuildTest(unittest.TestCase):
    def test_build_writes_details_and_taxonomy(self):
        with tempfile.TemporaryDirectory() as tmp:
            box = RadarSandbox(Path(tmp))
            papers = [enriched(i) for i in range(3)] + make_papers(2)
            (box.data / "papers.json").write_text(json.dumps({"papers": papers}), encoding="utf-8")
            with box.patched():
                manifest = bsd.build()
            self.assertEqual(manifest["total_papers"], 3)
            self.assertEqual(manifest["taxonomy"]["file"], "taxonomy.json")
            self.assertTrue((box.site / "taxonomy.json").exists())
            records = json.loads((box.site / manifest["recent"]["papers"][0]["file"]).read_text())["papers"]
            details = json.loads((box.site / manifest["recent"]["details"][0]["file"]).read_text())
            self.assertEqual({r["dc"] for r in records}, {0})
            self.assertEqual(set(details), {r["id"] for r in records})
            stats = json.loads((box.site / "stats.json").read_text())
            self.assertEqual(stats["facets"]["papers"], 3)

    def test_public_export_has_no_abstracts_and_uses_resolved_identity(self):
        with tempfile.TemporaryDirectory() as tmp:
            box = RadarSandbox(Path(tmp))
            papers = [enriched(i, abstract="INTERNAL ABSTRACT SENTINEL " * 100,
                               authors=[{"name": "Wei Zhang", "email": "private@example.invalid"}],
                               author_ids=[{"openalex": "A1"}]) for i in range(2)]
            papers += [enriched(2, published_date="2025-01-01", authors=[{"name": "Wei Zhang"}],
                                author_ids=[{"openalex": "A2"}], institutions=[], author_affiliations=[])]
            (box.data / "papers.json").write_text(json.dumps({"papers": papers}), encoding="utf-8")
            with box.patched():
                manifest = bsd.build()
            self.assertEqual(manifest["version"], 3)
            self.assertIn("leaders", manifest["agg"])
            self.assertNotIn("abstracts", manifest["recent"])
            self.assertFalse(list(box.site.rglob("abstracts-*.json")))
            for path in box.site.rglob("*.json"):
                text = path.read_text()
                self.assertNotIn("INTERNAL ABSTRACT SENTINEL", text)
                self.assertNotIn("private@example.invalid", text)
            records = json.loads((box.site / manifest["recent"]["papers"][0]["file"]).read_text())["papers"]
            self.assertTrue(all("s" not in r and "ac" not in r for r in records))
            details = json.loads((box.site / manifest["recent"]["details"][0]["file"]).read_text())
            self.assertEqual(details[papers[0]["id"]]["au"], [{"id": "A1", "n": "Wei Zhang", "page": "a1"}])
            index = json.loads((box.site / manifest["paper_index"]["file"]).read_text())
            self.assertEqual(index[papers[2]["id"]], "archive/2025-01")
            leaders = json.loads((box.site / "agg/leaders.json").read_text())
            authors = {a["id"]: a for a in leaders["periods"]["all"]["authors"]}
            self.assertEqual(authors["A1"]["page"], "a1")
            self.assertEqual(authors["A2"]["page"], "")

    def test_non_arxiv_link_and_absent_pdf_never_become_arxiv_urls(self):
        for paper_id, url in (("nber:w35987", "https://www.nber.org/papers/w35987"),
                              ("venue:kdd-2026-paper", "https://kdd.org/paper")):
            record, abstract = bsd.slim_paper(enriched(id=paper_id, abs_link=url, pdf_link=""))
            self.assertEqual(record["u"], url)
            self.assertEqual(record["p"], "")
            self.assertEqual(record["ar"], 0)
            self.assertIsNone(abstract)


if __name__ == "__main__":
    unittest.main()
