#!/usr/bin/env python3
"""Weekly digest subscriptions for quant.hfthnu.com: subscribe, confirm, unsubscribe.

A tiny HTTP service (standard library + SQLite) that listens on 127.0.0.1 only; nginx forwards
https://quant.hfthnu.com/api/subscribe/ to it. See README.md in this folder.

What it stores, and nothing else: email, chosen finance domains (up to 3), status
(pending / subscribed / unsubscribed), two random tokens (confirm, unsubscribe) and timestamps.

Flow (double opt-in):
  POST /api/subscribe/              {"email", "domains": [...], "website": ""}  -> sends a confirm email
  GET  /api/subscribe/confirm?t=…    -> subscribed, redirects to /subscribe/confirmed
  GET  /api/subscribe/unsubscribe?t=… -> unsubscribed, redirects to /subscribe/unsubscribed
  POST /api/subscribe/unsubscribe?t=… -> same, for mail clients' one-click unsubscribe (RFC 8058)
  POST /api/subscribe/domains        {"t", "domains"} -> change topics (from the link in each digest)
The POST answer never says whether an address was already known.

Mail modes (MAIL_MODE, or picked automatically):
  smtp   - SMTP is configured: the confirm mail goes out right away.
  queue  - no mail service yet (default without SMTP): the address is stored as pending and the
           reader is told a confirm mail will come before the first issue. Once SMTP is set up,
           `subscribe_server.py send-confirms` mails all of them.
  outbox - for tests: mails are appended to the OUTBOX file instead of being sent.

Feishu: if FEISHU_WEBHOOK (a custom group bot) is set, each new subscription and each
unsubscription is posted to that internal group. FEISHU_SECRET is needed only when the bot has
signature checking on. A failed post never fails the subscription.
"""
from __future__ import annotations

import argparse
import base64
import hashlib
import hmac
import json
import re
import secrets
import smtplib
import sqlite3
import sys
import threading
import time
import urllib.request
from collections import defaultdict, deque
from datetime import datetime, timezone
from email.message import EmailMessage
from email.utils import formataddr, make_msgid
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Dict, List, Optional
from urllib.parse import parse_qs, urlencode, urlsplit

EMAIL_RE = re.compile(r"^[A-Za-z0-9._%+\-]+@[A-Za-z0-9\-]+(\.[A-Za-z0-9\-]+)*\.[A-Za-z]{2,}$")
ID_RE = r"[a-z0-9][a-z0-9\-]{0,40}"
# an interest is a whole row (d:<domain>), a whole column (t:<task>) or one cell (d:<domain>|t:<task>)
PICK_RE = re.compile(rf"^(?:d:(?P<d>{ID_RE})(?:\|t:(?P<t>{ID_RE}))?|t:(?P<t2>{ID_RE}))$")
MAX_DOMAINS = 9
MAX_BODY = 4096
RATE_LIMIT = (5, 3600)  # at most 5 subscribe requests per IP per hour
CONFIRM_TTL_DAYS = 7
DOMAIN_NAMES = {
    "asset-pricing": "资产定价与因子", "trading": "交易与执行", "portfolio-risk": "组合与风险",
    "derivatives": "衍生品", "credit-banking": "信用、银行与支付", "corporate-finance": "公司金融与会计",
    "fin-nlp": "金融文本与舆情", "crypto-defi": "加密资产", "macro-policy": "宏观与政策",
    "insurance-household": "保险与个人金融", "market-structure": "市场结构与行为",
}
TASK_NAMES = {
    "forecasting": "预测", "pricing": "定价", "decision": "交易决策", "signal-mining": "因子挖掘",
    "understanding": "理解问答", "risk-assessment": "风险评估", "generation": "生成", "simulation": "市场模拟",
    "multi-task": "多任务",
}

