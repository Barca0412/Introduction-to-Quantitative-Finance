"""
LLM processing module for LLM-Finance-Radar.
Handles paper analysis via an OpenAI-compatible chat API (DeepSeek by default).
"""

import asyncio
import functools
import logging
import socket
from typing import Any, Awaitable, Callable, Dict, List, Optional

import aiohttp

from .config import (
    LLM_API_KEY,
    LLM_API_URL,
    THINKING_TOGGLE_PREFIXES,
    MODEL_NAME,
    DISABLE_THINKING,
    MAX_CONCURRENT,
    MAX_RETRIES,
    REQUEST_TIMEOUT,
    CHECKPOINT_EVERY,
    PREDEFINED_TAGS,
)
from . import enrich
from .utils import has_any_term

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

FINANCE_TERMS = [
    "finance",
    "financial",
    "trading",
    "market microstructure",
    "market making",
    "stock",
    "portfolio",
    "asset pricing",
    "asset allocation",
    "credit",
    "risk management",
    "fraud detection",
    "quantitative finance",
    "option pricing",
    "derivative",
    "order book",
    "earnings call",
    "sec filing",
    "cryptocurrency",
    "defi",
    "banking",
    "loan default",
    "value-at-risk",
    "alpha",
]

NON_FINANCE_TERMS = [
    "advertising",
    "advertisement",
    "ad auction",
    "auto-bidding",
    "click-through",
    "conversion rate",
    "job advertisement",
    "labour market",
    "labor market",
    "student",
    "education",
    "renewable energy",
    "e-commerce",
    "recommendation feed",
]

TAG_SIGNALS = {
    "agent-planning": [
        "agent planning",
        "planning",
        "re-planning",
        "react",
        "reasoning and acting",
        "workflow",
        "autonomous agent",
        "task decomposition",
        "goal-oriented",
        "long-horizon",
    ],
    "deep-research": [
        "deep research",
        "research agent",
        "literature review",
        "survey generation",
        "evidence gathering",
        "fact-check",
        "multi-step search",
        "information synthesis",
        "report generation",
        "knowledge synthesis",
    ],
    "tool-use": [
        "tool use",
        "tool-use",
        "function calling",
        "api",
        "browser",
        "computer use",
        "external tool",
        "tool selection",
        "tool retrieval",
        "mcp",
    ],
    "multi-agent": [
        "multi-agent",
        "multiagent",
        "multiple agents",
        "agent collaboration",
        "agent debate",
        "agent communication",
        "agent team",
        "cooperative agents",
        "marl",
        "swarm",
    ],
    "memory": [
        "memory",
        "long-term memory",
        "episodic memory",
        "working memory",
        "context window",
        "kv cache",
        "persistent memory",
        "memory bank",
        "memory stream",
    ],
    "rag": [
        "retrieval-augmented",
        "rag",
        "retrieval augmented",
        "graph rag",
        "graphrag",
        "retriever",
        "vector search",
    ],
    "reasoning": [
        "reasoning",
        "chain-of-thought",
        "tree-of-thought",
        "cot",
        "logical reasoning",
        "mathematical reasoning",
        "reasoning trace",
        "inference-time compute",
    ],
    "time-series": [
        "time series",
        "time-series",
        "forecasting",
        "temporal",
        "sequential data",
        "multivariate time series",
        "anomaly detection",
    ],
}


def _paper_text(paper: Dict[str, Any]) -> str:
    return " ".join(
        [
            str(paper.get("title", "")),
            str(paper.get("abstract", "")),
            " ".join(str(keyword) for keyword in paper.get("keywords", [])),
        ]
    ).lower()


def _has_any(text: str, terms: List[str]) -> bool:
    return has_any_term(text, terms)


def validate_tags_for_paper(paper: Dict[str, Any], tags: List[str]) -> List[str]:
    """Prune obvious false-positive tags using deterministic rules."""
    text = _paper_text(paper)
    categories = [str(category) for category in paper.get("categories", [])]

    validated: List[str] = []
    for tag in tags:
        if tag in validated:
            continue

        if tag == "ai-finance":
            has_finance_signal = _has_any(text, FINANCE_TERMS) or any(
                category.startswith("q-fin.") for category in categories
            )
            has_non_finance_signal = _has_any(text, NON_FINANCE_TERMS)
            if not has_finance_signal or (has_non_finance_signal and not any(category.startswith("q-fin.") for category in categories)):
                continue

        elif tag in TAG_SIGNALS and not _has_any(text, TAG_SIGNALS[tag]):
            continue

        validated.append(tag)

    return validated[:3]


