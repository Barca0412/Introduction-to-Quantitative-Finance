#!/usr/bin/env python3
"""Public visit counters for the site's home page: people and AI agents, online now and in total.

Runs every minute on the web server (from the qgh user's crontab, see README.md) and writes one small
JSON file that nginx serves at https://quant.hfthnu.com/site-stats.json. Only totals are published:
no IP, no user agent string of a person, no page a person read.

Two sources, because neither sees everything:
- People come from Umami (our self-hosted analytics). Umami only sees visitors whose browser runs its
  script, so it does not see AI crawlers, but it does see crawlers that use a real browser. Sessions
  of one such crawler we identified (ExaSearchBot, see EXA_PATTERN) are left out.
- AI agents come from the nginx access log of the site. Only agents that name themselves in the
  User-Agent are counted. Agents that look like a normal browser are counted as people by Umami.

Standard library only (the server has plain Python 3.12).
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import tempfile
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple

ONLINE_WINDOW = timedelta(minutes=5)

# Known AI crawlers and assistants, matched case-insensitively against the User-Agent.
# Names follow the ai-robots-txt project (github.com/ai-robots-txt/ai.robots.txt), checked 2026-11-21,
# plus ExaSearchBot, which we saw in our own logs. Plain search engines (Googlebot, bingbot,
# Baiduspider, ...) are deliberately not on the list.
# kind: "crawler" = the company's crawler or search index;
#       "user"    = fetched because a person asked the assistant about this page right now.
AI_AGENTS: List[Tuple[str, str, str]] = [
    # (display name, regex, kind)
    ("ChatGPT-User", r"ChatGPT-User", "user"),
    ("OAI-SearchBot", r"OAI-SearchBot", "crawler"),
    ("GPTBot", r"GPTBot", "crawler"),
    ("Claude-User", r"Claude-User", "user"),
    ("Claude-SearchBot", r"Claude-SearchBot", "crawler"),
    ("ClaudeBot", r"ClaudeBot|anthropic-ai|Claude-Web", "crawler"),
    ("Perplexity-User", r"Perplexity-User", "user"),
    ("PerplexityBot", r"PerplexityBot", "crawler"),
    ("MistralAI-User", r"MistralAI-User", "user"),
    ("DuckAssistBot", r"DuckAssistBot", "user"),
    ("Gemini", r"Google-CloudVertexBot|Gemini-Deep-Research|GoogleAgent-Mariner", "user"),
    ("ExaSearchBot", r"ExaSearchBot|ExaBot", "crawler"),
    ("Meta AI", r"meta-externalagent|meta-externalfetcher|FacebookBot", "crawler"),
    ("Amazonbot", r"Amazonbot", "crawler"),
    ("Applebot", r"Applebot", "crawler"),
    ("Bytespider", r"Bytespider|TikTokSpider", "crawler"),
    ("CCBot", r"CCBot", "crawler"),
    ("Cohere", r"cohere-ai|cohere-training-data-crawler", "crawler"),
    ("YouBot", r"YouBot", "crawler"),
    ("Diffbot", r"Diffbot", "crawler"),
    ("PetalBot", r"PetalBot", "crawler"),
    ("Timpibot", r"Timpibot", "crawler"),
    ("AI2Bot", r"AI2Bot", "crawler"),
    ("Kangaroo Bot", r"Kangaroo Bot", "crawler"),
    ("ImagesiftBot", r"ImagesiftBot", "crawler"),
    ("PanguBot", r"PanguBot", "crawler"),
    ("Brightbot", r"Brightbot", "crawler"),
    ("FirecrawlAgent", r"FirecrawlAgent", "crawler"),
    ("TavilyBot", r"TavilyBot|Tavily", "crawler"),
    ("Jina", r"Jina-Reader|jina\.ai", "crawler"),
]
_AGENT_RE = [(name, re.compile(pattern, re.I), kind) for name, pattern, kind in AI_AGENTS]

# Static files are not "reading": an agent that renders a page also fetches its scripts and fonts.
STATIC_RE = re.compile(r"^/(assets|fonts|site)/|\.(js|mjs|css|woff2?|ttf|png|jpe?g|webp|gif|svg|ico|map)(\?|$)", re.I)

# nginx "combined": ip - user [time] "request" status bytes "referer" "user agent"
LOG_RE = re.compile(r'^(\S+) \S+ \S+ \[([^\]]+)\] "([^"]*)" (\d{3}) \S+ "[^"]*" "([^"]*)"')

# Umami sessions of ExaSearchBot (the crawler renders pages in a real browser). Identified on
# 2026-11-21 from the nginx log: IPs 152.163.101.x, all sessions below share these four fields.
EXA_PATTERN = "s.region = 'US-FL' AND s.os = 'Linux' AND s.screen = '1920x1080' AND s.language = 'en-US'"


def classify(user_agent: str) -> Optional[Tuple[str, str]]:
    """The AI agent named in a User-Agent, once per request; None for anything else."""
    for name, pattern, kind in _AGENT_RE:
        if pattern.search(user_agent):
            return name, kind
    return None


def parse_line(line: str) -> Optional[Tuple[datetime, str, str, str]]:
    """(time, ip, path, user agent) of one access-log line, or None if it is not a page request."""
    m = LOG_RE.match(line)
    if not m:
        return None
    ip, stamp, request, _status, ua = m.groups()
    parts = request.split(" ")
    if len(parts) < 2 or parts[0] not in ("GET", "HEAD"):
        return None
    path = parts[1]
    if STATIC_RE.search(path):
        return None
    try:
        when = datetime.strptime(stamp, "%d/%b/%Y:%H:%M:%S %z")
    except ValueError:
        return None
    return when, ip, path, ua


# ---------------------------------------------------------------- reading the log incrementally


def read_new_lines(log: Path, cursor: Dict) -> Tuple[List[str], Dict]:
    """Lines added since the last run, following a daily logrotate (rename + delaycompress).

    cursor = {"inode": int, "offset": int}. If the file was rotated, the rest of the old file is
    read from `<log>.1` (same inode) before starting the new file from the beginning.
    """
    lines: List[str] = []
    try:
        st = log.stat()
    except FileNotFoundError:
        return lines, cursor
    inode, offset = cursor.get("inode"), int(cursor.get("offset") or 0)

    if inode is not None and inode != st.st_ino:
        rotated = Path(str(log) + ".1")
        try:
            if rotated.stat().st_ino == inode:
                with open(rotated, "rb") as fh:
                    fh.seek(offset)
                    lines.extend(fh.read().decode("utf-8", "replace").splitlines(keepends=True))
        except FileNotFoundError:
            pass
        offset = 0
    elif st.st_size < offset:  # truncated in place
        offset = 0

    with open(log, "rb") as fh:
        fh.seek(offset)
        chunk = fh.read()
    end = chunk.rfind(b"\n") + 1  # a partial last line waits for the next run
    lines.extend(chunk[:end].decode("utf-8", "replace").splitlines(keepends=True))
    offset += end
    return lines, {"inode": st.st_ino, "offset": offset}


def update_agents(state: Dict, lines: Iterable[str], now: datetime) -> None:
    """Add AI requests from new log lines to the running totals and the recent-activity list."""
    totals: Dict[str, int] = state.setdefault("agent_totals", {})
    recent: List[List] = state.setdefault("agent_recent", [])  # [[epoch, name], ...]
    for line in lines:
        parsed = parse_line(line)
        if not parsed:
            continue
        when, _ip, _path, ua = parsed
        hit = classify(ua)
        if not hit:
            continue
        name, kind = hit
        totals[name] = totals.get(name, 0) + 1
        if kind == "user":
            state["agent_user_requests"] = int(state.get("agent_user_requests", 0)) + 1
        recent.append([when.timestamp(), name])
    cutoff = (now - ONLINE_WINDOW).timestamp()
    state["agent_recent"] = [r for r in recent if r[0] >= cutoff]


# ---------------------------------------------------------------- Umami (people)


def umami_people(website_id: str, container: str) -> Dict[str, int]:
    """People online now and in total, from the Umami database (read-only queries)."""
    if not re.fullmatch(r"[0-9a-f-]{36}", website_id):
        raise ValueError("bad website id")
    sql = f"""