SCHEMA = """
CREATE TABLE IF NOT EXISTS subscribers (
  email          TEXT PRIMARY KEY,
  domains        TEXT NOT NULL DEFAULT '[]',
  status         TEXT NOT NULL CHECK (status IN ('pending', 'subscribed', 'unsubscribed')),
  confirm_token  TEXT UNIQUE,
  unsub_token    TEXT NOT NULL UNIQUE,
  created_at     TEXT NOT NULL,
  confirm_sent_at TEXT,
  confirmed_at   TEXT,
  unsubscribed_at TEXT
);
"""


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def load_config(path: Optional[str]) -> Dict[str, str]:
    """KEY=VALUE lines; # comments. Secrets (SMTP_PASS) live only in this file on the server."""
    cfg = {
        "HOST": "127.0.0.1",
        "PORT": "8731",
        "DB_PATH": str(Path.home() / "subscribe" / "subscribers.db"),
        "OUTBOX": str(Path.home() / "subscribe" / "outbox.txt"),
        "SITE_URL": "https://quant.hfthnu.com",
        "ALLOWED_ORIGINS": "https://quant.hfthnu.com,https://barca0412.github.io",
        "MAIL_FROM": "",
        "MAIL_FROM_NAME": "AI × 金融周报",
        "REPLY_TO": "",
        "SMTP_HOST": "",
        "SMTP_PORT": "465",
        "SMTP_USER": "",
        "SMTP_PASS": "",
        "DOMAINS": "",  # comma-separated allowed finance-domain ids; empty = accept any well-formed id
        "MAIL_MODE": "",  # smtp | queue | outbox; empty = smtp if SMTP is configured, else queue
        "FEISHU_WEBHOOK": "",
        "FEISHU_SECRET": "",
    }
    if path and Path(path).exists():
        for line in Path(path).read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                cfg[k.strip()] = v.strip()
    return cfg


class Store:
    def __init__(self, db_path: str):
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self.db = sqlite3.connect(db_path, check_same_thread=False, isolation_level=None)
        self.db.execute("PRAGMA journal_mode=WAL")
        self.db.executescript(SCHEMA)
        self.lock = threading.Lock()

    def subscribe(self, email: str, domains: List[str], send: bool = True) -> Optional[Dict]:
        """Store or refresh a subscription. Returns {"email", "confirm_token"} when this is a new or
        renewed sign-up (send a confirm mail if `send`, and notify), or None when nothing changed
        that needs a mail or a notification.

        send=False (queue mode): the address is stored as pending with confirm_sent_at empty;
        `pending_unsent()` + `mark_sent()` mail it later.
        """
        with self.lock:
            row = self.db.execute("SELECT status, confirm_sent_at FROM subscribers WHERE email=?", (email,)).fetchone()
            token = secrets.token_urlsafe(24)
            ts = now_iso()
            sent_at = ts if send else None
            if row is None:
                self.db.execute(
                    "INSERT INTO subscribers (email, domains, status, confirm_token, unsub_token, created_at, confirm_sent_at)"
                    " VALUES (?, ?, 'pending', ?, ?, ?, ?)",
                    (email, json.dumps(domains), token, secrets.token_urlsafe(24), ts, sent_at),
                )
            elif row[0] == "subscribed" or (row[0] == "pending" and not send and row[1] is None):
                # already in, or already queued: just update topics, no mail, no notification
                self.db.execute("UPDATE subscribers SET domains=? WHERE email=?", (json.dumps(domains), email))
                return None
            else:
                # pending or unsubscribed: (re)start double opt-in, at most one mail per 10 minutes
                last = row[1]
                if send and last and time.time() - datetime.fromisoformat(last).timestamp() < 600:
                    return None
                self.db.execute(
                    "UPDATE subscribers SET domains=?, status='pending', confirm_token=?, confirm_sent_at=? WHERE email=?",
                    (json.dumps(domains), token, sent_at, email),
                )
            return {"email": email, "confirm_token": token}

    def pending_unsent(self) -> List[Dict]:
        rows = self.db.execute("SELECT email FROM subscribers WHERE status='pending' AND confirm_sent_at IS NULL ORDER BY created_at")
        return [{"email": e} for (e,) in rows]

    def renew_token(self, email: str) -> str:
        """A fresh confirm token for a queued address, stamped as sent now (the 7-day clock starts)."""
        token = secrets.token_urlsafe(24)
        with self.lock:
            self.db.execute("UPDATE subscribers SET confirm_token=?, confirm_sent_at=? WHERE email=? AND status='pending'",
                            (token, now_iso(), email))
        return token

    def unmark_sent(self, email: str) -> None:
        with self.lock:
            self.db.execute("UPDATE subscribers SET confirm_sent_at=NULL WHERE email=? AND status='pending'", (email,))

    def active_count(self) -> int:
        return self.db.execute("SELECT count(*) FROM subscribers WHERE status IN ('pending', 'subscribed')").fetchone()[0]

    def domains_of(self, email: str) -> List[str]:
        row = self.db.execute("SELECT domains FROM subscribers WHERE email=?", (email,)).fetchone()
        return json.loads(row[0]) if row else []

    def confirm(self, token: str) -> bool:
        with self.lock:
            row = self.db.execute(
                "SELECT email, confirm_sent_at FROM subscribers WHERE confirm_token=? AND status='pending'", (token,)
            ).fetchone()
            if not row:
                return False
            sent = datetime.fromisoformat(row[1]).timestamp() if row[1] else 0
            if time.time() - sent > CONFIRM_TTL_DAYS * 86400:
                return False
            self.db.execute(
                "UPDATE subscribers SET status='subscribed', confirmed_at=?, confirm_token=NULL WHERE email=?",
                (now_iso(), row[0]),
            )
            return True

    def unsubscribe(self, token: str) -> Optional[str]:
        """The email that was unsubscribed now, or None (unknown token or already unsubscribed)."""
        with self.lock:
            row = self.db.execute("SELECT email FROM subscribers WHERE unsub_token=? AND status != 'unsubscribed'", (token,)).fetchone()
            if not row:
                return None
            self.db.execute(
                "UPDATE subscribers SET status='unsubscribed', unsubscribed_at=?, confirm_token=NULL WHERE email=?",
                (now_iso(), row[0]),
            )
            return row[0]

    def set_domains(self, token: str, domains: List[str]) -> bool:
        with self.lock:
            cur = self.db.execute(
                "UPDATE subscribers SET domains=? WHERE unsub_token=? AND status='subscribed'", (json.dumps(domains), token)
            )
            return cur.rowcount > 0

    def subscribed(self) -> List[Dict]:
        rows = self.db.execute("SELECT email, domains, unsub_token FROM subscribers WHERE status='subscribed' ORDER BY email")
        return [{"email": e, "domains": json.loads(d), "unsub_token": t} for e, d, t in rows]

    def counts(self) -> Dict[str, int]:
        return dict(self.db.execute("SELECT status, count(*) FROM subscribers GROUP BY status").fetchall())


