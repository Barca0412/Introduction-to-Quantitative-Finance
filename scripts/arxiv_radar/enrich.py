"""S3 enrichment v2: one LLM call per paper -> relevance, five-way classification,
Chinese TL;DR and key points, keywords, market, reproducibility, venue mention.

This module is pure: it builds the prompt, validates the model's JSON and writes the
result into a paper record. The HTTP call and retries live in llm_processor.py.

Design: pipeline design doc, sections 3.2, 4.3 and S4; taxonomy in vocab/taxonomy.yaml.
"""

from __future__ import annotations

import ast
import functools
import json
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import yaml

from .config import PREDEFINED_TAGS

# Bump when the prompt, the taxonomy or the validation rules change: papers enriched
# with an older version are redone the next time they are fetched.
ENRICH_VERSION = "s3-v2.1"
# s3-v2.1 (2026-11-15): after the first real-model trial: method vs system, finance-only
# models and benchmarks are relevance 3, "general" never for price models, report QA
# is corporate-finance.
SCHEMA_VERSION = 2
# Give up on a paper after this many failed enrichments with the current version.
MAX_ENRICH_ATTEMPTS = 3

TAXONOMY_FILE = Path(__file__).resolve().parent / "vocab" / "taxonomy.yaml"


class EnrichError(ValueError):
    """The model's answer cannot be used; the message is fed back on retry."""


@functools.lru_cache(maxsize=1)
def taxonomy() -> Dict[str, Any]:
    with open(TAXONOMY_FILE, encoding="utf-8") as fh:
        data = yaml.safe_load(fh)
    for key in ("paper_types", "task_types", "finance_domains", "methods", "data_markets"):
        ids = [item["id"] for item in data[key]]
        if len(ids) != len(set(ids)):
            raise ValueError(f"duplicate ids in taxonomy.{key}")
    return data


def ids(key: str) -> List[str]:
    return [item["id"] for item in taxonomy()[key]]


# --------------------------------------------------------------------------
# Prompt
# --------------------------------------------------------------------------

_SYSTEM = (
    "You classify research papers for Chinese finance practitioners and students who "
    "follow AI x finance research. Be precise: a wrong 'finance' label is worse than a "
    "missing one. Answer with one JSON object only."
)

# Few-shot answers from the trial rounds (design doc appendix A). Short on purpose.
_EXAMPLES = [
    {
        "paper": "AlphaGen (2306.12964): RL generates synergistic formulaic alpha factor collections; tested on Chinese stocks.",
        "answer": {"relevance": 3, "paper_type": "method", "task_types": ["signal-mining"],
                   "finance_domains": ["asset-pricing"], "methods": ["rl"], "data_market": ["a-share"]},
    },
    {
        "paper": "Temporal Relational Ranking for Stock Prediction: ranks stocks for next-day returns with a graph model.",
        "answer": {"relevance": 3, "paper_type": "method", "task_types": ["forecasting"],
                   "finance_domains": ["asset-pricing"], "methods": ["graph", "deep-ts"]},
        "why": "cross-sectional ranking -> asset-pricing even at a one-day horizon",
    },
    {
        "paper": "Can GPT models be Financial Analysts? Evaluates ChatGPT/GPT-4 on mock CFA exam questions.",
        "answer": {"relevance": 3, "paper_type": "empirical", "task_types": ["understanding"],
                   "finance_domains": ["general"], "methods": ["llm"]},
        "why": "evaluates existing models, releases no new benchmark -> empirical",
    },
    {
        "paper": "ClimateBert: a language model pre-trained on general climate-related text.",
        "answer": {"relevance": 1, "paper_type": "method", "task_types": ["understanding"],
                   "finance_domains": ["corporate-finance"], "methods": ["llm"]},
        "why": "generic climate text, no investment or disclosure use stated -> relevance 1",
    },
    {
        "paper": "Chronos: a general pre-trained probabilistic time-series model; abstract never mentions finance.",
        "answer": {"relevance": 0, "paper_type": "method", "task_types": ["forecasting"],
                   "finance_domains": [], "methods": ["deep-ts", "llm"]},
    },
]


def _menu(key: str) -> str:
    return "\n".join(f'  - "{item["id"]}" ({item["zh"]}): {item.get("en", "")}'.rstrip(": ") for item in taxonomy()[key])


