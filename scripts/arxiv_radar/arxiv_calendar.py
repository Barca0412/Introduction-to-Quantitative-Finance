"""arXiv's announcement calendar: explain on the site why there are no new papers.

arXiv announces new submissions Sunday to Thursday at 20:00 US Eastern, not on Friday
or Saturday, and skips the evening of each date on its holiday list
(https://info.arxiv.org/help/availability.html; our copy is vocab/arxiv_holidays.yaml).
When the newest papers on the Radar stop moving because of that, readers should see
that arXiv paused, not think the Radar is broken.

``announcement_status(now, data_updated_at)`` walks back from the latest evening that
has passed in US Eastern time and collects the evenings without an announcement, up to
the last regular one. It returns ``None`` when nothing was skipped, and also when our own
data is more than ``MAX_DATA_AGE`` old: then our pipeline did not run, and the notice
must not claim the site is fine. Otherwise a dict with ``level`` ("holiday" when a
holiday or one-off deferral is among the skipped evenings, else "weekend"), the skipped
evenings, the next expected announcement and ready-made Chinese / English text, used as
is by the site (manifest.json) and the README (stats.json).
"""

from __future__ import annotations

import functools
import logging
import os
from datetime import date, datetime, time, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union
from zoneinfo import ZoneInfo

import yaml

logger = logging.getLogger(__name__)

CALENDAR_FILE = Path(__file__).resolve().parent / "vocab" / "arxiv_holidays.yaml"
EASTERN = ZoneInfo("America/New_York")
BEIJING = ZoneInfo("Asia/Shanghai")
ANNOUNCE_AT = time(20, 0)
# Sunday to Thursday (Monday = 0).
ANNOUNCE_WEEKDAYS = {6, 0, 1, 2, 3}
# Our daily run is scheduled once a day but GitHub often starts it hours late.
MAX_DATA_AGE = timedelta(hours=36)
MAX_WALK_DAYS = 14
WEEKDAY_ZH = "一二三四五六日"


@functools.lru_cache(maxsize=1)
def calendar() -> Dict[str, Any]:
    with open(CALENDAR_FILE, encoding="utf-8") as fh:
        raw = yaml.safe_load(fh) or {}
    holidays: Dict[date, Dict[str, Any]] = {}
    for entry in raw.get("holidays") or []:
        day = _as_date(entry["date"])
        if day in holidays:
            raise ValueError(f"duplicate arXiv holiday {day}")
        holidays[day] = entry
    deferred = {_as_date(entry["date"]): entry for entry in raw.get("deferred") or []}
    return {
        "source_url": raw["source_url"],
        "years": {int(y) for y in raw.get("years") or []},
        "holidays": holidays,
        "deferred": deferred,
    }


def _as_date(value: Union[str, date]) -> date:
    return value if isinstance(value, date) else date.fromisoformat(str(value))


def _as_utc(value: Union[None, str, datetime]) -> Optional[datetime]:
    """Parse our timestamps; the pipeline writes naive ISO strings meaning UTC."""
    if value is None or value == "":
        return None
    if isinstance(value, str):
        try:
            value = datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError:
            return None
    return value.replace(tzinfo=timezone.utc) if value.tzinfo is None else value.astimezone(timezone.utc)


def skip_reason(day: date) -> Optional[Tuple[str, Dict[str, Any]]]:
    """Why arXiv makes no announcement on the evening of ``day`` (US Eastern), if it doesn't."""
    cal = calendar()
    if day in cal["deferred"]:
        return "deferred", cal["deferred"][day]
    if day.weekday() not in ANNOUNCE_WEEKDAYS:
        return "weekend", {}
    if day in cal["holidays"]:
        return "holiday", cal["holidays"][day]
    return None


def _md(day: date) -> str:
    return f"{day.month} 月 {day.day} 日"


def _wd(day: date) -> str:
    return "周" + WEEKDAY_ZH[day.weekday()]


