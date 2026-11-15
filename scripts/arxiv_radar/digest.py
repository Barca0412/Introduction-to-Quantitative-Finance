"""S9 weekly digest (design doc S9): a Chinese draft of "this week in AI x finance".

    python -m scripts.arxiv_radar.digest [--week 2026-11-09] [--facts-only]

1. Facts, computed here (no LLM): papers the site shows that were published in the
   week, the week before, counts per finance domain and method, risers (same rule as
   trends.py), and up to 5 candidate papers per domain (relevance x 10 + freshness +
   code) with their Chinese TL;DR, key points, venue and link.
2. Draft, written by the LLM from those facts only. Every link in the draft must be one
   of the candidates' links and every number must come from the facts; a draft that
   breaks this is rejected and asked again (twice), else only the facts are written.

Output: docs/arxiv/weekly/<ISO year>-W<week>.md marked "机器起草，待人工审核" and
data/digest/<week>.facts.json. Nothing is published: the draft is reviewed in a PR.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import logging
import re
from collections import Counter
from datetime import date, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

from .config import BASE_DIR, DATA_DIR, LLM_API_KEY
from .enrich import taxonomy
from . import leaders
from .site_filter import site_visible
from .storage import load_papers
from .trends import TRENDS_SINCE, representative_score, rising, week_of

logger = logging.getLogger(__name__)
WEEKLY_DIR = BASE_DIR / "docs" / "arxiv" / "weekly"
FACTS_DIR = DATA_DIR / "digest"
PER_DOMAIN = 5


def _zh(key: str, kind: str) -> str:
    return next((i["zh"] for i in taxonomy()[kind] if i["id"] == key), key)


def first_complete_week() -> str:
    first = week_of(TRENDS_SINCE)
    return first if first >= TRENDS_SINCE else (date.fromisoformat(first) + timedelta(days=7)).isoformat()


def last_complete_week(today: Optional[date] = None) -> str:
    """Monday of the latest week that ended before today."""
    today = today or date.today()
    return (today - timedelta(days=today.weekday() + 7)).isoformat()


def link_of(paper: Dict[str, Any]) -> str:
    return paper.get("abs_link") or f"https://arxiv.org/abs/{paper['id']}"


def collect_facts(papers: List[Dict[str, Any]], week: str) -> Dict[str, Any]:
    shown = [p for p in papers if site_visible(p)]
    this = [p for p in shown if week_of(p["published_date"]) == week]
    prev_week = (date.fromisoformat(week) - timedelta(days=7)).isoformat()
    # The week before counts only if it is a whole week of collected data.
    before = ([p for p in shown if week_of(p["published_date"]) == prev_week]
              if prev_week >= first_complete_week() else None)
    newest = max((p["published_date"][:10] for p in this), default=week)

    # History for the risers: only whole weeks since the data is complete (trends.py),
    # so weeks filled only by older papers added from the venue library do not count.
    weeks = [w for w in ((date.fromisoformat(week) - timedelta(days=7 * k)).isoformat() for k in range(4, -1, -1))
             if w >= first_complete_week()]
    weekly_domain = {w: Counter() for w in weeks}
    for p in shown:
        w = week_of(p["published_date"])
        if w in weekly_domain:
            weekly_domain[w].update(p.get("finance_domains") or [])

    candidates: Dict[str, List[Dict[str, Any]]] = {}
    for domain in sorted({d for p in this for d in p.get("finance_domains") or []}):
        group = sorted((p for p in this if domain in (p.get("finance_domains") or [])),
                       key=lambda p: -representative_score(p, newest))[:PER_DOMAIN]
        candidates[_zh(domain, "finance_domains")] = [{
            "title": p["title"], "link": link_of(p), "relevance": p.get("relevance"),
            "tldr_zh": p.get("tldr_zh", ""), "points_zh": p.get("points_zh") or {},
            "venue": (p.get("venue") or {}).get("name"), "code": bool((p.get("reproducibility") or {}).get("code")),
            "institutions": [i.get("zh") or i.get("name") for i in (p.get("institutions") or [])][:3],
        } for p in group]

    who = who_facts(this)
    return {
        "week": week, "week_end": (date.fromisoformat(week) + timedelta(days=6)).isoformat(),
        "papers": len(this), "papers_previous_week": len(before) if before is not None else None,
        "core_papers": sum(1 for p in this if p.get("relevance") == 3),
        "domains": {_zh(k, "finance_domains"): n for k, n in Counter(d for p in this for d in p.get("finance_domains") or []).most_common()},
        "methods": {_zh(k, "methods"): n for k, n in Counter(m for p in this for m in p.get("methods") or []).most_common()},
        "rising_domains": [{**r, "name": _zh(r["id"], "finance_domains")} for r in rising(weekly_domain, weeks, {})],
        "history_weeks": len(weeks) - 1,
        "who": who,
        "candidates": candidates,
    }


def who_facts(papers: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Institutions, companies, countries and active authors of the week (leaders.py rules)."""
    if not papers:
        return {}
    people = leaders.People()
    rows = leaders._per_paper(papers, people)
    names: Dict[str, Counter] = {}
    person_inst: Dict[str, Counter] = {}
    info: Dict[str, Dict[str, Any]] = {}
    for row in rows:
        for key, inst in row["inst_records"].items():
            info.setdefault(key, {"label": leaders._institution_label(inst), "name": inst.get("name", ""),
                                  "type": inst.get("type", ""), "country": inst.get("country", "")})
        for person, name, own in row["authors"]:
            names.setdefault(person, Counter())[name] += 1
            person_inst.setdefault(person, Counter()).update(info[k]["label"] for k in own)
    lists = leaders._leader_lists(rows, names, person_inst, info)
    return {
        "papers_with_institutions": sum(1 for r in rows if r["inst_records"]),
        "institutions": [{"name": i["name"], "type": i["type_zh"], "n": i["n"]} for i in lists["institutions"] if i["n"] >= 2][:8],
        "companies": [{"name": i["name"], "n": i["n"]} for i in lists["companies"]][:6],
        "countries": [{"name": c["name"], "n": c["n"]} for c in lists["countries"]][:6],
        "authors_with_2_or_more": [{"name": a["name"], "institution": a["institution"], "n": a["n"]}
                                   for a in lists["authors"] if a["n"] >= 2][:6],
        "collaboration": {"只有高校": lists["collaboration"]["education"], "只有企业": lists["collaboration"]["company"],
                          "校企合作": lists["collaboration"]["mixed"], "其他类型机构": lists["collaboration"]["other"],
                          "未查到机构": lists["collaboration"]["unknown"]},
        "cross_country_papers": lists["cross_country"]["papers"],
    }