class Mailer:
    def __init__(self, cfg: Dict[str, str]):
        self.cfg = cfg
        mode = (cfg.get("MAIL_MODE") or "").strip().lower()
        if mode not in ("smtp", "queue", "outbox"):
            mode = "smtp" if (cfg["SMTP_HOST"] and cfg["MAIL_FROM"]) else "queue"
        self.mode = mode

    @property
    def sends_now(self) -> bool:
        return self.mode in ("smtp", "outbox")

    def send(self, to: str, subject: str, text: str, html: Optional[str] = None, headers: Optional[Dict[str, str]] = None) -> None:
        cfg = self.cfg
        msg = EmailMessage()
        msg["Subject"] = subject
        msg["From"] = formataddr((cfg["MAIL_FROM_NAME"], cfg["MAIL_FROM"] or "noreply@localhost"))
        msg["To"] = to
        msg["Message-ID"] = make_msgid(domain=(cfg["MAIL_FROM"].split("@")[-1] or "localhost"))
        if cfg.get("REPLY_TO"):
            msg["Reply-To"] = cfg["REPLY_TO"]
        for k, v in (headers or {}).items():
            msg[k] = v
        msg.set_content(text)
        if html:
            msg.add_alternative(html, subtype="html")
        if self.mode == "queue":
            raise RuntimeError("no mail service configured (MAIL_MODE=queue)")
        if self.mode == "outbox":
            Path(cfg["OUTBOX"]).parent.mkdir(parents=True, exist_ok=True)
            with open(cfg["OUTBOX"], "a", encoding="utf-8") as fh:
                fh.write(f"===== {now_iso()} To: {to}\nSubject: {subject}\n{text}\n\n")
            return
        port = int(cfg["SMTP_PORT"])
        if port == 465:
            with smtplib.SMTP_SSL(cfg["SMTP_HOST"], port, timeout=15) as s:
                s.login(cfg["SMTP_USER"], cfg["SMTP_PASS"])
                s.send_message(msg)
        else:
            with smtplib.SMTP(cfg["SMTP_HOST"], port, timeout=15) as s:
                s.starttls()
                s.login(cfg["SMTP_USER"], cfg["SMTP_PASS"])
                s.send_message(msg)