SELECT
  (SELECT count(DISTINCT e.session_id) FROM website_event e JOIN session s ON s.session_id = e.session_id
     WHERE e.website_id = '{website_id}' AND e.created_at > now() - interval '{int(ONLINE_WINDOW.total_seconds())} seconds'
       AND NOT ({EXA_PATTERN})),
  (SELECT count(*) FROM session s WHERE s.website_id = '{website_id}' AND NOT ({EXA_PATTERN})),
  (SELECT to_char(min(created_at) AT TIME ZONE 'Asia/Shanghai', 'YYYY-MM-DD') FROM session WHERE website_id = '{website_id}');
"""
    cmd = [
        "docker", "exec", "-i", container, "sh", "-c",
        'psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -At -F "|" -v ON_ERROR_STOP=1',
    ]
    out = subprocess.run(cmd, input=sql, capture_output=True, text=True, timeout=30, check=True).stdout.strip()
    online, total, since = out.splitlines()[-1].split("|")
    return {"online": int(online), "total": int(total), "since": since}


# ---------------------------------------------------------------- output


def build_public(state: Dict, people: Optional[Dict], now: datetime) -> Dict:
    totals = state.get("agent_totals", {})
    online_names = sorted({name for _t, name in state.get("agent_recent", [])})
    top = sorted(totals.items(), key=lambda kv: (-kv[1], kv[0]))[:8]
    return {
        "online": {
            "humans": people["online"] if people else None,
            "agents": len(online_names),
            "agent_names": online_names,
        },
        "total": {
            "visitors": people["total"] if people else None,
            "agent_requests": sum(totals.values()),
            "agent_user_requests": int(state.get("agent_user_requests", 0)),
        },
        "agents_top": top,
        "since": {"visitors": (people or {}).get("since") or state.get("people_since"), "agents": state.get("agents_since")},
        "updated_at": now.astimezone(timezone.utc).isoformat(timespec="seconds"),
    }


def write_atomic(path: Path, data: Dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=path.parent, prefix=".site-stats-", suffix=".json")
    with os.fdopen(fd, "w", encoding="utf-8") as fh:
        json.dump(data, fh, ensure_ascii=False, separators=(",", ":"))
    os.chmod(tmp, 0o644)
    os.replace(tmp, path)


def run(args: argparse.Namespace, now: Optional[datetime] = None) -> Dict:
    now = now or datetime.now(timezone.utc)
    state_path = Path(args.state)
    state = json.loads(state_path.read_text()) if state_path.exists() else {}
    state.setdefault("agents_since", now.astimezone(timezone(timedelta(hours=8))).strftime("%Y-%m-%d"))

    lines, state["cursor"] = read_new_lines(Path(args.log), state.get("cursor", {}))
    update_agents(state, lines, now)

    people = None
    if not args.no_umami:
        try:
            people = umami_people(args.website_id, args.container)
            state["people_last"] = people
            state["people_since"] = people["since"]
        except Exception as exc:  # keep the last good numbers rather than publishing zeros
            print(f"umami query failed: {type(exc).__name__}: {exc}", file=sys.stderr)
            last = state.get("people_last")
            people = {"online": None, "total": last["total"], "since": last.get("since")} if last else None

    public = build_public(state, people, now)
    write_atomic(Path(args.out), public)
    write_atomic(state_path, state)
    return public


def main(argv: Optional[List[str]] = None) -> int:
    home = Path.home() / "site-stats"
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    p.add_argument("--log", default="/var/log/nginx/quant.hfthnu.com.access.log")
    p.add_argument("--out", default="/var/lib/site-stats/site-stats.json")
    p.add_argument("--state", default=str(home / "state.json"))
    p.add_argument("--website-id", default="ed0af5b9-1111-4553-a42e-54cc0ddaeeca")
    p.add_argument("--container", default="umami-db-1")
    p.add_argument("--no-umami", action="store_true", help="skip the Umami query (for tests)")
    args = p.parse_args(argv)
    public = run(args)
    print(json.dumps(public, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