PROMPT = """你在为中文的金融从业者和学生写一份 AI × 金融论文周报。下面是本周的统计和候选论文（JSON）。

只用这些材料写，不要补充材料里没有的事实、数字、论文或机构。写成 Markdown：

## 本周概况
用 2–3 句话：本周网站收录多少篇、上周多少篇（papers_previous_week 为 null 时说明"上周数据不完整，不作比较"）、相关度 3 的核心论文多少篇、哪几个金融领域最多。
如果 history_weeks 少于 4，说明"数据刚开始积累，趋势仅供参考"，不要写"升温"。

## 值得关注的方向
2–3 个方向（来自 domains 或 rising_domains），每个方向一段，引用 1–2 篇该方向候选论文，
用 [论文标题](链接) 的格式，链接只能用材料里的 link。

## 谁在做
2–3 句，只用材料里 who 的数字：本周最活跃的机构（篇数 ≥2 的）、有哪些企业、主要来自哪些国家和地区、
校企合作有几篇。机构用材料里的中文名。不要评价机构水平。

## 本周必读
3–5 篇，从候选论文里选。每篇一个小标题 `### [论文标题](链接)`，下面 2–3 句：做了什么、结论是什么、为什么值得读。
有发表去向的写上（如"KDD 2026"），有开源代码的说明。

要求：讲人话，不用"本文"开头，不写宣传腔；数字一律照抄材料。只输出 Markdown 正文，不要前言。

材料：
{facts}"""


def check_draft(draft: str, facts: Dict[str, Any]) -> List[str]:
    """Problems that make the draft unusable: links not in the facts, numbers not in them."""
    links = {c["link"] for group in facts["candidates"].values() for c in group}
    problems = [f"unknown link {url}" for url in re.findall(r"\]\((https?://[^)\s]+)\)", draft) if url not in links]
    allowed = {str(v) for v in (facts["papers"], facts["papers_previous_week"], facts["core_papers"]) if v is not None}
    allowed |= {str(n) for n in list(facts["domains"].values()) + list(facts["methods"].values())}
    who = facts.get("who") or {}
    allowed |= {str(x["n"]) for key in ("institutions", "companies", "countries", "authors_with_2_or_more")
                for x in who.get(key) or []}
    allowed |= {str(v) for v in (who.get("collaboration") or {}).values()}
    for key in ("papers_with_institutions", "cross_country_papers"):
        if who.get(key) is not None:
            allowed.add(str(who[key]))
    for text in re.findall(r"(\d+)\s*篇", draft):
        if text not in allowed:
            problems.append(f"number {text} 篇 not in the facts")
    if "## 本周必读" not in draft:
        problems.append("missing section 本周必读")
    return problems