@functools.lru_cache(maxsize=1)
def _instructions() -> str:
    tax = taxonomy()
    relevance = "\n".join(f"  {score} ({v['zh']}): {v['en']}" for score, v in sorted(tax["relevance"].items(), reverse=True))
    rules = "\n".join(f"  - {rule}" for rule in tax["rules"])
    legacy = ", ".join(f'"{tag}"' for tag in PREDEFINED_TAGS)
    examples = "\n".join(
        f"  - {ex['paper']}\n    -> {json.dumps(ex['answer'], ensure_ascii=False)}"
        + (f"  ({ex['why']})" if ex.get("why") else "")
        for ex in _EXAMPLES
    )
    return f"""Return this JSON object:
{{
  "relevance": 0-3,
  "relevance_reason_zh": "一句中文理由",
  "paper_type": one id,
  "task_types": 0-2 ids,
  "finance_domains": 0-3 ids,
  "methods": 1-3 ids,
  "tags": 0-3 ids from the legacy tag list,
  "keywords": [{{"text": "...", "kind": "finance" or "tech"}}, ...] (3-6),
  "data_market": ids,
  "reproducibility": {{"code": true/false/null, "data_public": true/false/null}},
  "tldr_zh": "...",
  "points_zh": {{"problem": "...", "method": "...", "result": "...", "limitation": "..."}},
  "venue_mention": "..." or null,
  "withdrawn": true/false
}}

RELEVANCE to AI x finance:
{relevance}

PAPER_TYPE (exactly one):
{_menu("paper_types")}

TASK_TYPES (what the AI is asked to do; 1-2, may be empty only if relevance <= 1):
{_menu("task_types")}

FINANCE_DOMAINS (0-3; empty when relevance is 0):
{_menu("finance_domains")}

METHODS (1-3):
{_menu("methods")}

DATA_MARKET (markets or data the paper uses; ["none"] if not stated):
{_menu("data_markets")}

RULES for unclear cases:
{rules}

TAGS: legacy research tags kept for the old pages, choose 0-3 that are truly central: {legacy}.
Use "ai-finance" only when relevance >= 2.

KEYWORDS: 3-6 specific English terms in their common spelling, both finance objects
(kind "finance") and techniques (kind "tech"); no abbreviation-plus-full-name pairs, no
broad words such as "machine learning" or "deep learning". Relevance 0 may have only tech.

CHINESE WRITING:
  - tldr_zh: one sentence, 40-80 Chinese characters, starting with what was done and what it found; never start with "本文".
  - points_zh: 1-2 sentences each. Only state what the abstract supports; otherwise write "摘要未说明".
  - relevance_reason_zh: one short sentence.

REPRODUCIBILITY: code = true only if code is said to be released (a link or "code is available");
data_public likewise; null when the abstract and comment do not say.
VENUE_MENTION: the comment's own words about where it is published or accepted, e.g.
"Accepted by KDD '23, ADS track"; null if none. Page counts and figures are not venues.

EXAMPLES (abbreviated answers):
{examples}
"""


def build_messages(paper: Dict[str, Any], error_hint: Optional[str] = None) -> List[Dict[str, str]]:
    parts = [
        f"Title: {paper.get('title', '')}",
        f"Abstract: {paper.get('abstract', '')}",
        f"arXiv categories: {', '.join(paper.get('categories', []))}",
    ]
    if paper.get("comment"):
        parts.append(f"arXiv comment: {paper['comment']}")
    if paper.get("journal_ref"):
        parts.append(f"Journal reference: {paper['journal_ref']}")
    user = "\n".join(parts) + "\n\n" + _instructions()
    if error_hint:
        user += f"\n\nYour previous answer was rejected: {error_hint}. Fix it and answer again."
    return [{"role": "system", "content": _SYSTEM}, {"role": "user", "content": user}]


# --------------------------------------------------------------------------
# Parsing and validation
# --------------------------------------------------------------------------

def extract_json(text: str) -> Dict[str, Any]:
    """Pull one JSON object out of a model reply (tolerates fences and stray text)."""
    text = (text or "").strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
    start, end = text.find("{"), text.rfind("}")
    body = text[start:end + 1] if start != -1 and end != -1 else text
    try:
        parsed = json.loads(body)
    except json.JSONDecodeError as exc:
        repaired = re.sub(r"\bnull\b", "None", re.sub(r"\btrue\b", "True", re.sub(r"\bfalse\b", "False", body)))
        try:
            parsed = ast.literal_eval(repaired.replace("\n", " "))
        except Exception:
            raise EnrichError(f"not valid JSON ({exc})") from None
    if not isinstance(parsed, dict):
        raise EnrichError("the answer is not a JSON object")
    return parsed