def confirm_mail(cfg: Dict[str, str], token: str) -> Dict[str, str]:
    link = f"{cfg['SITE_URL']}/api/subscribe/confirm?{urlencode({'t': token})}"
    text = (
        "你好！\n\n"
        "有人（希望是你）在「量化研究入门与AI+金融」网站上用这个邮箱订阅了每周的全球 AI × 金融资讯。\n"
        f"点下面的链接确认订阅（{CONFIRM_TTL_DAYS} 天内有效）：\n\n{link}\n\n"
        "如果不是你本人操作，忽略这封邮件即可，我们不会再给你发信。\n\n"
        "—— 湖南大学金融科技协会 Quant Group\n"
        f"{cfg['SITE_URL']}\n"
    )
    return {"subject": "请确认订阅：每周全球 AI × 金融资讯", "text": text}


class Feishu:
    """Posts short text messages to an internal Feishu group through a custom bot. Never raises."""

    def __init__(self, cfg: Dict[str, str]):
        self.url = cfg.get("FEISHU_WEBHOOK", "").strip()
        self.secret = cfg.get("FEISHU_SECRET", "").strip()

    def payload(self, text: str, ts: Optional[int] = None) -> Dict:
        body: Dict = {"msg_type": "text", "content": {"text": text}}
        if self.secret:
            ts = ts or int(time.time())
            string_to_sign = f"{ts}\n{self.secret}"
            sign = base64.b64encode(hmac.new(string_to_sign.encode(), digestmod=hashlib.sha256).digest()).decode()
            body.update(timestamp=str(ts), sign=sign)
        return body

    def _post(self, text: str) -> None:
        try:
            req = urllib.request.Request(self.url, data=json.dumps(self.payload(text)).encode(),
                                         headers={"Content-Type": "application/json"}, method="POST")
            with urllib.request.urlopen(req, timeout=10) as r:
                answer = json.loads(r.read() or b"{}")
            if answer.get("code", 0) not in (0, None):
                sys.stderr.write(f"{now_iso()} feishu rejected: code {answer.get('code')}\n")
        except Exception as exc:
            sys.stderr.write(f"{now_iso()} feishu post failed: {type(exc).__name__}\n")

    def notify(self, text: str, wait: bool = False) -> None:
        if not self.url:
            return
        t = threading.Thread(target=self._post, args=(text,), daemon=True)
        t.start()
        if wait:
            t.join()


def domain_label(picks: List[str]) -> str:
    def one(key: str) -> str:
        m = PICK_RE.match(key if ":" in key else f"d:{key}")
        if not m:
            return key
        d, t = m.group("d"), m.group("t") or m.group("t2")
        dn, tn = DOMAIN_NAMES.get(d or "", d), TASK_NAMES.get(t or "", t)
        return f"{dn}×{tn}" if d and t else (f"{dn}（整行）" if d else f"{tn}（整列）")
    return "、".join(one(k) for k in picks) or "全部"


class RateLimiter:
    def __init__(self, limit: int, window: int):
        self.limit, self.window = limit, window
        self.hits: Dict[str, deque] = defaultdict(deque)
        self.lock = threading.Lock()

    def allow(self, key: str) -> bool:
        now = time.monotonic()
        with self.lock:
            q = self.hits[key]
            while q and now - q[0] > self.window:
                q.popleft()
            if len(q) >= self.limit:
                return False
            q.append(now)
            return True


