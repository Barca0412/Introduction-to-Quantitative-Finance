"""Venue and discipline (design doc 4.3.6).

From the venue the authors wrote (``venue_mention`` from the LLM, taken from the arXiv
comment) or arXiv's ``journal_ref``, find the conference or journal in vocab/venues.yaml.
When there is none, guess the discipline from the authors' departments and institutions
(S6 ``affiliation_raw`` / ``institutions``), never from the arXiv category: the trials
showed q-fin primary papers are mostly published in CS venues.

Per paper (papers with the v2 enrichment):
  venue             {id, name, kind, discipline, status, year, source, text} or None
  team_background   cs | finance-econ | mixed | unknown
  discipline        cs | finance-econ | interdisciplinary | other | unknown
  discipline_basis  venue | team | none
"""

from __future__ import annotations

import functools
import re
from collections import Counter
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

import yaml

VENUES_FILE = Path(__file__).resolve().parent / "vocab" / "venues.yaml"

_WORKSHOP = re.compile(r"\bworkshop\b|\bsymposium\b|\bw/s\b", re.I)
_ACCEPTED = re.compile(r"accepted|to appear|forthcoming|camera.?ready|in press", re.I)
_PUBLISHED = re.compile(r"published|proceedings|\bvol(ume)?\.?\s*\d|\bpp\.|\bpages?\s+\d|\bno\.\s*\d", re.I)
_YEAR = re.compile(r"\b(19[89]\d|20[0-4]\d)\b|['’](\d{2})\b")

# Department / institution wording -> team background (S6 raw text and names).
_CS = re.compile(
    r"computer|computing|informatics|artificial intelligence|\bai\b (lab|research|institute)|machine learning|"
    r"electrical|electronic|software|data science|information (science|technology|engineering)|automation|"
    r"robotics|intelligent|\bcs\b|\beecs\b|google|microsoft|deepmind|openai|meta ai|nvidia|amazon|alibaba|"
    r"tencent|baidu|bytedance|huawei|\bai lab", re.I)
_FIN = re.compile(
    r"financ|economic|business school|school of business|management school|school of management|accounting|"
    r"banking|\bbank\b|actuar|insurance|federal reserve|central bank|securities|asset management|capital|"
    r"investment|hedge fund|\bfund\b|wharton|booth|sloan|kellogg|haas|stern school|insead|london business", re.I)


@functools.lru_cache(maxsize=1)
def venue_table() -> List[Dict[str, Any]]:
    with open(VENUES_FILE, encoding="utf-8") as fh:
        entries = yaml.safe_load(fh) or []
    ids = [e["id"] for e in entries]
    if len(ids) != len(set(ids)):
        raise ValueError("duplicate venue ids")
    for entry in entries:
        entry["_re"] = re.compile(entry["match"], re.I)
    return entries


def _year(text: str) -> Optional[int]:
    found = _YEAR.search(text or "")
    if not found:
        return None
    return int(found.group(1)) if found.group(1) else 2000 + int(found.group(2))


def detect_venue(text: str, source: str) -> Optional[Dict[str, Any]]:
    """Venue from one piece of text. ``source``: comment | journal-ref."""
    text = " ".join(str(text or "").split())
    if not text:
        return None
    entry = next((e for e in venue_table() if e["_re"].search(text)), None)
    workshop = bool(_WORKSHOP.search(text))
    if entry is None:
        # A venue we do not know yet: kept as written, listed for the weekly review.
        if not (workshop or re.search(r"conference|journal|proceedings|transactions|accepted|published", text, re.I)):
            return None
        return {"id": None, "name": text[:120], "kind": "workshop" if workshop else "unknown",
                "discipline": "unknown", "status": "accepted", "year": _year(text), "source": source, "text": text[:200]}
    if entry["kind"] == "working-paper":
        status = "working-paper"
    elif source == "journal-ref" or (_PUBLISHED.search(text) and not _ACCEPTED.search(text)):
        status = "published"
    else:
        status = "accepted"
    return {
        "id": entry["id"], "name": entry["name"],
        "kind": "workshop" if workshop and entry["kind"] == "conference" else entry["kind"],
        "discipline": entry["discipline"], "status": status, "year": _year(text),
        "source": source, "text": text[:200],
    }


def team_background(paper: Dict[str, Any]) -> str:
    lines = list(paper.get("affiliation_raw") or [])
    lines += [i.get("name", "") for i in paper.get("institutions") or [] if isinstance(i, dict)]
    text = " ; ".join(lines)
    if not text.strip():
        return "unknown"
    cs, fin = bool(_CS.search(text)), bool(_FIN.search(text))
    if cs and fin:
        return "mixed"
    return "cs" if cs else ("finance-econ" if fin else "unknown")


_TEAM_TO_DISCIPLINE = {"cs": "cs", "finance-econ": "finance-econ", "mixed": "interdisciplinary"}


def classify_paper(paper: Dict[str, Any]) -> None:
    venue = detect_venue(paper.get("journal_ref", ""), "journal-ref") or detect_venue(paper.get("venue_mention", ""), "comment")
    team = team_background(paper)
    paper["venue"] = venue
    paper["team_background"] = team
    if venue and venue.get("discipline") not in (None, "unknown"):
        paper["discipline"], paper["discipline_basis"] = venue["discipline"], "venue"
    elif team in _TEAM_TO_DISCIPLINE:
        paper["discipline"], paper["discipline_basis"] = _TEAM_TO_DISCIPLINE[team], "team"
    else:
        paper["discipline"], paper["discipline_basis"] = "unknown", "none"


def classify_all(papers: Iterable[Dict[str, Any]]) -> Dict[str, Any]:
    """Classify every v2-enriched paper; report counts and unknown venues."""
    done = 0
    discipline, basis = Counter(), Counter()
    unknown_venues: Counter = Counter()
    with_venue = 0
    for paper in papers:
        if paper.get("relevance") is None:
            continue
        classify_paper(paper)
        done += 1
        discipline[paper["discipline"]] += 1
        basis[paper["discipline_basis"]] += 1
        if paper["venue"]:
            with_venue += 1
            if paper["venue"]["id"] is None:
                unknown_venues[paper["venue"]["name"]] += 1
    return {"papers": done, "with_venue": with_venue, "discipline": dict(discipline),
            "basis": dict(basis), "unknown_venues": unknown_venues.most_common(20)}