async def draft_with_llm(facts: Dict[str, Any]) -> Optional[str]:
    from .llm_processor import LLMClient

    async with LLMClient(LLM_API_KEY, 1) as client:
        hint = ""
        for _ in range(3):
            messages = [{"role": "user", "content": PROMPT.format(facts=json.dumps(facts, ensure_ascii=False, indent=1)) + hint}]
            # The client asks for JSON; wrap the Markdown so the response format is honoured.
            messages[0]["content"] += '\n\n以 JSON 返回：{"markdown": "..."}'
            reply = await client.call_llm(messages)
            try:
                draft = json.loads(reply)["markdown"]
            except (json.JSONDecodeError, KeyError, TypeError):
                hint = "\n\n上一次没有按要求返回 JSON。"
                continue
            problems = check_draft(draft, facts)
            if not problems:
                return draft
            logger.warning("Draft rejected: %s", problems[:5])
            hint = "\n\n上一稿有问题，请改正：" + "；".join(problems[:10])
    return None


def facts_markdown(facts: Dict[str, Any]) -> str:
    """A plain listing when there is no LLM draft (or for --facts-only)."""
    lines = ["## 本周概况", "",
             f"本周收录 {facts['papers']} 篇（" + (f"上周 {facts['papers_previous_week']} 篇" if facts["papers_previous_week"] is not None
                                              else "上周数据不完整，不作比较") + f"），其中核心论文 {facts['core_papers']} 篇。", "",
             ""]
    who = facts.get("who") or {}
    if who:
        inst = "、".join(f"{i['name']}（{i['n']} 篇）" for i in who.get("institutions") or []) or "没有机构超过 1 篇"
        comp = "、".join(f"{i['name']}（{i['n']} 篇）" for i in who.get("companies") or []) or "无"
        ctry = "、".join(f"{c['name']} {c['n']} 篇" for c in who.get("countries") or [])
        lines += ["## 谁在做", "", f"- 机构：{inst}", f"- 企业：{comp}", f"- 国家和地区：{ctry}",
                  f"- 合作方式：" + "，".join(f"{k} {v} 篇" for k, v in who["collaboration"].items()), ""]
    lines += ["## 候选论文", ""]
    for domain, group in facts["candidates"].items():
        lines += [f"### {domain}", ""]
        lines += [f"- [{c['title']}]({c['link']})：{c['tldr_zh']}" for c in group]
        lines.append("")
    return "\n".join(lines)


def write(week: str, body: str, facts: Dict[str, Any], drafted: bool) -> Path:
    year, number, _ = date.fromisoformat(week).isocalendar()
    path = WEEKLY_DIR / f"{year}-W{number:02d}.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    note = "机器起草，待人工审核" if drafted else "仅为数据清单，尚未起草"
    header = (f"---\ntitle: AI × 金融论文周报 {year} 年第 {number} 周（{facts['week']} 至 {facts['week_end']}）\n"
              f"description: FinPaperRadar 周报，{note}。\n---\n\n"
              f"# AI × 金融论文周报 · {year} 年第 {number} 周\n\n"
              f"> {facts['week']} 至 {facts['week_end']}。{note}。统计口径：网站收录的论文"
              f"（大模型判定相关度 ≥2、用了 AI 方法）。\n\n")
    path.write_text(header + body.strip() + "\n", encoding="utf-8")
    return path


def main(argv: Optional[List[str]] = None) -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--week", help="Monday of the week (default: the last complete week)")
    parser.add_argument("--facts-only", action="store_true", help="no LLM: write the facts and a plain listing")
    args = parser.parse_args(argv)

    papers = load_papers().get("papers", [])
    week = args.week or last_complete_week()
    facts = collect_facts(papers, week)
    FACTS_DIR.mkdir(parents=True, exist_ok=True)
    (FACTS_DIR / f"{week}.facts.json").write_text(json.dumps(facts, ensure_ascii=False, indent=1), encoding="utf-8")

    draft = None
    if not args.facts_only:
        if not LLM_API_KEY:
            raise SystemExit("LLM_API_KEY is not set: use --facts-only, or export the key.")
        draft = asyncio.run(draft_with_llm(facts))
    path = write(week, draft or facts_markdown(facts), facts, drafted=bool(draft))
    print(f"{'Draft' if draft else 'Facts listing'} written to {path} ({facts['papers']} papers)")


if __name__ == "__main__":
    main()
