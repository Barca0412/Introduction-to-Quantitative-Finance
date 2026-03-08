"""
LLM processing module for LLM-Finance-Radar.
Handles paper analysis using DashScope API (通义千问).
"""

import asyncio
import ast
import functools
import json
import logging
import socket
from typing import Dict, Any, Optional, List

import aiohttp

from .config import (
    DASHSCOPE_API_KEY,
    DASHSCOPE_API_URL,
    MODEL_NAME,
    DISABLE_THINKING,
    MAX_CONCURRENT,
    MAX_RETRIES,
    REQUEST_TIMEOUT,
    PREDEFINED_TAGS,
    PAPER_ANALYSIS_PROMPT,
)

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
        "retrieval",
        "knowledge graph",
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
    return any(term in text for term in terms)


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


class DashScopeClient:
    """Async HTTP client for DashScope API."""

    def __init__(self, api_key: str, max_concurrent: int = MAX_CONCURRENT):
        if not api_key:
            raise ValueError("DASHSCOPE_API_KEY is required for LLM processing")
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
        """Call DashScope API with retry logic.

        Args:
            messages: List of message dicts with 'role' and 'content'

        Returns:
            LLM response text

        Raises:
            Exception: If all retry attempts fail
        """
        async with self.semaphore:
            if self.session is None:
                raise RuntimeError("DashScopeClient session has not been initialized")

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

            if DISABLE_THINKING and MODEL_NAME.startswith("glm-"):
                payload["thinking"] = {"type": "disabled"}

            async with self.session.post(
                DASHSCOPE_API_URL,
                headers=headers,
                json=payload,
                timeout=aiohttp.ClientTimeout(total=REQUEST_TIMEOUT),
            ) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(f"API error {response.status}: {error_text}")

                data = await response.json()
                return data["choices"][0]["message"]["content"]


def parse_llm_response(response_text: str) -> Dict[str, Any]:
    """
    Parse LLM JSON response and validate fields.

    Args:
        response_text: Raw LLM response

    Returns:
        Parsed dictionary with tags, keywords, and summary_zh

    Raises:
        ValueError: If response cannot be parsed or is invalid
    """
    # Try to extract JSON from response
    response_text = response_text.strip()
    response_text = response_text.removeprefix("```json").removeprefix("```")
    response_text = response_text.removesuffix("```").strip()

    # Find JSON in case there's extra text
    start_idx = response_text.find("{")
    end_idx = response_text.rfind("}")

    if start_idx != -1 and end_idx != -1:
        json_str = response_text[start_idx:end_idx + 1]
    else:
        json_str = response_text

    try:
        parsed = json.loads(json_str)
    except json.JSONDecodeError as e:
        repaired = (
            json_str.replace("\n", " ")
            .replace("\t", " ")
            .replace(" null", " None")
            .replace(": null", ": None")
            .replace(" true", " True")
            .replace(": true", ": True")
            .replace(" false", " False")
            .replace(": false", ": False")
        )
        try:
            parsed = ast.literal_eval(repaired)
        except Exception:
            raise ValueError(f"Failed to parse JSON: {e}")

    # Validate required fields
    result = {
        "tags": parsed.get("tags", []),
        "keywords": parsed.get("keywords", []),
        "summary_zh": parsed.get("summary_zh", ""),
    }

    # Validate tags
    if not isinstance(result["tags"], list):
        result["tags"] = []
    # Filter to only valid tags
    valid_tags = set(PREDEFINED_TAGS.keys())
    result["tags"] = [t for t in result["tags"] if t in valid_tags]

    # Validate keywords
    if not isinstance(result["keywords"], list):
        result["keywords"] = []
    result["keywords"] = [str(k).strip() for k in result["keywords"] if str(k).strip()]
    result["keywords"] = result["keywords"][:5]

    # Validate summary
    if not isinstance(result["summary_zh"], str):
        result["summary_zh"] = ""

    return result


async def process_paper(
    paper: Dict[str, Any],
    client: DashScopeClient
) -> Dict[str, Any]:
    """
    Process a single paper with LLM to extract tags, keywords, and Chinese summary.

    Args:
        paper: Paper dictionary with at least 'title' and 'abstract'
        client: DashScopeClient instance

    Returns:
        Paper dictionary with added 'tags', 'keywords', and 'summary_zh'
    """
    title = paper.get("title", "")
    abstract = paper.get("abstract", "")

    if not title or not abstract:
        return paper

    # Build prompt using the improved template from config
    prompt = PAPER_ANALYSIS_PROMPT.format(
        title=title,
        abstract=abstract
    )

    messages = [
        {"role": "system", "content": "You are an expert AI/Finance research analyst who carefully evaluates whether papers actually focus on financial applications of AI."},
        {"role": "user", "content": prompt}
    ]

    try:
        response_text = await client.call_llm(messages)
        llm_data = parse_llm_response(response_text)
        llm_data["tags"] = validate_tags_for_paper(paper, llm_data["tags"])

        # Update paper with LLM extracted data
        paper["tags"] = llm_data["tags"]
        paper["keywords"] = llm_data["keywords"]
        paper["summary_zh"] = llm_data["summary_zh"]

        logger.info(f"Processed paper: {paper['id']}")
    except Exception as e:
        logger.error(f"Error processing paper {paper.get('id', 'unknown')}: {type(e).__name__}: {e!r}")
        # Set default values on error
        paper["tags"] = []
        paper["keywords"] = []
        paper["summary_zh"] = ""

    return paper


async def process_papers_batch(
    papers: List[Dict[str, Any]],
    concurrency: int = MAX_CONCURRENT
) -> List[Dict[str, Any]]:
    """
    Process a batch of papers concurrently.

    Args:
        papers: List of papers to process
        concurrency: Maximum number of concurrent LLM calls

    Returns:
        List of processed papers
    """
    if not DASHSCOPE_API_KEY:
        logger.warning("DASHSCOPE_API_KEY is not configured; skipping LLM enrichment")
        return [
            {
                **paper,
                "tags": list(paper.get("tags", [])),
                "keywords": list(paper.get("keywords", [])),
                "summary_zh": str(paper.get("summary_zh", "")),
            }
            for paper in papers
        ]

    async with DashScopeClient(DASHSCOPE_API_KEY, concurrency) as client:
        tasks = [process_paper(paper.copy(), client) for paper in papers]
        results = await asyncio.gather(*tasks)

    return results


def process_papers_sync(papers: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Synchronous wrapper for processing papers.

    Args:
        papers: List of papers to process

    Returns:
        List of processed papers
    """
    return asyncio.run(process_papers_batch(papers))
