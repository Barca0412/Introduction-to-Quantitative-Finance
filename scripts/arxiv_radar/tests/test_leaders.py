import json
import tempfile
import unittest
from pathlib import Path

from scripts.arxiv_radar import leaders


def paper(pid, day, authors, ids, insts, affs, rel=2):
    return {"id": pid, "published_date": day, "relevance": rel, "authors": authors, "author_ids": ids,
            "institutions": insts, "author_affiliations": affs,
            "finance_domains": ["asset_pricing"], "methods": ["llm"]}


NTU = {"ror": "02e7b5302", "name": "Nanyang Technological University", "zh": "南洋理工大学",
       "type": "education", "country": "SG"}
ANT = {"ror": "00g5w7n47", "name": "Ant Group", "zh": "蚂蚁集团", "type": "company", "country": "CN"}


class LeadersTest(unittest.TestCase):
    def build(self, papers):
        out = Path(tempfile.mkdtemp())
        info = leaders.build(papers, out)
        return out, info, json.loads((out / "leaders.json").read_text())

    def test_same_name_different_people_stay_apart(self):
        papers = [
            paper("1", "2026-11-10", ["Wei Zhang"], [{"openalex": "A1"}], [NTU], [[0]]),
            paper("2", "2026-11-11", ["Wei Zhang"], [{"openalex": "A2"}], [ANT], [[0]]),
        ]
        _, _, data = self.build(papers)
        authors = data["periods"]["all"]["authors"]
        self.assertEqual(len(authors), 2)
        self.assertEqual({a["institution"] for a in authors}, {"南洋理工大学", "蚂蚁集团"})

    def test_split_openalex_ids_joined_by_orcid_or_email(self):
        papers = [
            paper("1", "2026-11-10", ["Li Na"], [{"openalex": "A1", "orcid": "0000-1"}], [NTU], [[0]]),
            paper("2", "2026-11-11", ["Na Li"], [{"openalex": "A9", "orcid": "0000-1"}], [NTU], [[0]]),
            paper("3", "2026-11-12", ["N. Li"], [{"email_hash": "abc"}, ], [NTU], [[0]]),
            paper("4", "2026-11-12", ["Li Na"], [{"openalex": "A9", "email_hash": "abc"}], [NTU], [[0]]),
        ]
        out, info, data = self.build(papers)
        authors = data["periods"]["all"]["authors"]
        self.assertEqual(len(authors), 1)
        self.assertEqual(authors[0]["n"], 4)
        self.assertEqual(info["details"]["author"], 1)
        page = json.loads(next((out / "author").iterdir()).read_text())
        self.assertTrue(page["id"].startswith("A"))
        self.assertEqual(len(page["papers"]), 4)

    def test_fresh_openalex_ids_joined_by_shared_coauthor_not_by_name_alone(self):
        papers = [
            paper("1", "2026-11-10", ["Jimin Huang", "Xueqing Peng"], [{"openalex": "A1"}, {"openalex": "A7"}], [], []),
            paper("2", "2026-11-11", ["Jimin Huang", "Xueqing Peng"], [{"openalex": "A2"}, {"openalex": "A8"}], [], []),
            paper("3", "2026-11-12", ["Jimin Huang"], [{"openalex": "A3"}], [ANT], [[0]]),  # nothing shared
            paper("4", "2026-11-12", ["Jimin Huang"], [{"openalex": "A4", "orcid": "0000-9"}], [NTU], [[0]]),
            paper("5", "2026-11-13", ["Jimin Huang"], [{"openalex": "A5", "orcid": "0000-8"}], [NTU], [[0]]),
        ]
        _, _, data = self.build(papers)
        counts = sorted(a["n"] for a in data["periods"]["all"]["authors"] if a["name"] == "Jimin Huang")
        # 1+2 joined (shared co-author); 3 alone; 4 and 5 share NTU but their ORCIDs differ.
        self.assertEqual(counts, [1, 1, 1, 2])

    def test_periods_companies_and_mix(self):
        papers = [
            paper("old", "2026-01-05", ["X"], [{}], [ANT], [[0]]),
            paper("new", "2026-11-12", ["Y", "Z"], [{}, {}], [NTU, ANT], [[0], [1]], rel=3),
        ]
        _, _, data = self.build(papers)
        self.assertEqual(data["periods"]["30d"]["papers"], 1)
        self.assertEqual(data["periods"]["all"]["papers"], 2)
        self.assertEqual(data["periods"]["all"]["companies"][0]["n"], 2)
        self.assertEqual(data["periods"]["30d"]["collaboration"]["mixed"], 1)
        self.assertEqual(data["periods"]["all"]["institutions"][0]["core"], 1)
        self.assertEqual({c["code"] for c in data["periods"]["all"]["countries"]}, {"CN", "SG"})


if __name__ == "__main__":
    unittest.main()
