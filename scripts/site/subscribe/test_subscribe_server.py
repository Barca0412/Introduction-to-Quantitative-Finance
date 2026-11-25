"""Tests: python3 -m unittest scripts/site/subscribe/test_subscribe_server.py (binds 127.0.0.1)."""
import json
import re
import time
import sys
import tempfile
import threading
import unittest
import urllib.error
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import subscribe_server as ss  # noqa: E402


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *a, **k):
        return None


OPENER = urllib.request.build_opener(NoRedirect)


class FakeFeishu:
    """A local stand-in for the Feishu webhook that records what was posted."""

    def __init__(self):
        self.posts = []
        outer = self

        class H(BaseHTTPRequestHandler):
            def log_message(self, *a):
                pass

            def do_POST(self):
                outer.posts.append(json.loads(self.rfile.read(int(self.headers["Content-Length"]))))
                body = b'{"code":0}'
                self.send_response(200)
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)

        self.server = ThreadingHTTPServer(("127.0.0.1", 0), H)
        self.url = f"http://127.0.0.1:{self.server.server_address[1]}/hook"
        threading.Thread(target=self.server.serve_forever, daemon=True).start()

    def texts(self, n, timeout=3):
        end = time.time() + timeout
        while len(self.posts) < n and time.time() < end:
            time.sleep(0.02)
        return [p["content"]["text"] for p in self.posts]

    def close(self):
        self.server.shutdown()
        self.server.server_close()


class FlowTest(unittest.TestCase):
    MODE = "outbox"
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        d = Path(self.tmp.name)
        self.cfg = ss.load_config(None)
        self.feishu = FakeFeishu()
        self.cfg.update(DB_PATH=str(d / "s.db"), OUTBOX=str(d / "outbox.txt"), SITE_URL="https://site.test",
                        DOMAINS="asset-pricing,trading,credit-banking", MAIL_MODE=self.MODE, FEISHU_WEBHOOK=self.feishu.url)
        self.store = ss.Store(self.cfg["DB_PATH"])
        handler = ss.make_handler(self.store, ss.Mailer(self.cfg), self.cfg, ss.RateLimiter(3, 3600), ss.Feishu(self.cfg))
        self.server = ThreadingHTTPServer(("127.0.0.1", 0), handler)
        self.base = f"http://127.0.0.1:{self.server.server_address[1]}"
        threading.Thread(target=self.server.serve_forever, daemon=True).start()

    def tearDown(self):
        self.feishu.close()
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
        self.assertEqual(self.feishu.texts(2), ["新订阅：reader@example.com｜关心：交易与执行｜现有 1 人", "退订：reader@example.com｜现有 0 人"])

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


class QueueModeTest(FlowTest):
    """No mail service yet: store as pending, tell the reader, notify Feishu, mail later."""
    MODE = "queue"

    def test_double_opt_in_then_unsubscribe(self):  # replaced by the queue-mode flow below
        pass

    def test_known_address_gets_no_new_mail_and_same_answer(self):
        pass

    def test_pending_resend_is_throttled(self):
        pass

    def test_one_click_unsubscribe_post(self):
        pass

    def test_queue_then_send_confirms(self):
        code, body, _ = self.post("/api/subscribe/", {"email": "q@example.com", "domains": ["trading", "credit-banking"]})
        self.assertEqual((code, body), (200, {"ok": True, "queued": True}))
        self.assertEqual(self.outbox_tokens(), [])  # nothing mailed
        self.assertEqual(self.store.counts(), {"pending": 1})
        self.assertEqual(self.feishu.texts(1), ["新订阅：q@example.com｜关心：交易与执行、信用、银行与支付｜现有 1 人（确认信待发）"])
        # same address again: same answer, no second notification
        self.assertEqual(self.post("/api/subscribe/", {"email": "q@example.com"})[1], {"ok": True, "queued": True})
        time.sleep(0.2)
        self.assertEqual(len(self.feishu.posts), 1)
        # an unsent confirm token cannot be used
        tok = self.store.db.execute("SELECT confirm_token FROM subscribers").fetchone()[0]
        self.assertEqual(self.get(f"/api/subscribe/confirm?t={tok}")[1], "https://site.test/subscribe/invalid")
        # mail service arrives: send-confirms mails every queued address once
        cfg = dict(self.cfg, MAIL_MODE="outbox")
        self.assertEqual(ss.send_confirms(self.store, ss.Mailer(cfg), cfg, ss.Feishu(cfg)), 0)
        tokens = self.outbox_tokens()
        self.assertEqual(len(tokens), 1)
        self.assertEqual(ss.send_confirms(self.store, ss.Mailer(cfg), cfg, ss.Feishu(cfg)), 0)
        self.assertEqual(len(self.outbox_tokens()), 1)  # not mailed twice
        self.assertEqual(self.get(f"/api/subscribe/confirm?t={tokens[0]}")[1], "https://site.test/subscribe/confirmed")
        self.assertEqual(self.store.counts(), {"subscribed": 1})

    def test_send_confirms_refuses_without_mail_service(self):
        self.post("/api/subscribe/", {"email": "z@example.com"})
        self.assertEqual(ss.send_confirms(self.store, ss.Mailer(self.cfg), self.cfg, ss.Feishu({})), 1)
        self.assertEqual(self.store.pending_unsent(), [{"email": "z@example.com"}])


class FeishuSignTest(unittest.TestCase):
    def test_signature_matches_feishu_rule(self):
        import base64, hashlib, hmac
        f = ss.Feishu({"FEISHU_WEBHOOK": "x", "FEISHU_SECRET": "abc"})
        body = f.payload("hi", ts=1700000000)
        expect = base64.b64encode(hmac.new(b"1700000000\nabc", digestmod=hashlib.sha256).digest()).decode()
        self.assertEqual(body, {"msg_type": "text", "content": {"text": "hi"}, "timestamp": "1700000000", "sign": expect})
        self.assertNotIn("sign", ss.Feishu({"FEISHU_WEBHOOK": "x"}).payload("hi"))

    def test_mode_picked_from_config(self):
        self.assertEqual(ss.Mailer(ss.load_config(None)).mode, "queue")
        cfg = ss.load_config(None)
        cfg.update(SMTP_HOST="smtp.example", MAIL_FROM="a@example.com")
        self.assertEqual(ss.Mailer(cfg).mode, "smtp")


if __name__ == "__main__":
    unittest.main()
