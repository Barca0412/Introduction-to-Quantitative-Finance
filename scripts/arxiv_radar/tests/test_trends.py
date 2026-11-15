"""S8 aggregates (trends.py).

    python3 -m unittest scripts.arxiv_radar.tests.test_trends -v
"""

import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from scripts.arxiv_radar import trends


def paper(pid, day, kws=(), domains=("trading",), insts=(), rel=3):
    return {"id": pid, "published_date": day, "relevance": rel, "finance_domains": list(domains), "methods": ["llm"],
            "keywords_norm": [{"id": k, "en": k, "zh": k + "中", "new": False} for k in kws],
            "institutions": [{"name": n, "ror": "", "type": "education"} for n in insts],
            "authors": [{"name": "Ana Lee"}], "reproducibility": {"code": pid.endswith("c")}}


class TrendsTest(unittest.TestCase):
    def test_week_of(self):
        self.assertEqual(trends.week_of("2026-11-15"), "2026-11-09")  # Sunday -> its Monday
        self.assertEqual(trends.week_of("2026-11-16"), "2026-11-16")

    def test_rising_rule(self):
        weeks = ["w1", "w2", "w3", "w4", "w5"]
        weekly = {w: trends.Counter() for w in weeks}
        for w in weeks[:4]:
            weekly[w]["steady"] = 3
            weekly[w]["grow"] = 1
        weekly["w5"].update({"steady": 3, "grow": 6, "brandnew": 3, "small": 2})
        out = {r["id"]: r for r in trends.rising(weekly, weeks, {})}
        self.assertNotIn("steady", out)
        self.assertNotIn("small", out)  # n < 3
        self.assertEqual(out["grow"]["rise"], round((6 - 1) / 2 ** 0.5, 2))
        self.assertTrue(out["brandnew"]["new"])

    def test_build_writes_files_and_respects_since(self):
        papers = [
            paper("old", "2025-06-01", ["llm-agent"]),  # before TRENDS_SINCE: ignored
            paper("a", "2026-11-03", ["llm-agent", "backtesting"], insts=["Tsinghua University"]),
            paper("bc", "2026-11-12", ["llm-agent"], insts=["Tsinghua University"]),
            paper("c", "2026-11-13", ["backtesting"], domains=("asset-pricing",), rel=2),
        ]
        with tempfile.TemporaryDirectory() as tmp, mock.patch.object(trends, "TRENDS_SINCE", "2026-11-01"):
            out = Path(tmp)
            summary = trends.build(papers, out)
            kw = json.loads((out / "weekly_keywords.json").read_text())
            topic = json.loads((out / "topic" / "trading.json").read_text())
            key = json.loads((out / "keyword" / "llm-agent.json").read_text())
            inst = json.loads((out / "weekly_institutions.json").read_text())
        self.assertEqual(summary["papers"], 3)
        self.assertEqual(summary["since"], "2026-11-02")  # first whole week after 2026-11-01 (a Sunday)
        self.assertEqual(kw["weeks"], ["2026-11-02", "2026-11-09"])
        self.assertEqual(kw["keywords"]["llm-agent"]["counts"], [1, 1])
        self.assertEqual(topic["counts"], [1, 1])
        self.assertEqual(key["representative"][0], "bc")  # newer and has code
        self.assertEqual(key["keywords"][0]["id"], "backtesting")
        self.assertEqual(inst["institutions"]["Tsinghua University"]["counts"], [1, 1])

    def test_empty(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(trends.build([], Path(tmp))["papers"], 0)
            self.assertTrue((Path(tmp) / "rising.json").exists())


if __name__ == "__main__":
    unittest.main()