def clean_domains(raw, allowed: List[str], tasks: Optional[List[str]] = None) -> Optional[List[str]]:
    """Normalise the reader's interests: up to 9 of 'd:<domain>', 't:<task>', 'd:<domain>|t:<task>'.
    A bare domain id (older form) is read as 'd:<id>'. Returns None for anything invalid."""
    tasks = list(TASK_NAMES) if tasks is None else tasks
    if raw is None:
        return []
    if not isinstance(raw, list) or len(raw) > MAX_DOMAINS:
        return None
    out = []
    for item in raw:
        if not isinstance(item, str):
            return None
        key = item if ":" in item else f"d:{item}"
        m = PICK_RE.match(key)
        if not m:
            return None
        d, t = m.group("d"), m.group("t") or m.group("t2")
        if (d and allowed and d not in allowed) or (t and t not in tasks):
            return None
        if key not in out:
            out.append(key)
    return out


def make_handler(store: Store, mailer: Mailer, cfg: Dict[str, str], limiter: RateLimiter, feishu: Optional[Feishu] = None):
    feishu = feishu or Feishu({})
    allowed_origins = {o.strip() for o in cfg["ALLOWED_ORIGINS"].split(",") if o.strip()}
    allowed_domains = [d.strip() for d in cfg["DOMAINS"].split(",") if d.strip()]
    site = cfg["SITE_URL"].rstrip("/")

    class Handler(BaseHTTPRequestHandler):
        server_version = "subscribe"
        sys_version = ""

        def log_message(self, fmt, *args):  # no IPs or emails in logs
            sys.stderr.write(f"{now_iso()} {self.command} {urlsplit(self.path).path} {args[1] if len(args) > 1 else ''}\n")

        def _ip(self) -> str:
            return self.headers.get("X-Real-IP") or self.client_address[0]

        def _cors(self):
            origin = self.headers.get("Origin")
            if origin in allowed_origins:
                self.send_header("Access-Control-Allow-Origin", origin)
                self.send_header("Vary", "Origin")
                self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
                self.send_header("Access-Control-Allow-Headers", "Content-Type")

        def _json(self, code: int, body: Dict):
            data = json.dumps(body, ensure_ascii=False).encode()
            self.send_response(code)
            self._cors()
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Cache-Control", "no-store")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)

        def _redirect(self, path: str):
            self.send_response(303)
            self.send_header("Location", site + path)
            self.send_header("Cache-Control", "no-store")
            self.end_headers()

        def _route(self):
            parts = urlsplit(self.path)
            path = parts.path.rstrip("/")
            token = (parse_qs(parts.query).get("t") or [""])[0]
            return path, token

        def _body(self) -> Optional[Dict]:
            length = int(self.headers.get("Content-Length") or 0)
            if length <= 0 or length > MAX_BODY:
                return None
            try:
                data = json.loads(self.rfile.read(length))
            except (ValueError, UnicodeDecodeError):
                return None
            return data if isinstance(data, dict) else None

        def do_OPTIONS(self):
            self.send_response(204)
            self._cors()
            self.end_headers()

        def do_GET(self):
            path, token = self._route()
            if path == "/api/subscribe/confirm":
                ok = bool(token) and store.confirm(token)
                return self._redirect("/subscribe/confirmed" if ok else "/subscribe/invalid")
            if path == "/api/subscribe/unsubscribe":
                gone = store.unsubscribe(token) if token else None
                if gone:
                    feishu.notify(f"退订：{gone}｜现有 {store.active_count()} 人")
                return self._redirect("/subscribe/unsubscribed" if gone else "/subscribe/invalid")
            if path == "/api/subscribe/health":
                return self._json(200, {"ok": True})
            self._json(404, {"ok": False})

        def do_POST(self):
            path, token = self._route()
            if path == "/api/subscribe/unsubscribe":  # RFC 8058 one-click
                gone = store.unsubscribe(token) if token else None
                if gone:
                    feishu.notify(f"退订：{gone}｜现有 {store.active_count()} 人")
                return self._json(200 if gone else 404, {"ok": bool(gone)})
            if path == "/api/subscribe/domains":
                body = self._body() or {}
                domains = clean_domains(body.get("domains"), allowed_domains)
                if domains is None or not isinstance(body.get("t"), str):
                    return self._json(400, {"ok": False, "error": "bad-request"})
                return self._json(200, {"ok": store.set_domains(body["t"], domains)})
            if path != "/api/subscribe":
                return self._json(404, {"ok": False})
            if not limiter.allow(self._ip()):
                return self._json(429, {"ok": False, "error": "too-many"})
            body = self._body()
            if body is None:
                return self._json(400, {"ok": False, "error": "bad-request"})
            if body.get("website"):  # honeypot: humans never fill this hidden field
                return self._json(200, {"ok": True})
            email = str(body.get("email") or "").strip().lower()
            if len(email) > 254 or not EMAIL_RE.match(email):
                return self._json(400, {"ok": False, "error": "bad-email"})
            domains = clean_domains(body.get("domains"), allowed_domains)
            if domains is None:
                return self._json(400, {"ok": False, "error": "bad-domains"})
            pending = store.subscribe(email, domains, send=mailer.sends_now)
            if pending:
                if mailer.sends_now:
                    mail = confirm_mail(cfg, pending["confirm_token"])
                    try:
                        mailer.send(email, mail["subject"], mail["text"])
                    except Exception as exc:  # stored; `send-confirms` can mail it later
                        store.unmark_sent(email)
                        sys.stderr.write(f"{now_iso()} confirm mail failed: {type(exc).__name__}\n")
                        return self._json(502, {"ok": False, "error": "mail-failed"})
                feishu.notify(f"新订阅：{email}｜关心：{domain_label(domains)}｜现有 {store.active_count()} 人"
                              + ("" if mailer.sends_now else "（确认信待发）"))
            # queued: the same answer whether or not the address was known before
            return self._json(200, {"ok": True, **({} if mailer.sends_now else {"queued": True})})

    return Handler


