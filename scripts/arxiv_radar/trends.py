"""S8 aggregates for the trends, keyword and institution pages (design doc S8).

Written by build_site_data next to the other site files, under arxiv-data/agg/:
  weekly_keywords.json      per week, papers per standard keyword
  weekly_institutions.json  per week, papers per institution (with its type)
  rising.json               this week's risers: domains, methods, keywords, institutions
  topic/<id>.json           per finance domain and method: weekly series, top keywords,
                            institutions, authors, representative papers
  keyword/<id>.json         per standard keyword: the same, plus co-occurring keywords

Rules (design S8, shown on the page): natural weeks (Monday to Sunday) of
published_date; only whole weeks from TRENDS_SINCE on (the date the data is complete);
rise = (n - m) / sqrt(m + 1) with n = this week, m = mean of the 4 weeks before;
listed when n >= 3 and rise >= 2; "new" = absent in those 4 weeks and n >= 3.
Weekly domain / task / method counts are in stats.json "facets" (compute_stats).
"""

from __future__ import annotations

import json
import math
import os
from collections import Counter, defaultdict
from datetime import date, timedelta
from pathlib import Path
from typing import Any, Dict, Iterable, List, Tuple

TRENDS_SINCE = os.getenv("RADAR_TRENDS_SINCE", "2026-11-01")
RISE_MIN_COUNT = 3
RISE_MIN_SCORE = 2.0
HISTORY_WEEKS = 4
TOP = 10


def week_of(day: str) -> str:
    """Monday of the ISO week of a YYYY-MM-DD date."""
    d = date.fromisoformat(day[:10])
    return (d - timedelta(days=d.weekday())).isoformat()


def _keywords(paper: Dict[str, Any]) -> List[Tuple[str, str]]:
    return [(k["id"], k.get("zh") or k["en"]) for k in paper.get("keywords_norm") or [] if not k.get("new")]


def _institutions(paper: Dict[str, Any]) -> List[Tuple[str, str]]:
    out = []
    for inst in paper.get("institutions") or []:
        key = inst.get("ror") or inst.get("name", "")
        if key:
            out.append((key, inst.get("zh") or inst.get("short") or inst.get("name", "")))
    return list(dict.fromkeys(out))


def _authors(paper: Dict[str, Any]) -> List[str]:
    return [a.get("name", "") if isinstance(a, dict) else str(a) for a in paper.get("authors") or []]


def representative_score(paper: Dict[str, Any], newest: str) -> float:
    """relevance x 10 + freshness (0-5, by weeks before the newest paper) + code (2)."""
    try:
        age = (date.fromisoformat(newest) - date.fromisoformat(paper["published_date"][:10])).days
    except (KeyError, ValueError):
        age = 365
    fresh = max(0.0, 5 - age / 7)
    code = 2 if (paper.get("reproducibility") or {}).get("code") else 0
    return 10 * (paper.get("relevance") or 0) + fresh + code


def rising(weekly: Dict[str, Counter], weeks: List[str], names: Dict[str, str]) -> List[Dict[str, Any]]:
    """Risers of the last week against the HISTORY_WEEKS before it."""
    if not weeks:
        return []
    current, history = weeks[-1], weeks[-1 - HISTORY_WEEKS:-1]
    out = []
    keys = set(weekly[current])
    for key in keys:
        n = weekly[current][key]
        past = [weekly[w][key] for w in history]
        m = sum(past) / len(history) if history else 0.0
        score = (n - m) / math.sqrt(m + 1)
        new = bool(history) and not any(past)
        if n >= RISE_MIN_COUNT and (score >= RISE_MIN_SCORE or new):
            out.append({"id": key, "name": names.get(key, key), "n": n, "mean_before": round(m, 2),
                        "rise": round(score, 2), "new": new})
    return sorted(out, key=lambda r: (-r["rise"], -r["n"]))


