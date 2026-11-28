"""arXiv announcement calendar and the "arXiv paused" notice (arxiv_calendar.py).

    python3 -m unittest scripts.arxiv_radar.tests.test_arxiv_calendar -v
"""

import unittest
from datetime import datetime, timedelta, timezone

from scripts.arxiv_radar import arxiv_calendar as C


def utc(text):
    return datetime.fromisoformat(text).replace(tzinfo=timezone.utc)


def status_at(text, data_age_hours=1):
    now = utc(text)
    return C.announcement_status(now, now - timedelta(hours=data_age_hours))


class CalendarFileTest(unittest.TestCase):
    def test_2026_list_matches_the_arxiv_page(self):
        days = sorted(d.isoformat() for d in C.calendar()["holidays"])
        self.assertEqual(days, [
            "2026-01-01", "2026-01-19", "2026-06-19", "2026-07-03", "2026-09-07",
            "2026-10-12", "2026-11-11", "2026-11-26", "2026-12-25",
        ])
        self.assertIn(2026, C.calendar()["years"])
        self.assertEqual(C.calendar()["source_url"], "https://info.arxiv.org/help/availability.html")


class StatusTest(unittest.TestCase):
    def test_friday_after_thanksgiving(self):
        s = status_at("2026-11-27T12:00:00")
        self.assertEqual(s["level"], "holiday")
        self.assertEqual([(x["date"], x["reason"]) for x in s["skipped"]], [("2026-11-26", "holiday")])
        self.assertEqual(s["skipped"][0]["name_zh"], "美国感恩节")
        self.assertEqual(s["next_et"], "2026-11-29T20:00-05:00")
        self.assertEqual(s["next_bj"], "2026-11-30T09:00+08:00")
        self.assertEqual(
            s["notice_zh"],
            "11 月 26 日（周四）是美国感恩节，在 arXiv 官方的 2026 假期名单上，当天晚上那一期停发了。"
            "所以这一天没有新论文，不是本站出了问题。下一期预计北京时间 11 月 30 日（周一）上午发布，本站当天自动更新。",
        )
        self.assertIn(s["link_text_zh"], s["notice_zh"])
        self.assertIn("https://info.arxiv.org/help/availability.html", s["notice_en"])
        self.assertNotIn("calendar_missing_year", s)

    def test_saturday_after_thanksgiving_mentions_the_weekend_too(self):
        s = status_at("2026-11-28T12:00:00")
        self.assertEqual(s["level"], "holiday")
        self.assertEqual([(x["date"], x["reason"]) for x in s["skipped"]],
                         [("2026-11-27", "weekend"), ("2026-11-26", "holiday")])
        self.assertIn("美国感恩节", s["notice_zh"])
        self.assertIn("周五、周六 arXiv 本来不发新论文", s["notice_zh"])
        self.assertIn("所以这几天没有新论文", s["notice_zh"])
        self.assertEqual(s["short_zh"], "遇 arXiv 停发")

    def test_sunday_daytime_still_explains_thanksgiving(self):
        s = status_at("2026-11-29T12:00:00")
        self.assertEqual(s["level"], "holiday")
        self.assertEqual(len(s["skipped"]), 3)

    def test_monday_after_the_sunday_announcement_is_normal(self):
        self.assertIsNone(status_at("2026-11-30T12:00:00"))

    def test_plain_saturday_is_a_weekend_notice(self):
        s = status_at("2026-11-21T12:00:00")
        self.assertEqual(s["level"], "weekend")
        self.assertEqual([(x["date"], x["reason"]) for x in s["skipped"]], [("2026-11-20", "weekend")])
        self.assertEqual(s["short_zh"], "arXiv 周五、周六不发新论文")
        self.assertEqual(s["next_et"], "2026-11-22T20:00-05:00")

    def test_friday_is_normal_because_thursday_announced(self):
        self.assertIsNone(status_at("2026-11-20T12:00:00"))

    def test_ordinary_wednesday(self):
        self.assertIsNone(status_at("2026-11-18T12:00:00"))

    def test_monday_holiday_in_daylight_saving_time(self):
        s = status_at("2026-10-13T12:00:00")
        self.assertEqual(s["level"], "holiday")
        self.assertEqual(s["skipped"][0]["date"], "2026-10-12")
        self.assertEqual(s["next_et"], "2026-10-13T20:00-04:00")
        self.assertEqual(s["next_bj"], "2026-10-14T08:00+08:00")

    def test_before_and_after_eight_pm_eastern(self):
        # 2026-11-27 00:30 UTC = 26 Nov 19:30 EST: Wednesday announced, Thanksgiving evening not yet due.
        self.assertIsNone(status_at("2026-11-27T00:30:00"))
        # 01:30 UTC = 20:30 EST on Thanksgiving: that evening was skipped.
        self.assertEqual(status_at("2026-11-27T01:30:00")["level"], "holiday")

    def test_daylight_saving_switch_weekend(self):
        # DST ended on Sunday 2026-11-01; Saturday 31 Oct is a weekend evening.
        s = status_at("2026-11-01T12:00:00")
        self.assertEqual(s["level"], "weekend")
        self.assertEqual(s["next_et"], "2026-11-01T20:00-05:00")

    def test_stale_data_shows_nothing(self):
        self.assertIsNone(status_at("2026-11-27T12:00:00", data_age_hours=72))
        self.assertIsNone(C.announcement_status(utc("2026-11-27T12:00:00"), None))

    def test_naive_timestamps_from_the_pipeline_are_utc(self):
        s = C.announcement_status("2026-11-27T12:30:00+00:00", "2026-11-27T12:11:23.552198")
        self.assertEqual(s["level"], "holiday")

    def test_missing_year_is_flagged_and_never_claims_a_holiday(self):
        with self.assertLogs(C.logger, level="WARNING"):
            s = status_at("2027-01-02T12:00:00")  # Saturday
        self.assertEqual(s["level"], "weekend")
        self.assertEqual(s["calendar_missing_year"], [2027])

    def test_deferred_mailing(self):
        cal = C.calendar()
        day = datetime(2026, 11, 18).date()
        cal["deferred"][day] = {"date": day, "reason_zh": "系统维护", "reason_en": "maintenance"}
        try:
            s = status_at("2026-11-19T12:00:00")
        finally:
            del cal["deferred"][day]
        self.assertEqual(s["level"], "holiday")
        self.assertEqual(s["skipped"][0]["reason"], "deferred")
        self.assertIn("arXiv 临时停发了一期（系统维护）", s["notice_zh"])


if __name__ == "__main__":
    unittest.main()
