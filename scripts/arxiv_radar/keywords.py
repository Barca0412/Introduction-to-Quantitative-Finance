"""S5 keyword normalisation (design doc 4.5): map the LLM's keywords to the standard
keywords in vocab/keywords.yaml, so trends and keyword pages count one concept once.

Deterministic and cheap: re-run on every enriched paper each run, so editing the YAML
takes effect on the next run without any LLM call.

Per paper (only papers with ``keywords_raw`` from the v2 enrichment):
  keywords_norm  [{id, en, zh, kind, raw, new}]  ``new`` = no standard keyword matched
  keywords       standard English names (or the cleaned new term), at most 6 (old field)
"""

from __future__ import annotations

import functools
import re
from collections import Counter
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

import yaml

VOCAB_FILE = Path(__file__).resolve().parent / "vocab" / "keywords.yaml"
MAX_KEYWORDS = 6


@functools.lru_cache(maxsize=1)
def vocabulary() -> List[Dict[str, Any]]:
    with open(VOCAB_FILE, encoding="utf-8") as fh:
        entries = yaml.safe_load(fh) or []
    seen = set()
    for entry in entries:
        if entry["id"] in seen:
            raise ValueError(f"duplicate keyword id {entry['id']}")
        seen.add(entry["id"])
        entry["_patterns"] = [re.compile(p) for p in entry["patterns"]]
    return entries


def clean(text: str) -> str:
    """Lower case, hyphens/slashes/underscores as spaces, single spaces, no edge marks."""
    text = re.sub(r"[-_/]+", " ", str(text or "").lower())
    text = re.sub(r"[()\[\]{}\"'`]", " ", text)
    return re.sub(r"\s+", " ", text).strip(" .,;:")


def match(text: str) -> Tuple[Optional[Dict[str, Any]], str]:
    """(standard entry or None, cleaned text) for one keyword."""
    cleaned = clean(text)
    for entry in vocabulary():
        if any(p.search(cleaned) for p in entry["_patterns"]):
            return entry, cleaned
    return None, cleaned


def normalize_paper_keywords(paper: Dict[str, Any]) -> bool:
    """Fill keywords_norm and keywords from keywords_raw. Returns whether it changed."""
    raw = paper.get("keywords_raw")
    if not raw:
        return False
    norm: List[Dict[str, Any]] = []
    for item in raw:
        text = item.get("text", "") if isinstance(item, dict) else str(item)
        kind = item.get("kind", "tech") if isinstance(item, dict) else "tech"
        entry, cleaned = match(text)
        if not cleaned:
            continue
        if entry:
            record = {"id": entry["id"], "en": entry["en"], "zh": entry["zh"], "kind": entry["kind"], "raw": text, "new": False}
        else:
            record = {"id": cleaned.replace(" ", "-"), "en": cleaned, "zh": "", "kind": kind, "raw": text, "new": True}
        if record["id"] not in {r["id"] for r in norm}:
            norm.append(record)
    norm = norm[:MAX_KEYWORDS]
    names = [r["en"] for r in norm]
    changed = norm != paper.get("keywords_norm") or names != paper.get("keywords")
    paper["keywords_norm"], paper["keywords"] = norm, names
    return changed


def normalize_all(papers: Iterable[Dict[str, Any]]) -> Dict[str, Any]:
    """Normalise every paper that has v2 keywords; report coverage and top new terms."""
    total = matched = changed = 0
    new_terms: Counter = Counter()
    for paper in papers:
        if not paper.get("keywords_raw"):
            continue
        changed += normalize_paper_keywords(paper)
        for record in paper["keywords_norm"]:
            total += 1
            if record["new"]:
                new_terms[record["en"]] += 1
            else:
                matched += 1
    return {
        "keywords": total,
        "matched": matched,
        "coverage": round(matched / total, 3) if total else 0.0,
        "papers_changed": changed,
        "top_new_terms": new_terms.most_common(30),
    }
