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

Mail goes out through SMTP configured in the config file. Without SMTP settings, mails are
appended to an "outbox" file instead (for testing).
"""
from __future__ import annotations

import argparse
import json
import re
import secrets
import smtplib
import sqlite3
import sys
import threading
import time
from collections import defaultdict, deque
from datetime import datetime, timezone
from email.message import EmailMessage
from email.utils import formataddr, make_msgid
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Dict, List, Optional
from urllib.parse import parse_qs, urlencode, urlsplit

EMAIL_RE = re.compile(r"^[A-Za-z0-9._%+\-]+@[A-Za-z0-9\-]+(\.[A-Za-z0-9\-]+)*\.[A-Za-z]{2,}$")
DOMAIN_RE = re.compile(r"^[a-z0-9][a-z0-9\-]{0,40}$")
MAX_DOMAINS = 3
MAX_BODY = 4096
RATE_LIMIT = (5, 3600)  # at most 5 subscribe requests per IP per hour
CONFIRM_TTL_DAYS = 7

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

    def subscribe(self, email: str, domains: List[str]) -> Optional[Dict]:
        """Returns the row to send a confirm mail for, or None if nothing should be sent."""
        with self.lock:
            row = self.db.execute("SELECT status, confirm_sent_at FROM subscribers WHERE email=?", (email,)).fetchone()
            token = secrets.token_urlsafe(24)
            ts = now_iso()
            if row is None:
                self.db.execute(
                    "INSERT INTO subscribers (email, domains, status, confirm_token, unsub_token, created_at, confirm_sent_at)"
                    " VALUES (?, ?, 'pending', ?, ?, ?, ?)",
                    (email, json.dumps(domains), token, secrets.token_urlsafe(24), ts, ts),
                )
            elif row[0] == "subscribed":
                # already in: just update topics, do not mail (and do not tell the caller)
                self.db.execute("UPDATE subscribers SET domains=? WHERE email=?", (json.dumps(domains), email))
                return None
            else:
                # pending or unsubscribed: (re)start double opt-in, at most one mail per 10 minutes
                last = row[1]
                if last and time.time() - datetime.fromisoformat(last).timestamp() < 600:
                    return None
                self.db.execute(
                    "UPDATE subscribers SET domains=?, status='pending', confirm_token=?, confirm_sent_at=? WHERE email=?",
                    (json.dumps(domains), token, ts, email),
                )
            return {"email": email, "confirm_token": token}

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

    def unsubscribe(self, token: str) -> bool:
        with self.lock:
            cur = self.db.execute(
                "UPDATE subscribers SET status='unsubscribed', unsubscribed_at=?, confirm_token=NULL WHERE unsub_token=?",
                (now_iso(), token),
            )
            return cur.rowcount > 0

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
        if not (cfg["SMTP_HOST"] and cfg["MAIL_FROM"]):
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


def clean_domains(raw, allowed: List[str]) -> Optional[List[str]]:
    if raw is None:
        return []
    if not isinstance(raw, list) or len(raw) > MAX_DOMAINS:
        return None
    out = []
    for d in raw:
        if not isinstance(d, str) or not DOMAIN_RE.match(d) or (allowed and d not in allowed):
            return None
        if d not in out:
            out.append(d)
    return out


def make_handler(store: Store, mailer: Mailer, cfg: Dict[str, str], limiter: RateLimiter):
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
                ok = bool(token) and store.unsubscribe(token)
                return self._redirect("/subscribe/unsubscribed" if ok else "/subscribe/invalid")
            if path == "/api/subscribe/health":
                return self._json(200, {"ok": True})
            self._json(404, {"ok": False})

        def do_POST(self):
            path, token = self._route()
            if path == "/api/subscribe/unsubscribe":  # RFC 8058 one-click
                ok = bool(token) and store.unsubscribe(token)
                return self._json(200 if ok else 404, {"ok": ok})
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
            pending = store.subscribe(email, domains)
            if pending:
                mail = confirm_mail(cfg, pending["confirm_token"])
                try:
                    mailer.send(email, mail["subject"], mail["text"])
                except Exception as exc:  # the address is stored; the mail can be re-sent later
                    sys.stderr.write(f"{now_iso()} confirm mail failed: {type(exc).__name__}\n")
                    return self._json(502, {"ok": False, "error": "mail-failed"})
            return self._json(200, {"ok": True})

    return Handler


def main(argv: Optional[List[str]] = None) -> int:
    p = argparse.ArgumentParser(description="Weekly digest subscription service")
    p.add_argument("--config", default=str(Path.home() / "subscribe" / "config.env"))
    p.add_argument("command", nargs="?", default="serve", choices=["serve", "count"])
    args = p.parse_args(argv)
    cfg = load_config(args.config)
    store = Store(cfg["DB_PATH"])
    if args.command == "count":
        print(json.dumps(store.counts()))
        return 0
    server = ThreadingHTTPServer((cfg["HOST"], int(cfg["PORT"])),
                                 make_handler(store, Mailer(cfg), cfg, RateLimiter(*RATE_LIMIT)))
    sys.stderr.write(f"{now_iso()} listening on {cfg['HOST']}:{cfg['PORT']}\n")
    server.serve_forever()
    return 0


if __name__ == "__main__":
    sys.exit(main())
