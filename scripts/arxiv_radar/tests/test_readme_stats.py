"""Finance-domain counts for the README radar card (compute_stats.site_domain_counts).

    python3 -m unittest scripts.arxiv_radar.tests.test_readme_stats -v
"""

import unittest

from scripts.arxiv_radar.compute_stats import site_domain_counts


class SiteDomainCountsTest(unittest.TestCase):
    def test_most_first_ties_in_taxonomy_order(self):
        shown = [
            {"finance_domains": ["trading", "asset-pricing"]},
            {"finance_domains": ["trading"]},
            {"finance_domains": ["portfolio-risk", "portfolio-risk"]},  # counted once
            {"finance_domains": ["not-a-domain"]},                       # ignored
            {"finance_domains": None},
            {},
        ]
        self.assertEqual(site_domain_counts(shown), [
            {"id": "trading", "zh": "交易与执行", "papers": 2},
            {"id": "asset-pricing", "zh": "资产定价与因子", "papers": 1},
            {"id": "portfolio-risk", "zh": "组合与风险管理", "papers": 1},
        ])

    def test_empty(self):
        self.assertEqual(site_domain_counts([]), [])


if __name__ == "__main__":
    unittest.main()
