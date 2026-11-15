"""Which papers the site lists (decided 2026-11-15): scored by the LLM at least
SITE_MIN_RELEVANCE, using an AI/ML method, not withdrawn. Used by the site data builder
and by the README status block."""

from __future__ import annotations

from typing import Any, Dict

from .config import AI_METHODS, SITE_MIN_RELEVANCE, SITE_REQUIRE_AI_METHOD


def site_visible(
    paper: Dict[str, Any],
    min_relevance: int = SITE_MIN_RELEVANCE,
    require_ai: bool = SITE_REQUIRE_AI_METHOD,
) -> bool:
    """Scored by the LLM as relevant enough, uses an AI/ML method, not withdrawn."""
    relevance = paper.get("relevance")
    return (
        isinstance(relevance, int)
        and not isinstance(relevance, bool)
        and relevance >= min_relevance
        and not paper.get("withdrawn")
        and (not require_ai or any(m in AI_METHODS for m in paper.get("methods") or []))
    )