def _texts(skipped: List[Dict[str, Any]], next_et: datetime, source_url: str) -> Dict[str, str]:
    special = [s for s in skipped if s["reason"] != "weekend"]
    has_weekend = any(s["reason"] == "weekend" for s in skipped)
    next_bj = next_et.astimezone(BEIJING)
    next_line = f"下一期预计北京时间 {_md(next_bj.date())}（{_wd(next_bj.date())}）上午发布，本站当天自动更新。"

    zh_parts: List[str] = []
    en_parts: List[str] = []
    link_text = ""
    for s in sorted(special, key=lambda s: s["date"]):
        day = date.fromisoformat(s["date"])
        if s["reason"] == "holiday":
            link_text = link_text or f"arXiv 官方的 {day.year} 假期名单"
            zh_parts.append(f"{_md(day)}（{_wd(day)}）是{s['name_zh']}，在 {link_text}上，当天晚上那一期停发了")
            en_parts.append(f"no announcement on {s['date']} ({day.strftime('%a')}, {s['name_en']}, on arXiv's holiday list)")
        else:
            zh_parts.append(f"{_md(day)}（{_wd(day)}）arXiv 临时停发了一期（{s['reason_zh']}）")
            en_parts.append(f"no announcement on {s['date']} ({s.get('reason_en') or 'deferred by arXiv'})")
    if has_weekend:
        zh_parts.append("周五、周六 arXiv 本来不发新论文")
        en_parts.append("arXiv does not announce on Fridays or Saturdays")

    span = "这几天" if len(skipped) > 1 else "这一天"
    notice_zh = "；".join(zh_parts) + f"。所以{span}没有新论文，不是本站出了问题。" + next_line
    notice_en = "; ".join(en_parts)
    notice_en = notice_en[0].upper() + notice_en[1:] + (
        f". Next announcement expected {next_et.strftime('%Y-%m-%d %H:%M')} US Eastern "
        f"([arXiv schedule]({source_url}))."
    )
    short_zh = "arXiv 周五、周六不发新论文" if not special else "遇 arXiv 停发"
    return {"notice_zh": notice_zh, "notice_en": notice_en, "short_zh": short_zh, "link_text_zh": link_text}


def announcement_status(
    now: Union[None, str, datetime] = None,
    data_updated_at: Union[None, str, datetime] = None,
) -> Optional[Dict[str, Any]]:
    """The notice to show at ``now``, or None. See the module docstring."""
    now_utc = _as_utc(now) or datetime.now(timezone.utc)
    updated = _as_utc(data_updated_at)
    if updated is None or now_utc - updated > MAX_DATA_AGE:
        return None

    cal = calendar()
    now_et = now_utc.astimezone(EASTERN)
    evening = now_et.date() if now_et.time() >= ANNOUNCE_AT else now_et.date() - timedelta(days=1)

    skipped: List[Dict[str, Any]] = []
    for _ in range(MAX_WALK_DAYS):
        reason = skip_reason(evening)
        if reason is None:
            break
        kind, entry = reason
        item = {"date": evening.isoformat(), "weekday": _wd(evening), "reason": kind}
        if kind == "holiday":
            item.update(name_zh=entry["name_zh"], name_en=entry["name_en"])
        elif kind == "deferred":
            item.update(reason_zh=entry["reason_zh"], reason_en=entry.get("reason_en", ""),
                        source_url=entry.get("source_url", ""))
        skipped.append(item)
        evening -= timedelta(days=1)

    upcoming = now_et.date() if now_et.time() < ANNOUNCE_AT else now_et.date() + timedelta(days=1)
    for _ in range(MAX_WALK_DAYS):
        if skip_reason(upcoming) is None:
            break
        upcoming += timedelta(days=1)

    years = {now_et.year, upcoming.year} | {date.fromisoformat(s["date"]).year for s in skipped}
    missing = sorted(years - cal["years"])
    if missing:
        message = (f"vocab/arxiv_holidays.yaml has no arXiv holiday list for {missing}; "
                   f"copy it from {cal['source_url']}")
        logger.warning(message)
        if os.environ.get("GITHUB_ACTIONS") == "true":
            print(f"::warning title=arXiv holiday calendar::{message}")

    if not skipped:
        return None

    next_et = datetime.combine(upcoming, ANNOUNCE_AT, tzinfo=EASTERN)
    level = "holiday" if any(s["reason"] != "weekend" for s in skipped) else "weekend"
    status: Dict[str, Any] = {
        "level": level,
        "skipped": skipped,
        "next_et": next_et.isoformat(timespec="minutes"),
        "next_bj": next_et.astimezone(BEIJING).isoformat(timespec="minutes"),
        "source_url": cal["source_url"],
        "checked_at": now_utc.isoformat(timespec="seconds"),
        **_texts(skipped, next_et, cal["source_url"]),
    }
    if missing:
        status["calendar_missing_year"] = missing
    return status
