"""Author affiliation extraction and normalization helpers."""

from __future__ import annotations

import ast
import asyncio
import json
import logging
import re
import socket
from html import unescape
from typing import Any, Dict, List, Sequence

import aiohttp

from .config import DASHSCOPE_API_KEY
from .llm_processor import DashScopeClient


logger = logging.getLogger(__name__)

META_PATTERNS = [
    r'<meta name="citation_author_institution" content="([^"]+)"',
    r'<meta name="citation_technical_report_institution" content="([^"]+)"',
    r'<meta property="og:institution" content="([^"]+)"',
]

PLACEHOLDER_TERMS = [
    "company name",
    "location, country",
    "school of zzz",
    "institute of www",
    "department of xxx",
    "university of yyy",
    "organization=",
    "institute for clarity in documentation",
]

NOISY_TOKENS = [
    "\\institution",
    "\\email",
    "\\and",
    "\\texttt",
    "\\vspace",
    "\\centering",
    "\\begintabular",
    "\\at",
    "$^",
    "%",
]

INSTITUTION_SUFFIXES = [
    "University",
    "Institute",
    "College",
    "Academy",
    "Laboratory",
    "Lab",
    "Center",
    "Centre",
    "Hospital",
]


def clean_affiliation_text(value: str) -> str:
    """Normalize a raw affiliation string into compact plain text."""
    text = unescape(str(value or ""))
    text = text.replace("，", ",")
    text = text.replace("\\&", "&")
    text = text.replace("\\_", "_")
    text = text.replace("\\,", ",")
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\\\\", " ; ", text)
    text = re.sub(r"\\(?:email|thanks|texttt|footnotemark|footnotetext)\b[^;,.\n]*", " ", text)
    text = re.sub(r"\\(?:institution|and|centering|begintabular|endtabular|vspace|at)\b", " ", text)
    text = re.sub(r"\$\^?\d+", " ", text)
    text = re.sub(r"[%{}]", " ", text)
    text = re.sub(r"(?<=[a-z])(?=[A-Z])", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    text = text.strip(" ,;:-")
    return text[:240]


def prettify_affiliation_name(value: str) -> str:
    """Apply light deterministic cleanup after extraction/LLM normalization."""
    text = clean_affiliation_text(value)
    text = re.sub(r"\s*,\s*", ", ", text)

    suffix_pattern = "|".join(INSTITUTION_SUFFIXES)
    for prefix in ["Department", "School", "Faculty", "Institute", "Laboratory", "Center", "Centre"]:
        text = re.sub(
            rf"\b({prefix} of [A-Za-z&\- ]+?) ((?:The )?[A-Z][A-Za-z&.&-]*(?: [A-Z][A-Za-z&.&-]*){{0,4}} (?:{suffix_pattern}))\b",
            r"\1, \2",
            text,
            count=1,
        )

    text = re.sub(
        rf"((?:{suffix_pattern}))( [A-Z][a-z]+) (China|USA|UK|Australia|Canada|Germany|Austria|France|Japan|Singapore)\b",
        r"\1,\2, \3",
        text,
    )
    text = re.sub(r"\b(Hong Kong(?: SAR)?) China\b", r"\1, China", text)
    text = re.sub(r"\b([A-Z][a-z]+) China\b", r"\1, China", text)
    text = re.sub(r"\b([A-Z][a-z]+) USA\b", r"\1, USA", text)
    text = re.sub(r"\b([A-Z][a-z]+) UK\b", r"\1, UK", text)
    return text.strip(" ,;:-")


def is_placeholder_affiliation(text: str) -> bool:
    """Return whether an affiliation string is clearly placeholder/noise."""
    normalized = text.lower()
    return not normalized or any(term in normalized for term in PLACEHOLDER_TERMS)


def split_affiliation_candidates(value: Any) -> List[str]:
    """Split a stored affiliation value into likely institution strings."""
    if isinstance(value, list):
        candidates = [clean_affiliation_text(item) for item in value]
    else:
        text = clean_affiliation_text(str(value or ""))
        if not text:
            return []
        candidates = [clean_affiliation_text(part) for part in re.split(r"\s*;\s*", text)]

    deduped: List[str] = []
    for candidate in candidates:
        candidate = prettify_affiliation_name(candidate)
        if not candidate or candidate == "Unknown" or is_placeholder_affiliation(candidate):
            continue
        if candidate not in deduped:
            deduped.append(candidate)
    return deduped[:4]


def normalize_affiliation_fields(affiliation: Any, affiliations: Any = None) -> Dict[str, Any]:
    """Normalize stored affiliation fields into string + list representations."""
    candidates = split_affiliation_candidates(affiliations) + split_affiliation_candidates(affiliation)

    deduped: List[str] = []
    for candidate in candidates:
        if candidate not in deduped:
            deduped.append(candidate)

    return {
        "affiliation": "; ".join(deduped),
        "affiliations": deduped,
    }


def has_suspicious_affiliation_text(value: Any) -> bool:
    """Detect affiliation text that should be re-normalized with LLM."""
    text = str(value or "").strip()
    if not text or text == "Unknown":
        return True

    lowered = text.lower()
    if any(token in lowered for token in PLACEHOLDER_TERMS):
        return True
    if any(token in text for token in NOISY_TOKENS):
        return True
    if "\n" in text or "\\" in text:
        return True
    if text.count(";") >= 3:
        return True
    if re.search(r"[A-Za-z]China", text):
        return True
    return False


def needs_affiliation_normalization(paper: Dict[str, Any]) -> bool:
    """Return whether the paper needs affiliation extraction or cleanup."""
    raw = paper.get("affiliation") or ""
    affiliations = paper.get("affiliations") or []
    if has_suspicious_affiliation_text(raw):
        return True
    return not split_affiliation_candidates(affiliations or raw)


def build_affiliation_source_from_html(html: str) -> str:
    """Extract raw affiliation-related text from an arXiv HTML/abstract page."""
    parts: List[str] = []

    for pattern in META_PATTERNS:
        matches = re.findall(pattern, html, re.IGNORECASE)
        if matches:
            parts.extend(matches)

    authors_section = re.search(r'<div[^>]*class="authors"[^>]*>(.*?)</div>', html, re.IGNORECASE | re.DOTALL)
    if authors_section:
        parts.append(authors_section.group(1))

    if not parts:
        parts.append(html[:4000])

    return clean_affiliation_text(" ; ".join(parts))


async def fetch_affiliation_source(session: aiohttp.ClientSession, arxiv_id: str) -> str:
    """Fetch raw affiliation text from arXiv HTML or abstract pages."""
    urls = [
        f"https://arxiv.org/html/{arxiv_id}",
        f"https://arxiv.org/html/{arxiv_id}v1",
        f"https://arxiv.org/abs/{arxiv_id}",
    ]

    for url in urls:
        try:
            async with session.get(url) as response:
                if response.status != 200:
                    continue
                html = await response.text()
                source = build_affiliation_source_from_html(html)
                if source:
                    return source
        except Exception as exc:
            logger.debug("Affiliation fetch failed for %s via %s: %r", arxiv_id, url, exc)

    return ""


def parse_affiliation_response(response_text: str) -> List[str]:
    """Parse LLM affiliation JSON into a normalized list."""
    response_text = response_text.strip()
    response_text = response_text.removeprefix("```json").removeprefix("```")
    response_text = response_text.removesuffix("```").strip()

    start_idx = response_text.find("{")
    end_idx = response_text.rfind("}")
    json_str = response_text[start_idx:end_idx + 1] if start_idx != -1 and end_idx != -1 else response_text

    try:
        parsed = json.loads(json_str)
    except json.JSONDecodeError:
        parsed = ast.literal_eval(json_str)

    affiliations = parsed.get("affiliations", []) if isinstance(parsed, dict) else []
    return split_affiliation_candidates(affiliations)


async def normalize_affiliations_with_llm(
    client: DashScopeClient,
    paper: Dict[str, Any],
    raw_source: str,
) -> List[str]:
    """Use LLM to clean and extract institution names from raw affiliation text."""
    authors = ", ".join(author.get("name", "") for author in paper.get("authors", [])[:6])
    prompt = f"""Clean the following raw author affiliation text extracted from an academic paper.

Paper title: {paper.get('title', '')}
Authors: {authors}
Raw affiliation text: {raw_source}

Rules:
- Return 0-3 cleaned affiliations as JSON: {{"affiliations": ["..."]}}
- Each item must be one complete institution/department affiliation string
- Do NOT split a single affiliation because it contains commas
- Remove LaTeX, email addresses, markup, placeholders, and corrupted fragments
- Merge fragments when they clearly belong to one affiliation
- If a department/school/faculty phrase is immediately followed by a university or institute name, add commas appropriately
- Remove fake placeholders such as "Company Name, Location, Country" or "School of ZZZ"
- Prefer accurate, human-readable institution names
- Example: "% \\institutionTexas A\\&M University" -> ["Texas A&M University"]
- Example: "Faculty of Data Science，City University of Macau" -> ["Faculty of Data Science, City University of Macau"]
- Example: "Department of Software TechnologyZhejiang University Ningbo China" -> ["Department of Software Technology, Zhejiang University, Ningbo, China"]
- If nothing reliable can be recovered, return an empty list
"""

    response_text = await client.call_llm(
        [
            {
                "role": "system",
                "content": "You normalize messy author affiliation strings. Return only JSON.",
            },
            {"role": "user", "content": prompt},
        ]
    )
    return parse_affiliation_response(response_text)


async def enrich_affiliations(
    papers: Sequence[Dict[str, Any]],
    concurrency: int = 4,
) -> List[Dict[str, Any]]:
    """Fill or clean affiliations for papers using HTML fetch + LLM normalization."""
    if not DASHSCOPE_API_KEY:
        logger.warning("DASHSCOPE_API_KEY is not configured; keeping deterministic affiliation cleanup only")
        enriched: List[Dict[str, Any]] = []
        for paper in papers:
            current = normalize_affiliation_fields(paper.get("affiliation"), paper.get("affiliations"))
            paper_copy = paper.copy()
            paper_copy["affiliation"] = current["affiliation"] or "Unknown"
            paper_copy["affiliations"] = current["affiliations"]
            enriched.append(paper_copy)
        return enriched

    connector = aiohttp.TCPConnector(
        limit=concurrency,
        limit_per_host=max(1, concurrency),
        ttl_dns_cache=600,
        use_dns_cache=True,
        family=socket.AF_INET,
        enable_cleanup_closed=True,
    )
    http_semaphore = asyncio.Semaphore(concurrency)

    async with aiohttp.ClientSession(
        connector=connector,
        timeout=aiohttp.ClientTimeout(total=30),
    ) as session, DashScopeClient(DASHSCOPE_API_KEY, max(1, min(2, concurrency))) as client:

        async def enrich_one(paper: Dict[str, Any]) -> Dict[str, Any]:
            current = normalize_affiliation_fields(paper.get("affiliation"), paper.get("affiliations"))
            paper["affiliation"] = current["affiliation"]
            paper["affiliations"] = current["affiliations"]

            if not needs_affiliation_normalization(paper):
                return paper

            raw_source = paper.get("affiliation", "")
            if not raw_source or raw_source == "Unknown" or has_suspicious_affiliation_text(raw_source):
                async with http_semaphore:
                    fetched_source = await fetch_affiliation_source(session, paper.get("id", ""))
                raw_source = fetched_source or raw_source

            if not raw_source:
                paper["affiliation"] = "Unknown"
                paper["affiliations"] = []
                return paper

            try:
                normalized_list = await normalize_affiliations_with_llm(client, paper, raw_source)
            except Exception as exc:
                logger.warning("Affiliation normalization failed for %s: %r", paper.get("id"), exc)
                normalized_list = split_affiliation_candidates(raw_source)

            if normalized_list:
                paper["affiliations"] = normalized_list
                paper["affiliation"] = "; ".join(normalized_list)
            else:
                paper["affiliations"] = []
                paper["affiliation"] = "Unknown"

            return paper

        tasks = [enrich_one(paper.copy()) for paper in papers]
        return await asyncio.gather(*tasks)