def fallback_tags_for_paper(paper: Dict[str, Any]) -> List[str]:
    """Produce conservative navigation tags when the LLM secret is unavailable."""
    text = _paper_text(paper)
    categories = [str(category) for category in paper.get("categories", [])]
    tags: List[str] = []

    if _has_any(text, FINANCE_TERMS) or any(category.startswith("q-fin.") for category in categories):
        tags.append("ai-finance")

    for tag, signals in TAG_SIGNALS.items():
        if _has_any(text, signals):
            tags.append(tag)

    return validate_tags_for_paper(paper, tags)


# The API refuses every request with these (no balance, bad or revoked key): retrying
# a paper, or moving on to the next one, cannot help. Stop the batch instead.
FATAL_STATUSES = (401, 402, 403)


class FatalLLMError(Exception):
    """The LLM API refuses all requests (e.g. HTTP 402 Insufficient Balance)."""


class LLMBudgetExhausted(RuntimeError):
    """A batch stopped early on a FatalLLMError. ``papers`` holds the papers that were
    finished before the stop (enriched, or failed for their own reasons)."""

    def __init__(self, message: str, papers: List[Dict[str, Any]]):
        super().__init__(message)
        self.papers = papers


def async_retry(max_retries: int = 3, base_delay: float = 2.0):
    """
    Decorator for async function retry with exponential backoff.

    Args:
        max_retries: Maximum number of retry attempts
        base_delay: Base delay in seconds (doubled each retry)

    Returns:
        Decorated function
    """
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(max_retries):
                try:
                    return await func(*args, **kwargs)
                except FatalLLMError:
                    raise
                except Exception as e:
                    last_exception = e
                    if attempt < max_retries - 1:
                        delay = base_delay * (2 ** attempt)
                        await asyncio.sleep(delay)
            exception = last_exception
            if exception is None:
                raise RuntimeError("async_retry failed without capturing an exception")
            raise exception
        return wrapper
    return decorator


class LLMClient:
    """Async HTTP client for an OpenAI-compatible chat completions API."""

    def __init__(self, api_key: str, max_concurrent: int = MAX_CONCURRENT):
        if not api_key:
            raise ValueError("LLM_API_KEY is required for LLM processing")
        self.api_key = api_key
        self.max_concurrent = max_concurrent
        self.semaphore = asyncio.Semaphore(max_concurrent)
        self.session: Optional[aiohttp.ClientSession] = None

    async def __aenter__(self):
        connector = aiohttp.TCPConnector(
            limit=self.max_concurrent,
            limit_per_host=max(1, self.max_concurrent),
            ttl_dns_cache=600,
            use_dns_cache=True,
            family=socket.AF_INET,
            enable_cleanup_closed=True,
        )
        self.session = aiohttp.ClientSession(connector=connector)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    @async_retry(max_retries=MAX_RETRIES, base_delay=2.0)
    async def call_llm(self, messages: List[Dict[str, str]]) -> str:
        """Call the chat completions API with retry logic.

        Args:
            messages: List of message dicts with 'role' and 'content'

        Returns:
            LLM response text

        Raises:
            Exception: If all retry attempts fail
        """
        async with self.semaphore:
            if self.session is None:
                raise RuntimeError("LLMClient session has not been initialized")

            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            }

            payload = {
                "model": MODEL_NAME,
                "messages": messages,
                "temperature": 0.1,  # Low temperature for consistent output
                "response_format": {"type": "json_object"},
            }

            if DISABLE_THINKING and MODEL_NAME.startswith(THINKING_TOGGLE_PREFIXES):
                payload["thinking"] = {"type": "disabled"}

            async with self.session.post(
                LLM_API_URL,
                headers=headers,
                json=payload,
                timeout=aiohttp.ClientTimeout(total=REQUEST_TIMEOUT),
            ) as response:
                if response.status in FATAL_STATUSES:
                    raise FatalLLMError(f"API error {response.status}: {(await response.text())[:300]}")
                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(f"API error {response.status}: {error_text}")

                data = await response.json()
                return data["choices"][0]["message"]["content"]


# How many times one paper is re-asked when its answer fails validation (S3, 4.3.7).
VALIDATION_RETRIES = 2