def build(papers: Iterable[Dict[str, Any]], out_dir: Path) -> Dict[str, Any]:
    """Write the aggregate files for the given (site-visible) papers; returns a summary."""
    # Whole weeks only: a week that starts before TRENDS_SINCE would be counted partly.
    first_week = week_of(TRENDS_SINCE)
    if first_week < TRENDS_SINCE:
        first_week = (date.fromisoformat(first_week) + timedelta(days=7)).isoformat()
    papers = [p for p in papers if str(p.get("published_date", ""))[:10] >= first_week]
    out_dir.mkdir(parents=True, exist_ok=True)
    if not papers:
        summary = {"since": TRENDS_SINCE, "papers": 0, "weeks": []}
        (out_dir / "rising.json").write_text(json.dumps({**summary, "lists": {}}, ensure_ascii=False), encoding="utf-8")
        return summary

    newest = max(p["published_date"][:10] for p in papers)
    weeks = sorted({week_of(p["published_date"]) for p in papers})
    totals = Counter(week_of(p["published_date"]) for p in papers)

    dims = {
        "domain": lambda p: [(d, d) for d in p.get("finance_domains") or []],
        "method": lambda p: [(m, m) for m in p.get("methods") or []],
        "keyword": _keywords,
        "institution": _institutions,
    }
    weekly: Dict[str, Dict[str, Counter]] = {d: defaultdict(Counter) for d in dims}
    names: Dict[str, Dict[str, str]] = {d: {} for d in dims}
    members: Dict[str, Dict[str, List[Dict[str, Any]]]] = {d: defaultdict(list) for d in dims}
    inst_type: Dict[str, str] = {}
    for paper in papers:
        week = week_of(paper["published_date"])
        for dim, get in dims.items():
            for key, name in get(paper):
                weekly[dim][week][key] += 1
                names[dim][key] = name
                members[dim][key].append(paper)
        for inst in paper.get("institutions") or []:
            key = inst.get("ror") or inst.get("name", "")
            if key and inst.get("type"):
                inst_type[key] = inst["type"]

    def series(dim: str, key: str) -> List[int]:
        return [weekly[dim][w][key] for w in weeks]

    def dump(path: Path, payload: Any) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")

    keep_kw = [k for k in names["keyword"] if sum(series("keyword", k)) >= 2]  # skip one-off keywords
    dump(out_dir / "weekly_keywords.json", {
        "since": first_week, "weeks": weeks, "totals": [totals[w] for w in weeks],
        "keywords": {k: {"name": names["keyword"][k], "counts": series("keyword", k)} for k in sorted(keep_kw)},
    })
    top_inst = Counter({k: len(v) for k, v in members["institution"].items()}).most_common(200)
    dump(out_dir / "weekly_institutions.json", {
        "since": first_week, "weeks": weeks,
        "institutions": {k: {"name": names["institution"][k], "type": inst_type.get(k, ""),
                             "counts": series("institution", k)} for k, _ in top_inst},
    })
    lists = {dim: rising(weekly[dim], weeks, names[dim]) for dim in dims}
    dump(out_dir / "rising.json", {
        "since": first_week, "week": weeks[-1], "weeks_compared": weeks[-1 - HISTORY_WEEKS:-1],
        # The page should say "not enough history yet" until 4 earlier weeks exist.
        "enough_history": len(weeks) > HISTORY_WEEKS,
        "rule": "rise = (n - m) / sqrt(m + 1); n >= 3 and rise >= 2, or new", "lists": lists,
    })

    def detail(dim: str, key: str) -> Dict[str, Any]:
        group = members[dim][key]
        co = Counter(k for p in group for k, _ in _keywords(p) if not (dim == "keyword" and k == key))
        insts = Counter(i for p in group for i, _ in _institutions(p))
        authors = Counter(a for p in group for a in _authors(p) if a)
        reps = sorted(group, key=lambda p: -representative_score(p, newest))[:5]
        return {
            "id": key, "name": names[dim][key], "papers": len(group), "weeks": weeks, "counts": series(dim, key),
            "keywords": [{"id": k, "name": names["keyword"].get(k, k), "n": n} for k, n in co.most_common(TOP)],
            "institutions": [{"id": k, "name": names["institution"].get(k, k), "n": n} for k, n in insts.most_common(TOP)],
            "authors": [{"name": a, "n": n} for a, n in authors.most_common(TOP)],
            "representative": [p["id"] for p in reps],
        }

    for dim in ("domain", "method"):
        for key in names[dim]:
            dump(out_dir / "topic" / f"{key}.json", detail(dim, key))
    for key in names["keyword"]:
        dump(out_dir / "keyword" / f"{key}.json", detail("keyword", key))

    return {"since": first_week, "papers": len(papers), "weeks": weeks,
            "risers": {dim: len(v) for dim, v in lists.items()}}
