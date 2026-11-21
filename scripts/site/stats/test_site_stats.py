"""Tests for site_stats.py: python3 -m unittest scripts/site/stats/test_site_stats.py"""
import argparse
import json
import os
import sys
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import site_stats as ss  # noqa: E402

NOW = datetime(2026, 11, 21, 13, 0, 0, tzinfo=timezone.utc)  # 21:00 Beijing


def line(ua, path="/arxiv/papers", t="21/Nov/2026:20:58:00 +0800", ip="203.0.113.7", status=200):
    return f'{ip} - - [{t}] "GET {path} HTTP/1.1" {status} 512 "-" "{ua}"\n'


GPT = "Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko); compatible; GPTBot/1.1; +https://openai.com/gptbot"
CHATGPT_USER = "Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko); compatible; ChatGPT-User/1.0; +https://openai.com/bot"
EXA = "Mozilla/5.0 (compatible; ExaSearchBot/1.0; +https://crawler.exa.ai/)"
PERSON = "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_7_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0 Safari/537.36"
GOOGLE = "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)"


class ClassifyTest(unittest.TestCase):
    def test_names_and_kinds(self):
        self.assertEqual(ss.classify(GPT), ("GPTBot", "crawler"))
        self.assertEqual(ss.classify(CHATGPT_USER), ("ChatGPT-User", "user"))
        self.assertEqual(ss.classify(EXA), ("ExaSearchBot", "crawler"))
        self.assertEqual(ss.classify("claudebot"), ("ClaudeBot", "crawler"))
        self.assertIsNone(ss.classify(PERSON))
        self.assertIsNone(ss.classify(GOOGLE))  # plain search engines are not AI agents

    def test_static_files_and_bad_lines_skipped(self):
        self.assertIsNone(ss.parse_line(line(GPT, "/assets/app.4f2a.js")))
        self.assertIsNone(ss.parse_line(line(GPT, "/fonts/jost.woff2")))
        self.assertIsNone(ss.parse_line("garbage\n"))
        self.assertIsNotNone(ss.parse_line(line(GPT, "/arxiv-data/papers-1.json")))


class AgentCountTest(unittest.TestCase):
    def test_one_count_per_request_and_online_window(self):
        state = {}
        lines = [
            line(GPT),  # GPTBot also appears in its own URL: still one request
            line(GPT, "/tutorials/"),
            line(CHATGPT_USER),
            line(EXA, t="21/Nov/2026:20:40:00 +0800"),  # 20 minutes ago: total yes, online no
            line(PERSON),
            line(GPT, "/assets/x.css"),
        ]
        ss.update_agents(state, lines, NOW)
        self.assertEqual(state["agent_totals"], {"GPTBot": 2, "ChatGPT-User": 1, "ExaSearchBot": 1})
        self.assertEqual(state["agent_user_requests"], 1)
        pub = ss.build_public(state, {"online": 2, "total": 90, "since": "2026-11-16"}, NOW)
        self.assertEqual(pub["online"], {"humans": 2, "agents": 2, "agent_names": ["ChatGPT-User", "GPTBot"]})
        self.assertEqual(pub["total"]["agent_requests"], 4)
        self.assertEqual(pub["agents_top"][0], ("GPTBot", 2))


class LogFollowTest(unittest.TestCase):
    def test_incremental_partial_line_and_rotation(self):
        with tempfile.TemporaryDirectory() as d:
            log = Path(d) / "quant.access.log"
            log.write_text(line(GPT) + line(PERSON) + line(GPT)[:20])  # last line still being written
            got, cur = ss.read_new_lines(log, {})
            self.assertEqual(len(got), 2)
            with open(log, "a") as fh:
                fh.write(line(GPT)[20:] + line(CHATGPT_USER))
            got, cur = ss.read_new_lines(log, cur)
            self.assertEqual([ss.classify(ss.parse_line(g)[3])[0] for g in got], ["GPTBot", "ChatGPT-User"])
            # logrotate: rename to .1 (a late line lands there first), new empty file created
            with open(log, "a") as fh:
                fh.write(line(EXA))
            os.rename(log, str(log) + ".1")
            log.write_text(line(GPT))
            got, cur = ss.read_new_lines(log, cur)
            self.assertEqual([ss.classify(ss.parse_line(g)[3])[0] for g in got], ["ExaSearchBot", "GPTBot"])
            got, _ = ss.read_new_lines(log, cur)
            self.assertEqual(got, [])

    def test_run_writes_json_and_keeps_totals(self):
        with tempfile.TemporaryDirectory() as d:
            log = Path(d) / "a.log"
            log.write_text(line(GPT) + line(CHATGPT_USER))
            args = argparse.Namespace(log=str(log), out=str(Path(d) / "out" / "s.json"), state=str(Path(d) / "st.json"),
                                      website_id="x", container="x", no_umami=True)
            ss.run(args, NOW)
            with open(log, "a") as fh:
                fh.write(line(GPT))
            pub = ss.run(args, NOW)
            self.assertEqual(pub["total"]["agent_requests"], 3)
            self.assertIsNone(pub["online"]["humans"])  # unknown, not zero
            on_disk = json.loads((Path(d) / "out" / "s.json").read_text())
            self.assertEqual(on_disk["total"]["agent_requests"], 3)
            self.assertEqual(oct(os.stat(Path(d) / "out" / "s.json").st_mode & 0o777), "0o644")


if __name__ == "__main__":
    unittest.main()