def _id_list(value: Any, allowed: List[str], limit: int, field: str, warnings: List[str]) -> List[str]:
    if value is None:
        return []
    if isinstance(value, str):
        value = [value]
    if not isinstance(value, list):
        warnings.append(f"{field}: not a list")
        return []
    out: List[str] = []
    for item in value:
        item = str(item).strip()
        if item not in allowed:
            warnings.append(f"{field}: unknown id {item!r} dropped")
        elif item not in out:
            out.append(item)
    if len(out) > limit:
        warnings.append(f"{field}: {len(out)} ids, kept the first {limit}")
        out = out[:limit]
    return out


def _bool_or_none(value: Any) -> Optional[bool]:
    if isinstance(value, bool):
        return value
    if isinstance(value, str) and value.strip().lower() in ("true", "false"):
        return value.strip().lower() == "true"
    return None


def _text(value: Any) -> str:
    return value.strip() if isinstance(value, str) else ""


_WITHDRAWN = re.compile(r"\bwithdr[ae]wn?\b|\bwithdrawal\b", re.IGNORECASE)


def comment_says_withdrawn(comment: str) -> bool:
    return bool(_WITHDRAWN.search(comment or ""))


def validate(raw: Dict[str, Any], paper: Dict[str, Any]) -> Tuple[Dict[str, Any], List[str]]:
    """Check and clean one answer. Raises EnrichError for answers that must be retried;
    returns (result, warnings) where warnings list the soft fixes that were applied."""
    warnings: List[str] = []

    relevance = raw.get("relevance")
    if isinstance(relevance, str) and relevance.strip().isdigit():
        relevance = int(relevance.strip())
    if isinstance(relevance, bool) or not isinstance(relevance, int) or not 0 <= relevance <= 3:
        raise EnrichError(f"relevance must be an integer 0-3, got {raw.get('relevance')!r}")

    paper_type = _text(raw.get("paper_type"))
    if paper_type not in ids("paper_types"):
        raise EnrichError(f"paper_type must be one of {ids('paper_types')}, got {raw.get('paper_type')!r}")

    tldr = _text(raw.get("tldr_zh"))
    if not tldr:
        raise EnrichError("tldr_zh is empty")
    if not 15 <= len(tldr) <= 150:
        warnings.append(f"tldr_zh: {len(tldr)} characters")

    task_types = _id_list(raw.get("task_types"), ids("task_types"), 2, "task_types", warnings)
    domains = _id_list(raw.get("finance_domains"), ids("finance_domains"), 3, "finance_domains", warnings)
    methods = _id_list(raw.get("methods"), ids("methods"), 3, "methods", warnings) or ["other"]
    markets = _id_list(raw.get("data_market"), ids("data_markets"), 4, "data_market", warnings)
    if len(markets) > 1 and "none" in markets:
        markets.remove("none")

    if relevance >= 2 and not task_types:
        raise EnrichError("relevance >= 2 needs at least one task_types id")
    if relevance == 0 and domains:
        warnings.append("finance_domains: cleared because relevance is 0")
        domains = []
    if "general" in domains and len(domains) > 1:
        warnings.append("finance_domains: 'general' dropped next to specific domains")
        domains = [d for d in domains if d != "general"]

    tags = _id_list(raw.get("tags"), list(PREDEFINED_TAGS), 3, "tags", warnings)
    if relevance >= 2 and "ai-finance" not in tags:
        tags = ["ai-finance"] + tags[:2]
    if relevance < 2 and "ai-finance" in tags:
        tags = [t for t in tags if t != "ai-finance"]

    keywords: List[Dict[str, str]] = []
    for item in raw.get("keywords") or []:
        if isinstance(item, str):
            item = {"text": item, "kind": "tech"}
        if not isinstance(item, dict):
            continue
        text = _text(item.get("text"))
        kind = item.get("kind") if item.get("kind") in ("finance", "tech") else "tech"
        if text and text.lower() not in {k["text"].lower() for k in keywords}:
            keywords.append({"text": text, "kind": kind})
    if not keywords:
        warnings.append("keywords: none")
    keywords = keywords[:6]

    points_raw = raw.get("points_zh") if isinstance(raw.get("points_zh"), dict) else {}
    points = {key: _text(points_raw.get(key)) or "摘要未说明" for key in ("problem", "method", "result", "limitation")}

    repro_raw = raw.get("reproducibility") if isinstance(raw.get("reproducibility"), dict) else {}
    reproducibility = {"code": _bool_or_none(repro_raw.get("code")), "data_public": _bool_or_none(repro_raw.get("data_public"))}

    venue = _text(raw.get("venue_mention")) or None
    withdrawn = _bool_or_none(raw.get("withdrawn")) is True or comment_says_withdrawn(paper.get("comment", ""))

    result = {
        "relevance": relevance,
        "relevance_reason_zh": _text(raw.get("relevance_reason_zh")),
        "paper_type": paper_type,
        "task_types": task_types,
        "finance_domains": domains,
        "methods": methods,
        "tags": tags,
        "keywords_raw": keywords,
        "data_market": markets,
        "reproducibility": reproducibility,
        "tldr_zh": tldr,
        "points_zh": points,
        "venue_mention": venue,
        "withdrawn": withdrawn,
    }
    return result, warnings


