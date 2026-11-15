"""Leaderboards and detail pages for institutions and authors (site data, agg/).

  agg/leaders.json                periods (30d, 90d, year, all) x lists: institutions,
                                  companies, authors, countries, collaboration mix
  agg/institution/<id>.json       an institution with >= 2 papers: its papers, domains,
                                  methods, frequent co-institutions and authors
  agg/author/<id>.json            an author with >= 2 papers: papers, institutions,
                                  domains, frequent co-authors

People are told apart by identity, not by name: OpenAlex author id, else ORCID, else
the keyed e-mail fingerprint (institutions.email_hash), else the name. Ids that share an
ORCID or a fingerprint are one person (OpenAlex sometimes splits a person). Only the
site's papers are counted (site_visible).
"""

from __future__ import annotations

import json
import re
import shutil
from collections import Counter, defaultdict
from datetime import date, timedelta
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

TOP = 50
GRID_INSTITUTIONS = 15
TEAM_MIN_PAPERS = 2   # an author needs >= 2 papers, a pair >= 2 joint papers
TEAM_MIN_SIZE = 3
DETAIL_MIN_PAPERS = 2

COUNTRY_ZH = {
    "CN": "中国大陆", "US": "美国", "GB": "英国", "HK": "中国香港", "SG": "新加坡", "KR": "韩国", "FR": "法国",
    "CA": "加拿大", "AE": "阿联酋", "JP": "日本", "AU": "澳大利亚", "NL": "荷兰", "DE": "德国", "CH": "瑞士",
    "IT": "意大利", "ES": "西班牙", "IN": "印度", "TW": "中国台湾", "MO": "中国澳门", "SA": "沙特阿拉伯",
    "IE": "爱尔兰", "SE": "瑞典", "GR": "希腊", "IL": "以色列", "BR": "巴西", "TR": "土耳其", "VN": "越南",
    "BG": "保加利亚", "AT": "奥地利", "BE": "比利时", "DK": "丹麦", "FI": "芬兰", "NO": "挪威", "PL": "波兰",
    "PT": "葡萄牙", "RU": "俄罗斯", "MY": "马来西亚", "TH": "泰国", "ID": "印度尼西亚", "NZ": "新西兰",
}
TYPE_ZH = {"education": "高校", "company": "企业", "government": "政府机构", "facility": "研究机构",
           "nonprofit": "非营利机构", "healthcare": "医疗机构", "funder": "资助机构", "archive": "档案机构"}


