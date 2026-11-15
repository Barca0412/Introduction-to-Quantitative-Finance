"""S9 weekly digest: facts and the draft checks (no LLM).

    python3 -m unittest scripts.arxiv_radar.tests.test_digest -v
"""

import unittest
from datetime import date
from unittest import mock

from scripts.arxiv_radar import digest


def paper(pid, day, domain="trading", rel=3):
    return {"id": pid, "title": f"Paper {pid}", "published_date": day, "relevance": rel, "methods": ["llm"],
            "finance_domains": [domain], "tldr_zh": "一句话。", "points_zh": {}, "abs_link": f"https://arxiv.org/abs/{pid}"}


class DigestTest(unittest.TestCase):
    papers = [paper("2611.00001", "2026-11-03"), paper("2611.00002", "2026-11-04", "credit-banking"),
              paper("2611.00003", "2026-11-05", rel=2), paper("2611.00009", "2026-11-11")]

    def test_last_complete_week(self):
        self.assertEqual(digest.last_complete_week(date(2026, 11, 15)), "2026-11-02")  # Sunday: that week is still running
        self.assertEqual(digest.last_complete_week(date(2026, 11, 16)), "2026-11-09")

    def test_facts(self):
        with mock.patch.object(digest, "TRENDS_SINCE", "2026-11-01"):
            facts = digest.collect_facts(self.papers, "2026-11-02")
        self.assertEqual((facts["papers"], facts["core_papers"], facts["history_weeks"]), (3, 2, 0))
        self.assertEqual(facts["domains"], {"交易与执行": 2, "信用、银行与支付": 1})
        self.assertEqual(facts["candidates"]["交易与执行"][0]["link"], "https://arxiv.org/abs/2611.00001")

    def test_check_draft(self):
        with mock.patch.object(digest, "TRENDS_SINCE", "2026-11-01"):
            facts = digest.collect_facts(self.papers, "2026-11-02")
        good = "## 本周概况\n本周 3 篇。\n## 本周必读\n### [Paper 2611.00001](https://arxiv.org/abs/2611.00001)\n"
        self.assertEqual(digest.check_draft(good, facts), [])
        bad = good + "另有 [别的](https://example.com/x) 和 99 篇。"
        problems = digest.check_draft(bad, facts)
        self.assertTrue(any("unknown link" in p for p in problems))
        self.assertTrue(any("99" in p for p in problems))
        self.assertIn("missing section 本周必读", digest.check_draft("## 本周概况", facts))


if __name__ == "__main__":
    unittest.main()


class WhoFactsTest(unittest.TestCase):
    def test_who_facts_runs_on_real_shaped_papers(self):
        from scripts.arxiv_radar.digest import who_facts
        inst = {"ror": "027m9bs27", "name": "The University of Manchester", "zh": "曼彻斯特大学",
                "type": "education", "country": "GB"}
        papers = [{"id": str(i), "published_date": "2026-11-03", "relevance": 3, "authors": [{"name": "Jimin Huang"}],
                   "author_ids": [{"openalex": "A1"}], "institutions": [inst], "author_affiliations": [[0]]}
                  for i in range(2)]
        who = who_facts(papers)
        self.assertEqual(who["institutions"][0], {"name": "曼彻斯特大学", "type": "高校", "n": 2})
        self.assertEqual(who["authors_with_2_or_more"][0]["institution"], "曼彻斯特大学")


class DigestLayoutTest(unittest.TestCase):
    FACTS = {
        "papers": 3,
        "who": {"institutions": [{"name": "南洋理工大学", "type": "高校", "n": 2}],
                "countries": [{"name": "新加坡", "n": 2}],
                "collaboration": {"只有高校": 2, "校企合作": 0, "只有企业": 0, "其他类型机构": 0, "未查到机构": 1},
                "cross_country_papers": 0},
        "candidates": {"交易与执行": [{
            "title": "StockASkill: A Local-First AgentSkill for Intelligent Stock Selection",
            "link": "https://arxiv.org/abs/2611.09528", "short": "StockASkill",
            "authors": ["A One", "B Two", "C Three", "D Four"], "institutions": ["南洋理工大学"]}]},
    }

    def test_short_name(self):
        from scripts.arxiv_radar.digest import short_name
        self.assertEqual(short_name("StockASkill: A Local-First AgentSkill"), "StockASkill")
        self.assertEqual(short_name("A title without a colon"), "")

    def test_finish_adds_chart_and_byline(self):
        from scripts.arxiv_radar.digest import finish
        body = "## 谁在做\n\n一句结论。\n\n## 本周必读\n\n### [StockASkill: A Local-First AgentSkill for Intelligent Stock Selection](https://arxiv.org/abs/2611.09528)\n\n正文。"
        out = finish(body, self.FACTS)
        svg = next(line for line in out.splitlines() if line.startswith("<svg"))
        self.assertIn("南洋理工大学", svg)
        self.assertIn("未查到机构 1", svg)
        self.assertNotIn("\n", svg)  # one line: Markdown keeps it as one HTML block
        self.assertIn("<small>作者：A One、B Two、C Three 等 4 人　·　机构：南洋理工大学</small>", out)

    def test_full_title_in_directions_is_rejected(self):
        from scripts.arxiv_radar.digest import check_draft
        facts = {**self.FACTS, "papers_previous_week": None, "core_papers": 1, "domains": {}, "methods": {}}
        long = "## 值得关注的方向\n\n见 [StockASkill: A Local-First AgentSkill for Intelligent Stock Selection](https://arxiv.org/abs/2611.09528)。\n\n## 本周必读\n"
        short = long.replace("[StockASkill: A Local-First AgentSkill for Intelligent Stock Selection]", "[StockASkill]")
        self.assertTrue(any("full title" in p for p in check_draft(long, facts)))
        self.assertFalse(any("full title" in p for p in check_draft(short, facts)))