def consistency_flags(paper: Dict[str, Any]) -> List[str]:
    """S4: suspicious combinations, recorded for the quality report, never auto-fixed."""
    flags: List[str] = []
    relevance = paper.get("relevance")
    if relevance is None:
        return flags
    if relevance >= 2 and not paper.get("finance_domains"):
        flags.append("relevant-without-domain")
    if relevance == 0 and any(str(c).startswith("q-fin.") for c in paper.get("categories", [])):
        flags.append("q-fin-but-irrelevant")
    if relevance >= 2 and not any(k.get("kind") == "finance" for k in paper.get("keywords_raw", [])):
        flags.append("relevant-without-finance-keyword")
    return flags


def summary_paragraph(tldr: str, points: Dict[str, str]) -> str:
    """Old summary_zh field: TL;DR plus the four points, for pages that predate v2."""
    labels = (("problem", "问题"), ("method", "方法"), ("result", "结果"), ("limitation", "局限"))
    extra = "".join(f"{zh}：{points[key]}" + ("" if points[key].endswith("。") else "。")
                    for key, zh in labels if points.get(key) and points[key] != "摘要未说明")
    return tldr + ("" if tldr.endswith("。") else "。") + extra


def apply_result(paper: Dict[str, Any], result: Dict[str, Any], warnings: List[str]) -> Dict[str, Any]:
    paper.update(result)
    paper["keywords"] = [k["text"] for k in result["keywords_raw"]]
    paper["summary_zh"] = summary_paragraph(result["tldr_zh"], result["points_zh"])
    paper["schema_version"] = SCHEMA_VERSION
    paper["stage_versions"] = {**(paper.get("stage_versions") or {}), "enrich": ENRICH_VERSION}
    paper["attempts"] = {**(paper.get("attempts") or {}), "enrich": 0, "enrich_version": ENRICH_VERSION}
    paper["last_error"] = ""
    paper["enrich_warnings"] = warnings
    paper["quality_flags"] = consistency_flags(paper)
    return paper


def record_failure(paper: Dict[str, Any], error: str) -> Dict[str, Any]:
    """Keep whatever the paper already had; count the failed attempt for this version."""
    attempts = dict(paper.get("attempts") or {})
    if attempts.get("enrich_version") != ENRICH_VERSION:
        # Failures counted under an older version do not count against this one.
        attempts = {**attempts, "enrich": 0, "enrich_version": ENRICH_VERSION}
    attempts["enrich"] = int(attempts.get("enrich", 0) or 0) + 1
    paper["attempts"] = attempts
    paper["last_error"] = error[:300]
    return paper


def needs_enrich(paper: Dict[str, Any]) -> bool:
    """True when the paper has no current-version enrichment and has not failed too often."""
    if (paper.get("stage_versions") or {}).get("enrich") == ENRICH_VERSION:
        return False
    attempts = paper.get("attempts") or {}
    if attempts.get("enrich_version") == ENRICH_VERSION:
        return int(attempts.get("enrich", 0) or 0) < MAX_ENRICH_ATTEMPTS
    return True