def _slug(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", (text or "").lower()).strip("-")[:60] or "unknown"


def _authors(paper: Dict[str, Any]) -> List[str]:
    return [a.get("name", "") if isinstance(a, dict) else str(a) for a in paper.get("authors") or []]


class People:
    """Union-find over author identities: OpenAlex id, ORCID, e-mail fingerprint, name."""

    def __init__(self) -> None:
        self.parent: Dict[str, str] = {}

    def find(self, key: str) -> str:
        self.parent.setdefault(key, key)
        while self.parent[key] != key:
            self.parent[key] = self.parent[self.parent[key]]
            key = self.parent[key]
        return key

    def union(self, a: str, b: str) -> None:
        ra, rb = self.find(a), self.find(b)
        if ra != rb:
            # Prefer an OpenAlex id as the representative (stable, public).
            if rb.startswith("A") and not ra.startswith("A"):
                ra, rb = rb, ra
            self.parent[rb] = ra

    def key_for(self, ident: Dict[str, str], name: str) -> str:
        keys = []
        if ident.get("openalex"):
            keys.append(ident["openalex"])
        if ident.get("orcid"):
            keys.append("orcid:" + ident["orcid"])
        if ident.get("email_hash"):
            keys.append("email:" + ident["email_hash"])
        if not keys:
            keys.append("name:" + _slug(name))
        for other in keys[1:]:
            self.union(keys[0], other)
        return self.find(keys[0])


def _institution_label(inst: Dict[str, Any]) -> str:
    # OpenAlex adds the country to some company names: "Didi Chuxing (China)".
    name = inst.get("zh") or inst.get("short") or inst.get("name", "")
    return re.sub(r"\s*\((China|United States|United Kingdom|South Korea|Japan|Germany|France|Singapore|"
                  r"Canada|India|Switzerland|Netherlands|Australia|Hong Kong|Taiwan)\)$", "", name)


def _per_paper(papers: List[Dict[str, Any]], people: People) -> List[Dict[str, Any]]:
    """For each paper: its institutions (key, record) and its authors (person key, name, institution keys)."""
    rows = []
    for paper in papers:
        insts = paper.get("institutions") or []
        inst_keys = [(i.get("ror") or "name:" + _slug(i.get("name", ""))) for i in insts]
        ids = paper.get("author_ids") or []
        affs = paper.get("author_affiliations") or []
        authors = []
        for n, name in enumerate(_authors(paper)):
            ident = ids[n] if n < len(ids) else {}
            person = people.key_for(ident or {}, name)
            own = [inst_keys[i] for i in (affs[n] if n < len(affs) else []) if i < len(inst_keys)]
            authors.append((person, name, own))
        rows.append({"paper": paper, "inst_records": dict(zip(inst_keys, insts)), "authors": authors})
    _merge_same_name(rows, people)
    # Resolve every person key again: unions made later in the loop may have merged them.
    for row in rows:
        row["authors"] = [(people.find(p), name, own) for p, name, own in row["authors"]]
    return rows


def _norm_name(name: str) -> str:
    return re.sub(r"[^a-z]+", " ", (name or "").lower()).strip()


def _merge_same_name(rows: List[Dict[str, Any]], people: People) -> None:
    """OpenAlex often gives a new paper a fresh author id before it joins the person's
    profile. Join two ids with the same name when they share an institution or a
    co-author and their ORCIDs do not differ; same name alone never joins."""
    info: Dict[str, Dict[str, set]] = defaultdict(lambda: {"names": set(), "orcid": set(), "inst": set(), "co": set()})
    for row in rows:
        paper = row["paper"]
        ids = paper.get("author_ids") or []
        for n, (person, name, own) in enumerate(row["authors"]):
            entry = info[people.find(person)]
            entry["names"].add(_norm_name(name))
            orcid = (ids[n] if n < len(ids) else {}).get("orcid") if n < len(ids) else None
            if orcid:
                entry["orcid"].add(orcid)
            entry["inst"].update(own)
            entry["co"].update(_norm_name(other) for p, other, _ in row["authors"] if p != person)
    by_name: Dict[str, List[str]] = defaultdict(list)
    for key, entry in info.items():
        for name in entry["names"]:
            if name:
                by_name[name].append(key)
    for keys in by_name.values():
        changed = True
        while changed:  # greedy: keep joining until no pair qualifies
            changed = False
            roots = list(dict.fromkeys(people.find(k) for k in keys))
            for i, a in enumerate(roots):
                for b in roots[i + 1:]:
                    ea, eb = info[a], info[b]
                    if ea["orcid"] and eb["orcid"] and not ea["orcid"] & eb["orcid"]:
                        continue
                    if ea["inst"] & eb["inst"] or ea["co"] & eb["co"]:
                        people.union(a, b)
                        root = people.find(a)
                        merged = {f: ea[f] | eb[f] for f in ea}
                        info[root] = merged
                        changed = True
                        break
                if changed:
                    break


def _leader_lists(rows: List[Dict[str, Any]], names: Dict[str, Counter], person_inst: Dict[str, Counter],
                  inst_info: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    inst_n, inst_core, person_n, person_core, country_n = Counter(), Counter(), Counter(), Counter(), Counter()
    mix, pairs = Counter(), Counter()
    cross = 0
    for row in rows:
        core = row["paper"].get("relevance") == 3
        keys = list(row["inst_records"])
        for key in keys:
            inst_n[key] += 1
            inst_core[key] += core
        codes = sorted({inst_info[k]["country"] for k in keys if inst_info[k]["country"]})
        for code in codes:
            country_n[code] += 1
        if len(codes) > 1:
            cross += 1
            pairs.update(f"{a}-{b}" for i, a in enumerate(codes) for b in codes[i + 1:])
        for person in {p for p, _, _ in row["authors"]}:
            person_n[person] += 1
            person_core[person] += core
        types = {inst_info[k]["type"] for k in keys if inst_info[k]["type"]}
        mix["unknown" if not keys else "mixed" if {"education", "company"} <= types
            else "company" if types == {"company"} else "education" if types == {"education"} else "other"] += 1

    def inst_entry(key: str) -> Dict[str, Any]:
        info = inst_info[key]
        return {"id": key, "name": info["label"], "name_en": info["name"], "type": info["type"],
                "type_zh": TYPE_ZH.get(info["type"], ""), "country": info["country"],
                "n": inst_n[key], "core": inst_core[key]}

    ranked = sorted(inst_n, key=lambda k: (-inst_n[k], -inst_core[k], inst_info[k]["label"]))
    grid_rows = ranked[:GRID_INSTITUTIONS]
    grid = {k: Counter() for k in grid_rows}
    for row in rows:
        for key in row["inst_records"]:
            if key in grid:
                grid[key].update(row["paper"].get("finance_domains") or [])
    domains = _domain_order()
    return {
        "papers": len(rows),
        "institutions": [inst_entry(k) for k in ranked[:TOP]],
        "companies": [inst_entry(k) for k in ranked if inst_info[k]["type"] == "company"][:TOP],
        "authors": [{"id": p, "name": names[p].most_common(1)[0][0],
                     "institution": inst_info[top]["label"] if (top := _top(person_inst[p])) else "",
                     "institution_id": top or "",
                     "n": person_n[p], "core": person_core[p]}
                    for p in sorted(person_n, key=lambda p: (-person_n[p], -person_core[p]))[:TOP]],
        "countries": [{"code": c, "name": COUNTRY_ZH.get(c, c), "n": n} for c, n in country_n.most_common(TOP)],
        # Papers per institution (the top GRID_INSTITUTIONS) and finance domain (ids in taxonomy.yaml).
        "institution_domain": {"domains": domains,
                               "rows": [{"id": k, "name": inst_info[k]["label"], "counts": [grid[k][d] for d in domains]}
                                        for k in grid_rows]},
        "totals": {"institutions": len(inst_n), "authors": len(person_n),
                   "companies": sum(1 for k in inst_n if inst_info[k]["type"] == "company"), "countries": len(country_n)},
        # other: institutions found but not only universities / companies (e.g. a government
        # lab); unknown: no institution found for the paper.
        "collaboration": {"education": mix["education"], "company": mix["company"],
                          "mixed": mix["mixed"], "other": mix["other"], "unknown": mix["unknown"]},
        "cross_country": {"papers": cross, "pairs": [{"pair": k, "names": [COUNTRY_ZH.get(c, c) for c in k.split("-")], "n": n}
                                                     for k, n in pairs.most_common(10)]},
    }


def _domain_order() -> List[str]:
    """The 12 finance domains in taxonomy.yaml order (all of them, zeros included)."""
    from .enrich import taxonomy

    return [item["id"] for item in taxonomy()["finance_domains"]]


def _top(counter: Counter) -> str:
    return counter.most_common(1)[0][0] if counter else ""


def build(papers: Iterable[Dict[str, Any]], out_dir: Path, today: Optional[date] = None) -> Dict[str, Any]:
    papers = [p for p in papers if p.get("published_date")]
    out_dir.mkdir(parents=True, exist_ok=True)
    people = People()
    rows = _per_paper(papers, people)

    names: Dict[str, Counter] = defaultdict(Counter)
    person_inst: Dict[str, Counter] = defaultdict(Counter)
    inst_info: Dict[str, Dict[str, Any]] = {}
    for row in rows:
        for key, inst in row["inst_records"].items():
            inst_info.setdefault(key, {"label": _institution_label(inst), "name": inst.get("short") or inst.get("name", ""),
                                       "type": inst.get("type", ""), "country": inst.get("country", "")})
        for person, name, own in row["authors"]:
            names[person][name] += 1
            for key in own:
                person_inst[person][key] += 1

    newest = max((p["published_date"][:10] for p in papers), default=(today or date.today()).isoformat())
    end = date.fromisoformat(newest)
    periods = {
        "30d": (end - timedelta(days=29)).isoformat(),
        "90d": (end - timedelta(days=89)).isoformat(),
        str(end.year): f"{end.year}-01-01",
        "all": "",
    }
    leaders = {"generated_for": newest, "rule": "people by OpenAlex id / ORCID / e-mail fingerprint, else name",
               "periods": {name: {"since": since, **_leader_lists(
                   [r for r in rows if r["paper"]["published_date"][:10] >= since], names, person_inst, inst_info)}
                   for name, since in periods.items()}}
    (out_dir / "leaders.json").write_text(json.dumps(leaders, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")

    # Detail pages for institutions and authors with >= DETAIL_MIN_PAPERS papers.
    by_inst: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    by_person: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    for row in rows:
        for key in row["inst_records"]:
            by_inst[key].append(row)
        for person in {p for p, _, _ in row["authors"]}:
            by_person[person].append(row)

    def summary(group: List[Dict[str, Any]]) -> Dict[str, Any]:
        ordered = sorted(group, key=lambda r: r["paper"]["published_date"], reverse=True)
        return {
            "papers": [r["paper"]["id"] for r in ordered],
            "core": sum(1 for r in group if r["paper"].get("relevance") == 3),
            "domains": Counter(d for r in group for d in r["paper"].get("finance_domains") or []).most_common(),
            "methods": Counter(m for r in group for m in r["paper"].get("methods") or []).most_common(),
        }

    def inst_ref(key: str, n: int) -> Dict[str, Any]:
        # page: file name under institution/ when the institution has its own page, else "".
        return {"id": key, "name": inst_info[key]["label"], "n": n,
                "page": _slug(key) if len(by_inst[key]) >= DETAIL_MIN_PAPERS else ""}

    def person_ref(person: str, n: int) -> Dict[str, Any]:
        return {"id": person, "name": names[person].most_common(1)[0][0], "n": n,
                "page": _slug(person) if len(by_person[person]) >= DETAIL_MIN_PAPERS else ""}

    written = {"institution": 0, "author": 0}
    for sub in written:  # drop pages of earlier builds (people merged, papers dropped)
        shutil.rmtree(out_dir / sub, ignore_errors=True)
    for key, group in by_inst.items():
        if len(group) < DETAIL_MIN_PAPERS:
            continue
        co_inst = Counter(k for r in group for k in r["inst_records"] if k != key)
        authors = Counter(p for r in group for p, _, own in r["authors"] if key in own)
        info = inst_info[key]
        payload = {"id": key, "name": info["label"], "name_en": info["name"], "type": info["type"],
                   "type_zh": TYPE_ZH.get(info["type"], ""), "country": info["country"],
                   "country_zh": COUNTRY_ZH.get(info["country"], info["country"]), **summary(group),
                   "co_institutions": [inst_ref(k, n) for k, n in co_inst.most_common(10)],
                   "authors": [person_ref(p, n) for p, n in authors.most_common(10)]}
        path = out_dir / "institution" / f"{_slug(key)}.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
        written["institution"] += 1
    for person, group in by_person.items():
        if len(group) < DETAIL_MIN_PAPERS:
            continue
        coauthors = Counter(p for r in group for p, _, _ in r["authors"] if p != person)
        payload = {"id": person, "name": names[person].most_common(1)[0][0],
                   "spellings": [n for n, _ in names[person].most_common()],
                   "institutions": [inst_ref(k, n) for k, n in person_inst[person].most_common(5)], **summary(group),
                   "coauthors": [person_ref(p, n) for p, n in coauthors.most_common(10)],
                   "openalex": f"https://openalex.org/{person}" if re.fullmatch(r"A\d+", person) else ""}
        path = out_dir / "author" / f"{_slug(person)}.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
        written["author"] += 1

    teams = build_teams(rows, names, person_inst, inst_info, by_person)
    (out_dir / "teams.json").write_text(json.dumps(
        {"rule": f"authors with >= {TEAM_MIN_PAPERS} papers, linked when two wrote >= {TEAM_MIN_PAPERS} papers "
                 f"together; groups of >= {TEAM_MIN_SIZE}", "teams": teams},
        ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    return {"periods": {k: v["papers"] for k, v in leaders["periods"].items()}, "details": written, "teams": len(teams)}


def build_teams(rows, names, person_inst, inst_info, by_person) -> List[Dict[str, Any]]:
    """Stable groups: connected authors who keep writing together (see TEAM_* rules)."""
    active = {p for p, group in by_person.items() if len(group) >= TEAM_MIN_PAPERS}
    joint: Counter = Counter()
    for row in rows:
        members = sorted({p for p, _, _ in row["authors"] if p in active})
        joint.update((a, b) for i, a in enumerate(members) for b in members[i + 1:])
    links: Dict[str, set] = defaultdict(set)
    for (a, b), n in joint.items():
        if n >= TEAM_MIN_PAPERS:
            links[a].add(b)
            links[b].add(a)
    seen, teams = set(), []
    for start in sorted(links):
        if start in seen:
            continue
        stack, group = [start], set()
        while stack:
            p = stack.pop()
            if p not in group:
                group.add(p)
                stack.extend(links[p] - group)
        seen |= group
        if len(group) < TEAM_MIN_SIZE:
            continue
        # The team's papers: at least two members on the author list.
        papers = [r for r in {id(r): r for p in group for r in by_person[p]}.values()
                  if len(group & {p for p, _, _ in r["authors"]}) >= 2]
        inst = Counter(k for p in group for k in person_inst[p].elements())
        teams.append({
            "members": sorted(({"id": p, "name": names[p].most_common(1)[0][0], "n": len(by_person[p]),
                                "page": _slug(p)} for p in group), key=lambda m: -m["n"]),
            "papers": len(papers),
            "core": sum(1 for r in papers if r["paper"].get("relevance") == 3),
            "institutions": [{"id": k, "name": inst_info[k]["label"], "n": n} for k, n in inst.most_common(3)],
            "domains": Counter(d for r in papers for d in r["paper"].get("finance_domains") or []).most_common(3),
            "paper_ids": [r["paper"]["id"] for r in sorted(papers, key=lambda r: r["paper"]["published_date"], reverse=True)],
        })
    return sorted(teams, key=lambda t: (-t["papers"], -len(t["members"])))
