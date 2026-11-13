"""Focus scoring for AI/LLM/agent + finance papers."""

from __future__ import annotations

from typing import Any, Dict, List


FOCUS_TAG_ORDER = [
    "ai-finance",
    "agent-planning",
    "deep-research",
    "multi-agent",
    "tool-use",
    "reasoning",
    "memory",
    "rag",
    "time-series",
]

FOCUS_TAG_WEIGHTS = {
    "ai-finance": 12,
    "agent-planning": 10,
    "deep-research": 10,
    "multi-agent": 8,
    "tool-use": 8,
    "reasoning": 7,
    "memory": 6,
    "rag": 5,
    "time-series": 4,
    "benchmark": 2,
    "training-efficiency": 2,
}

FOCUS_CATEGORY_WEIGHTS = {
    "q-fin.ST": 5,
    "q-fin.CP": 5,
    "q-fin.PM": 5,
    "q-fin.TR": 5,
    "cs.CE": 3,
    "cs.MA": 3,
    "cs.AI": 2,
    "cs.CL": 2,
}

FINANCE_TERMS = [
    "finance",
    "financial",
    "trading",
    "market",
    "portfolio",
    "asset",
    "credit",
    "risk",
    "alpha",
    "return prediction",
    "stock",
    "order book",
    "quantitative finance",
    "cryptocurrency",
    "defi",
]

AGENT_TERMS = [
    "agent",
    "agentic",
    "workflow",
    "react",
    "reflection",
    "re-planning",
    "planning",
    "tool use",
    "function calling",
    "computer use",
    "browser",
    "autonomous",
]

DEEP_RESEARCH_TERMS = [
    "deep research",
    "research agent",
    "literature review",
    "survey generation",
    "evidence gathering",
    "fact-check",
    "information synthesis",
    "multi-hop",
    "report generation",
]

LLM_TERMS = [
    "llm",
    "language model",
    "large language model",
    "foundation model",
    "reasoning model",
]

FOCUS_TOPIC_LABELS = {
    "ai-finance": "AI + Finance",
    "agent-planning": "Agent Planning",
    "deep-research": "Deep Research",
}


def _paper_text(paper: Dict[str, Any]) -> str:
    parts = [
        str(paper.get("title", "")),
        str(paper.get("abstract", "")),
        " ".join(str(keyword) for keyword in paper.get("keywords", [])),
        " ".join(str(tag) for tag in paper.get("tags", [])),
    ]
    return " ".join(parts).lower()


def _contains_any(text: str, terms: List[str]) -> bool:
    return any(term in text for term in terms)


def build_focus_metadata(paper: Dict[str, Any]) -> Dict[str, Any]:
    """Derive a deterministic focus score from tags, categories, and text signals."""
    categories = [str(category) for category in paper.get("categories", [])]
    tags = [str(tag) for tag in paper.get("tags", [])]
    text = _paper_text(paper)

    matched_tags = [tag for tag in FOCUS_TAG_ORDER if tag in tags]
    matched_categories = [
        category for category in categories if category in FOCUS_CATEGORY_WEIGHTS
    ]

    finance_signal = _contains_any(text, FINANCE_TERMS) or any(
        category.startswith("q-fin.") for category in categories
    )
    agent_signal = _contains_any(text, AGENT_TERMS)
    deep_research_signal = _contains_any(text, DEEP_RESEARCH_TERMS)
    llm_signal = _contains_any(text, LLM_TERMS)

    score = sum(FOCUS_TAG_WEIGHTS.get(tag, 0) for tag in tags)
    score += sum(FOCUS_CATEGORY_WEIGHTS.get(category, 0) for category in matched_categories)

    reasons: List[str] = []
    if matched_tags:
        reasons.append("focus tags: " + ", ".join(matched_tags[:4]))
    if matched_categories:
        reasons.append("categories: " + ", ".join(matched_categories[:3]))
    if finance_signal:
        score += 4
        reasons.append("finance signal")
    if agent_signal:
        score += 4
        reasons.append("agent signal")
    if deep_research_signal:
        score += 4
        reasons.append("deep research signal")
    if llm_signal:
        score += 2
        reasons.append("llm signal")

    topics: List[str] = []
    if "ai-finance" in tags or (finance_signal and (llm_signal or agent_signal)):
        topics.append("ai-finance")
    if "agent-planning" in tags or agent_signal:
        topics.append("agent-planning")
    if "deep-research" in tags or deep_research_signal:
        topics.append("deep-research")

    primary_topic = topics[0] if topics else (matched_tags[0] if matched_tags else None)
    is_focus = score >= 10 or bool(topics) or bool(matched_tags)

    return {
        "score": score,
        "is_focus": is_focus,
        "primary_topic": primary_topic,
        "topics": topics,
        "labels": [FOCUS_TOPIC_LABELS[topic] for topic in topics if topic in FOCUS_TOPIC_LABELS],
        "matched_tags": matched_tags,
        "matched_categories": matched_categories,
        "reasons": reasons[:4],
    }
