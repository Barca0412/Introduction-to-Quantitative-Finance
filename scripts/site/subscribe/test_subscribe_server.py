"""Tests: python3 -m unittest scripts/site/subscribe/test_subscribe_server.py (binds 127.0.0.1)."""
import json
import re
import sys
import tempfile
import threading
import unittest
import urllib.error
import urllib.request
from http.server import ThreadingHTTPServer
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import subscribe_server as ss  # noqa: E402


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *a, **k):
        return None


OPENER = urllib.request.build_opener(NoRedirect)


class FlowTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        d = Path(self.tmp.name)
        self.cfg = ss.load_config(None)
        self.cfg.update(DB_PATH=str(d / "s.db"), OUTBOX=str(d / "outbox.txt"), SITE_URL="https://site.test",
                        DOMAINS="asset-pricing,trading,credit-banking")
        self.store = ss.Store(self.cfg["DB_PATH"])
        handler = ss.make_handler(self.store, ss.Mailer(self.cfg), self.cfg, ss.RateLimiter(3, 3600))
        self.server = ThreadingHTTPServer(("127.0.0.1", 0), handler)
        self.base = f"http://127.0.0.1:{self.server.server_address[1]}"
        threading.Thread(target=self.server.serve_forever, daemon=True).start()

    def tearDown(self):
        self.server.shutdown()
        self.server.server_close()
        self.tmp.cleanup()

    def post(self, path, body, origin=None):
        req = urllib.request.Request(self.base + path, data=json.dumps(body).encode(), method="POST",
                                     headers={"Content-Type": "application/json", **({"Origin": origin} if origin else {})})
        try:
            with OPENER.open(req) as r:
                return r.status, json.loads(r.read()), dict(r.headers)
        except urllib.error.HTTPError as e:
            return e.code, json.loads(e.read() or b"{}"), dict(e.headers)

    def get(self, path):
        try:
            with OPENER.open(self.base + path) as r:
                return r.status, r.headers.get("Location")
        except urllib.error.HTTPError as e:
            return e.code, e.headers.get("Location")

    def outbox_tokens(self):
        text = Path(self.cfg["OUTBOX"]).read_text(encoding="utf-8") if Path(self.cfg["OUTBOX"]).exists() else ""
        return re.findall(r"/api/subscribe/confirm\?t=([\w\-]+)", text)

    def test_double_opt_in_then_unsubscribe(self):
        code, body, headers = self.post("/api/subscribe/", {"email": " Reader@Example.com ", "domains": ["trading"]},
                                        origin="https://barca0412.github.io")
        self.assertEqual((code, body), (200, {"ok": True}))
        self.assertEqual(headers.get("Access-Control-Allow-Origin"), "https://barca0412.github.io")
        self.assertEqual(self.store.subscribed(), [])  # pending until confirmed
        tokens = self.outbox_tokens()
        self.assertEqual(len(tokens), 1)
        self.assertEqual(self.get(f"/api/subscribe/confirm?t={tokens[0]}"), (303, "https://site.test/subscribe/confirmed"))
        subs = self.store.subscribed()
        self.assertEqual([(s["email"], s["domains"]) for s in subs], [("reader@example.com", ["trading"])])
        # confirm link works once
        self.assertEqual(self.get(f"/api/subscribe/confirm?t={tokens[0]}")[1], "https://site.test/subscribe/invalid")
        # topics can be changed with the unsubscribe token from the digest
        code, body, _ = self.post("/api/subscribe/domains", {"t": subs[0]["unsub_token"], "domains": ["asset-pricing"]})
        self.assertTrue(body["ok"])
        self.assertEqual(self.get(f"/api/subscribe/unsubscribe?t={subs[0]['unsub_token']}")[1],
                         "https://site.test/subscribe/unsubscribed")
        self.assertEqual(self.store.subscribed(), [])
        self.assertEqual(self.store.counts(), {"unsubscribed": 1})

    def test_known_address_gets_no_new_mail_and_same_answer(self):
        self.post("/api/subscribe/", {"email": "a@example.com"})
        self.get(f"/api/subscribe/confirm?t={self.outbox_tokens()[0]}")
        code, body, _ = self.post("/api/subscribe/", {"email": "a@example.com", "domains": ["credit-banking"]})
        self.assertEqual((code, body), (200, {"ok": True}))
        self.assertEqual(len(self.outbox_tokens()), 1)
        self.assertEqual(self.store.subscribed()[0]["domains"], ["credit-banking"])

    def test_pending_resend_is_throttled(self):
        self.post("/api/subscribe/", {"email": "b@example.com"})
        self.post("/api/subscribe/", {"email": "b@example.com"})
        self.assertEqual(len(self.outbox_tokens()), 1)

    def test_rejects_bad_input_and_honeypot(self):
        code, body, _ = self.post("/api/subscribe/", {"email": "bot@example.com", "website": "http://spam"})
        self.assertEqual((code, body), (200, {"ok": True}))  # looks fine to the bot, but nothing stored or sent
        self.assertEqual(self.store.counts(), {})
        self.assertEqual(self.post("/api/subscribe/", {"email": "not-an-email"})[1]["error"], "bad-email")
        self.assertEqual(self.post("/api/subscribe/", {"email": "c@example.com", "domains": ["unknown"]})[1]["error"], "bad-domains")
        # invalid attempts count toward the per-IP limit too (3 in this test setup)
        self.assertEqual(self.post("/api/subscribe/", {"email": "c@example.com", "domains": ["x", "y", "z", "w"]})[0], 429)
        self.assertEqual(ss.clean_domains(["x", "y", "z", "w"], []), None)
        self.assertEqual(self.get("/api/subscribe/unsubscribe?t=nope")[1], "https://site.test/subscribe/invalid")

    def test_rate_limit(self):
        for i in range(3):
            self.post("/api/subscribe/", {"email": f"r{i}@example.com"})
        self.assertEqual(self.post("/api/subscribe/", {"email": "r9@example.com"})[0], 429)

    def test_one_click_unsubscribe_post(self):
        self.post("/api/subscribe/", {"email": "d@example.com"})
        self.get(f"/api/subscribe/confirm?t={self.outbox_tokens()[0]}")
        t = self.store.subscribed()[0]["unsub_token"]
        req = urllib.request.Request(f"{self.base}/api/subscribe/unsubscribe?t={t}", data=b"List-Unsubscribe=One-Click", method="POST")
        with OPENER.open(req) as r:
            self.assertEqual(r.status, 200)
        self.assertEqual(self.store.subscribed(), [])


if __name__ == "__main__":
    unittest.main()