async def process_paper(
    paper: Dict[str, Any],
    client: LLMClient
) -> Dict[str, Any]:
    """Enrich one paper with the v2 format (enrich.py): relevance, classification,
    Chinese TL;DR and points, keywords and more.

    An answer that fails validation is re-asked up to VALIDATION_RETRIES times with the
    reason attached. If it still fails, the paper keeps what it already had (an older
    enrichment, or rule tags), and the failure is counted so it is retried later.
    """
    if not paper.get("title") or not paper.get("abstract"):
        return paper

    error_hint: Optional[str] = None
    for _ in range(VALIDATION_RETRIES + 1):
        try:
            response_text = await client.call_llm(enrich.build_messages(paper, error_hint))
            result, warnings = enrich.validate(enrich.extract_json(response_text), paper)
        except enrich.EnrichError as exc:
            error_hint = str(exc)
            continue
        except FatalLLMError:
            raise  # not this paper's fault: the batch stops, nothing is counted
        except Exception as exc:  # HTTP errors after call_llm's own retries
            logger.error("LLM call failed for %s: %s: %r", paper.get("id", "unknown"), type(exc).__name__, exc)
            error_hint = f"{type(exc).__name__}: {exc}"
            break
        result["tags"] = validate_tags_for_paper(paper, result["tags"])
        if result["relevance"] >= 2 and "ai-finance" not in result["tags"]:
            result["tags"] = ["ai-finance"] + result["tags"][:2]
        enrich.apply_result(paper, result, warnings)
        logger.info("Processed paper %s: relevance %s", paper["id"], result["relevance"])
        return paper

    logger.error("Enrichment failed for %s: %s", paper.get("id", "unknown"), error_hint)
    enrich.record_failure(paper, error_hint or "unknown error")
    if not paper.get("tags"):
        paper["tags"] = fallback_tags_for_paper(paper)
    return paper


async def process_papers_batch(
    papers: List[Dict[str, Any]],
    concurrency: int = MAX_CONCURRENT,
    checkpoint: Optional[Callable[[List[Dict[str, Any]]], Awaitable[None]]] = None,
    checkpoint_every: Optional[int] = None,
) -> List[Dict[str, Any]]:
    """Process a batch of papers concurrently; returns them in input order.

    ``checkpoint`` is awaited with all papers finished so far after every
    ``checkpoint_every`` of them, so a crash or a stop loses at most that many.

    On a FatalLLMError (e.g. HTTP 402, no balance) no further calls are started and
    LLMBudgetExhausted is raised with the papers finished before the stop. Papers that
    were not reached are left untouched and get no failure count.
    """
    if not LLM_API_KEY:
        logger.warning(
            "LLM_API_KEY is not configured; using deterministic fallback tags"
        )
        return [
            {
                **paper,
                "tags": fallback_tags_for_paper(paper),
                "keywords": list(paper.get("keywords", [])),
                "summary_zh": str(paper.get("summary_zh", "")),
            }
            for paper in papers
        ]

    every = checkpoint_every or CHECKPOINT_EVERY
    fatal: List[str] = []
    finished: List[Dict[str, Any]] = []
    results: List[Optional[Dict[str, Any]]] = [None] * len(papers)
    queue: "asyncio.Queue[int]" = asyncio.Queue()
    for index in range(len(papers)):
        queue.put_nowait(index)

    async with LLMClient(LLM_API_KEY, concurrency) as client:

        async def worker() -> None:
            # A fixed pool of workers, each taking the next paper only while no fatal
            # error has been seen: after a 402 nothing new is sent.
            while not fatal and not queue.empty():
                index = queue.get_nowait()
                try:
                    result = await process_paper(papers[index].copy(), client)
                except FatalLLMError as exc:
                    if not fatal:
                        fatal.append(str(exc))
                        logger.error("Stopping the LLM batch: %s", exc)
                    return
                results[index] = result
                finished.append(result)
                if checkpoint and len(finished) % every == 0:
                    await checkpoint(list(finished))

        await asyncio.gather(*(worker() for _ in range(max(1, concurrency))))

    if fatal:
        raise LLMBudgetExhausted(fatal[0], finished)
    return [result for result in results if result is not None]


def process_papers_sync(papers: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Synchronous wrapper for processing papers.

    Args:
        papers: List of papers to process

    Returns:
        List of processed papers
    """
    return asyncio.run(process_papers_batch(papers))