def send_confirms(store: Store, mailer: Mailer, cfg: Dict[str, str], feishu: Feishu, dry_run: bool = False) -> int:
    """Mail a confirm link to every address that signed up while there was no mail service."""
    todo = store.pending_unsent()
    if dry_run:
        print(f"{len(todo)} confirm mails would be sent")
        return 0
    if not mailer.sends_now:
        print("No mail service configured (set SMTP_* in config.env first).", file=sys.stderr)
        return 1
    sent = failed = 0
    for row in todo:
        token = store.renew_token(row["email"])
        mail = confirm_mail(cfg, token)
        try:
            mailer.send(row["email"], mail["subject"], mail["text"])
            sent += 1
        except Exception as exc:
            store.unmark_sent(row["email"])
            failed += 1
            sys.stderr.write(f"{now_iso()} confirm mail failed: {type(exc).__name__}\n")
        time.sleep(0.2)  # stay well under the mail service's per-second limit
    print(f"sent {sent}, failed {failed}")
    feishu.notify(f"已补发确认信 {sent} 封，失败 {failed} 封", wait=True)
    return 0 if failed == 0 else 2


def main(argv: Optional[List[str]] = None) -> int:
    p = argparse.ArgumentParser(description="Weekly digest subscription service")
    p.add_argument("--config", default=str(Path.home() / "subscribe" / "config.env"))
    p.add_argument("command", nargs="?", default="serve", choices=["serve", "count", "send-confirms"])
    p.add_argument("--dry-run", action="store_true", help="send-confirms: only list who would get a mail")
    args = p.parse_args(argv)
    cfg = load_config(args.config)
    store = Store(cfg["DB_PATH"])
    if args.command == "count":
        print(json.dumps(store.counts()))
        return 0
    if args.command == "send-confirms":
        return send_confirms(store, Mailer(cfg), cfg, Feishu(cfg), dry_run=args.dry_run)
    server = ThreadingHTTPServer((cfg["HOST"], int(cfg["PORT"])),
                                 make_handler(store, Mailer(cfg), cfg, RateLimiter(*RATE_LIMIT), Feishu(cfg)))
    sys.stderr.write(f"{now_iso()} listening on {cfg['HOST']}:{cfg['PORT']}\n")
    server.serve_forever()
    return 0


if __name__ == "__main__":
    sys.exit(main())
