"""S6 authors and institutions (design doc 4.6): OpenAlex first, arXiv HTML for the
authors OpenAlex has no institution for. Each author is paired with institutions.

Per paper this writes:
  institutions          [{name, ror, country, type, source, confidence}]
  author_affiliations   one list of indices into ``institutions`` per author (same order
                        as ``authors``); empty when unknown
  affiliations          institution names (old field, kept for the current pages)
  affiliation           "; ".join(affiliations)
  affiliation_source    "openalex" | "openalex+html" | "html" | "none"
  affiliation_raw       the affiliation text as written (departments included), for the
                        team-background guess in venues.py
  affiliation_checked_at  ISO date of this lookup (newer OpenAlex data is fetched again
                        while a paper is less than RECHECK_DAYS old and not fully covered)

Only papers the site may show (relevance >= 1) are looked up: ~10% of what is fetched.
No LLM is used here.
"""

from __future__ import annotations

import asyncio
import logging
import re
import unicodedata
from datetime import date, timedelta
from html import unescape
from html.parser import HTMLParser
from typing import Any, Dict, List, Optional, Tuple

import aiohttp

from .config import openalex_url, redact
from .utils import Progress, is_arxiv_id, normalize_arxiv_id

logger = logging.getLogger(__name__)

OPENALEX_WORK = "https://api.openalex.org/works/doi:10.48550/arXiv.{id}?select=id,authorships"
ARXIV_HTML = "https://arxiv.org/html/{id}"
USER_AGENT = "FinPaperRadar/0.2 (+https://github.com/Barca0412/Introduction-to-Quantitative-Finance)"
OPENALEX_RATE = 5          # requests per second (OpenAlex polite pool asks for <= 10)
ARXIV_DELAY = 3.0          # seconds between arXiv HTML requests, as for the API
RECHECK_DAYS = 14          # look a paper up again while younger than this and incomplete
MIN_RELEVANCE = 1


# --------------------------------------------------------------------------
# Names
# --------------------------------------------------------------------------

def name_key(name: str) -> str:
    """Comparable author name: no accents, lower case, no punctuation or initials."""
    text = unicodedata.normalize("NFKD", name or "").encode("ascii", "ignore").decode()
    parts = [p for p in re.split(r"[^a-z]+", text.lower()) if len(p) > 1]
    return " ".join(parts)


def _tokens(name: str) -> List[str]:
    text = unicodedata.normalize("NFKD", name or "").encode("ascii", "ignore").decode()
    return [p for p in re.split(r"[^a-z]+", text.lower()) if p]


def names_match(a: str, b: str) -> bool:
    """Same person, allowing swapped order ("Wang Hao") and initials ("J. Smith")."""
    ka, kb = _tokens(a), _tokens(b)
    if not ka or not kb:
        return False
    if ka == kb or sorted(ka) == sorted(kb):
        return True
    full_a, full_b = {t for t in ka if len(t) > 1}, {t for t in kb if len(t) > 1}
    if len(full_a & full_b) >= 2:
        return True
    # Same family name (last token) and the same first given-name initial.
    return ka[-1] == kb[-1] and len(ka[-1]) > 1 and ka[0][0] == kb[0][0]


# --------------------------------------------------------------------------
# OpenAlex
# --------------------------------------------------------------------------

def parse_openalex(work: Dict[str, Any]) -> List[Dict[str, Any]]:
    """[{name, institutions: [{name, ror, country, type}]}] in author order."""
    authors = []
    for authorship in work.get("authorships") or []:
        institutions = []
        for inst in authorship.get("institutions") or []:
            if not inst.get("display_name"):
                continue
            institutions.append({
                "name": inst["display_name"],
                "ror": (inst.get("ror") or "").rsplit("/", 1)[-1],
                "country": inst.get("country_code") or "",
                "type": inst.get("type") or "",
            })
        authors.append({
            "name": (authorship.get("author") or {}).get("display_name") or authorship.get("raw_author_name") or "",
            "institutions": institutions,
            "raw": [str(r) for r in authorship.get("raw_affiliation_strings") or []],
        })
    return authors


# --------------------------------------------------------------------------
# arXiv HTML (LaTeXML)
# --------------------------------------------------------------------------

# Classes whose text is an affiliation (or holds one), and classes to skip inside them.
_AFFIL_CLASSES = {"ltx_role_affiliation", "ltx_role_address", "ltx_affiliation_institution",
                  "ltx_note_content", "ltx_author_notes", "ltx_role_institution"}
_SKIP_CLASSES = {"ltx_role_email", "ltx_contact_name", "ltx_note_mark", "ltx_note_type",
                 "ltx_affiliation_city", "ltx_affiliation_country", "ltx_affiliation_postcode",
                 "ltx_affiliation_streetaddress", "ltx_role_orcid", "ltx_role_homepage"}
_VOID = {"br", "img", "meta", "link", "hr", "input", "col", "area", "base", "wbr", "source"}


class _AuthorsParser(HTMLParser):
    """Collects each ``ltx_creator ltx_role_author`` block: person name and the text of
    its affiliation parts. Text after a <br> inside the person name is an affiliation
    line too (a common LaTeX layout)."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.stack: List[Tuple[str, set]] = []
        self.authors: List[Dict[str, Any]] = []
        self.current: Optional[Dict[str, Any]] = None
        self.creator_depth = -1
        self.after_break = False
        self.in_authors = False
        self.authors_depth = -1

    def handle_starttag(self, tag: str, attrs: List[Tuple[str, Optional[str]]]) -> None:
        classes = set((dict(attrs).get("class") or "").split())
        if tag == "br" and self.current is not None:
            self.after_break = True
            if self.current["aff"] and self.current["aff"][-1] != "\n":
                self.current["aff"].append("\n")
            return
        if tag in _VOID:
            return
        if "ltx_authors" in classes and not self.in_authors:
            self.in_authors, self.authors_depth = True, len(self.stack)
        if self.in_authors and "ltx_creator" in classes and "ltx_role_author" in classes:
            self.current = {"name": [], "aff": []}
            self.creator_depth = len(self.stack)
            self.after_break = False
        if tag in ("sup", "sub") and self.current is not None:
            classes = classes | {"ltx_note_mark"}  # footnote markers, not text
        self.stack.append((tag, classes))

    def handle_endtag(self, tag: str) -> None:
        if tag in _VOID or not self.stack:
            return
        # Pop to the matching tag (tolerates sloppy HTML).
        for depth in range(len(self.stack) - 1, -1, -1):
            if self.stack[depth][0] == tag:
                del self.stack[depth:]
                break
        if self.current is not None and len(self.stack) <= self.creator_depth:
            self.authors.append({
                "name": " ".join("".join(self.current["name"]).split()),
                "raw": "".join(self.current["aff"]),
            })
            self.current = None
        if self.in_authors and len(self.stack) <= self.authors_depth:
            self.in_authors = False

    def handle_data(self, data: str) -> None:
        if self.current is None:
            return
        active = set().union(*(c for _, c in self.stack[self.creator_depth:])) if self.stack else set()
        if active & _SKIP_CLASSES or "mailto:" in data:
            return
        if "ltx_personname" in active and not self.after_break and not (active & _AFFIL_CLASSES):
            self.current["name"].append(data)
        elif active & _AFFIL_CLASSES or ("ltx_personname" in active and self.after_break):
            self.current["aff"].append(data)


_EMAIL = re.compile(r"\S+@\S+")
_NOISE = re.compile(r"^(affiliation|thanks|email|e-mail|corresponding author|equal contribution)\s*:?\s*", re.I)
_INSTITUTION_WORD = re.compile(
    r"universit|institut|college|school|academy|laborator|\blab\b|labs\b|centre|center|hospital|"
    r"inc\.?$|ltd|corporation|company|technologies|research|bank|capital|securities|fund|"
    r"group|\bai\b|google|microsoft|meta|amazon|alibaba|tencent|baidu|bytedance|huawei|nvidia|deepmind|openai",
    re.I,
)


# Levels of an affiliation segment, best first. "Carey Business School, Johns Hopkins
# University" -> the university; "Department of Statistics" alone stays (better than
# nothing) but is dropped when the same author also names a university.
_LEVELS = [
    re.compile(r"universit|universidad|università|universität|université|école|ecole|polytechnic|"
               r"institute of technology|\bETH\b|\bEPFL\b|\bMIT\b", re.I),
    re.compile(r"institut|academy|college|national lab|chinese academy", re.I),
    re.compile(r"\binc\b|\bltd\b|\bllc\b|\bco\.|corporation|company|technologies|\bgroup\b|bank|capital|"
               r"securities|asset management|\bfund|research|laborator|\blabs?\b|google|microsoft|meta\b|amazon|"
               r"alibaba|ant group|tencent|baidu|bytedance|huawei|nvidia|deepmind|openai|jpmorgan|morgan stanley|"
               r"goldman|bloomberg|citadel|two sigma", re.I),
    re.compile(r"school|department|faculty|centre|center|division|hospital", re.I),
]
_ADDRESS = re.compile(r"\d{3,}|^\s*(usa|u\.s\.a\.|united states|united kingdom|uk|china|p\.\s?r\.\s?china|"
                      r"singapore|japan|korea|germany|france|canada|australia|india|hong kong|switzerland|"
                      r"netherlands|italy|spain|[A-Z]{2})\s*$", re.I)
_SENTENCE = re.compile(r"\b(work (was )?done|while (the author )?(was )?(at|visiting)|intern(ship)? at|"
                       r"equal contribution|corresponding author)\b", re.I)


# A legal suffix on its own ("Ltd"), or a sentence about a person, is not an institution.
_NOT_A_NAME = re.compile(r"^(ltd|inc|llc|gmbh|co|corp|plc|s\.?a|ag)\.?$|\b(is|was|are) (an?|the)\b|independent researcher|"
                         r"contributed equally|equally contributed|equal contribution", re.I)


def _level(segment: str) -> int:
    for rank, pattern in enumerate(_LEVELS):
        if pattern.search(segment):
            return rank
    return len(_LEVELS)


def institution_from_line(line: str) -> Tuple[str, int]:
    """The most institution-like comma segment of one line, and its level."""
    if _SENTENCE.search(line):
        at = re.search(r"\b(?:at|with)\s+(.+)$", line)
        if not at:
            return "", len(_LEVELS)
        line = at.group(1)
    segments = [seg.strip(" .;:") for seg in line.split(",")]
    segments = [seg for seg in segments if seg and not _ADDRESS.search(seg)]
    if not segments:
        return "", len(_LEVELS)
    best = min(segments, key=_level)
    return best, _level(best)


def split_raw_affiliations(raw: str) -> List[str]:
    """One author's raw affiliation text -> institution names, top level first (the
    university rather than its department; addresses, e-mails and notes removed)."""
    found: List[Tuple[str, int]] = []
    for line in re.split(r"[\n;]|\s{2,}", unescape(raw or "")):
        line = _EMAIL.sub("", line)
        line = re.sub(r"[.,;]?\s*\b(e-?mail|emails?|correspondence)\b.*$", "", line, flags=re.I)
        line = _NOISE.sub("", line.strip(" ,.;:*†‡§¶#0123456789\t"))
        line = re.sub(r"\s+", " ", line).strip(" ,.;:")
        if len(line) < 4 or not re.search(r"[A-Za-z一-鿿]", line):
            continue
        name, level = institution_from_line(line)
        if len(name) < 3 or len(name.split()) > 12 or _NOT_A_NAME.search(name):
            continue
        if level == len(_LEVELS) and len(found) and found[-1][1] < len(_LEVELS):
            continue  # stray fragment next to a real institution
        if name not in [n for n, _ in found]:
            found.append((name, level))
    if any(level <= 2 for _, level in found):
        found = [(n, lv) for n, lv in found if lv <= 2]  # drop bare departments
    return [name for name, _ in found]


def parse_arxiv_html(html: str) -> List[Dict[str, Any]]:
    """[{name, institutions: [str]}] from a LaTeXML arXiv page, in author order."""
    parser = _AuthorsParser()
    try:
        parser.feed(html)
    except Exception:  # malformed page: keep what was parsed
        pass
    return [
        {"name": a["name"], "institutions": split_raw_affiliations(a["raw"]),
         "raw": [line for line in (" ".join(l.split()) for l in a["raw"].split("\n")) if line]}
        for a in parser.authors if a["name"]
    ]


# --------------------------------------------------------------------------
# Combine
# --------------------------------------------------------------------------

def _paper_authors(paper: Dict[str, Any]) -> List[str]:
    names = []
    for author in paper.get("authors") or []:
        names.append(author.get("name", "") if isinstance(author, dict) else str(author))
    return names


def combine(paper: Dict[str, Any], openalex: List[Dict[str, Any]], html: Optional[List[Dict[str, Any]]]) -> Dict[str, Any]:
    """Merge both sources into the paper's fields (rules in design doc 4.6.2)."""
    institutions: List[Dict[str, Any]] = []
    index: Dict[str, int] = {}

    def add(inst: Dict[str, Any]) -> int:
        keys = [k for k in (inst.get("ror"), name_key(inst["name"])) if k]
        for key in keys:
            if key in index:
                return index[key]
        for key in keys:
            index[key] = len(institutions)
        institutions.append(inst)
        return len(institutions) - 1

    names = _paper_authors(paper)
    per_author: List[List[int]] = []
    raw_lines: List[str] = []  # departments etc., kept for the team-background guess
    used_html = False
    for position, name in enumerate(names):
        found: List[int] = []
        oa = next((a for a in openalex if names_match(a["name"], name)), None)
        if oa is None and position < len(openalex) and len(openalex) == len(names):
            oa = openalex[position]  # same author count: trust the order
        if oa and oa["institutions"]:
            found = [add({**inst, "source": "openalex", "confidence": "high"}) for inst in oa["institutions"]]
            raw_lines += oa.get("raw", [])
        elif html:
            ha = next((a for a in html if names_match(a["name"], name)), None)
            if ha is None and len(html) == len(names):
                ha = html[position]
            if ha and ha["institutions"]:
                used_html = True
                raw_lines += ha.get("raw", [])
                found = [add({"name": text, "ror": "", "country": "", "type": "", "source": "html", "confidence": "medium"})
                         for text in ha["institutions"]]
        per_author.append(found)

    has_oa = any(i["source"] == "openalex" for i in institutions)
    source = "none" if not institutions else ("openalex+html" if has_oa and used_html else ("html" if used_html else "openalex"))
    return {
        "institutions": institutions,
        "author_affiliations": per_author,
        "affiliations": [i["name"] for i in institutions],
        "affiliation": "; ".join(i["name"] for i in institutions),
        "affiliation_source": source,
        "affiliation_raw": list(dict.fromkeys(line[:200] for line in raw_lines))[:20],
        "affiliation_checked_at": date.today().isoformat(),
    }


def needs_lookup(paper: Dict[str, Any], today: Optional[date] = None) -> bool:
    """Relevant papers never looked up, or young and incomplete (OpenAlex lags)."""
    relevance = paper.get("relevance")
    if not isinstance(relevance, int) or isinstance(relevance, bool) or relevance < MIN_RELEVANCE:
        return False
    checked = paper.get("affiliation_checked_at")
    if not checked:
        return True
    complete = paper.get("affiliation_source") == "openalex" and all(paper.get("author_affiliations") or [[]])
    if complete:
        return False
    today = today or date.today()
    try:
        published = date.fromisoformat(str(paper.get("published_date", ""))[:10])
        last = date.fromisoformat(str(checked)[:10])
    except ValueError:
        return True
    return today - published <= timedelta(days=RECHECK_DAYS) and today > last


# --------------------------------------------------------------------------
# Fetching
# --------------------------------------------------------------------------

class _Pacer:
    """At most one request per ``interval`` seconds."""

    def __init__(self, interval: float):
        self.interval, self.lock, self.last = interval, asyncio.Lock(), 0.0

    async def wait(self) -> None:
        async with self.lock:
            loop = asyncio.get_running_loop()
            delay = self.last + self.interval - loop.time()
            if delay > 0:
                await asyncio.sleep(delay)
            self.last = loop.time()


async def _get(session: aiohttp.ClientSession, url: str, pacer: _Pacer, as_json: bool) -> Any:
    for attempt in range(3):
        await pacer.wait()
        try:
            async with session.get(url) as response:
                if response.status == 404:
                    return None
                if response.status in (429, 500, 502, 503, 504):
                    await asyncio.sleep(2 * (attempt + 1))
                    continue
                if response.status != 200:
                    return None
                return await (response.json(content_type=None) if as_json else response.text())
        except (aiohttp.ClientError, asyncio.TimeoutError):
            await asyncio.sleep(2 * (attempt + 1))
    return None


async def lookup_paper(session, paper, oa_pacer, html_pacer) -> Dict[str, Any]:
    paper_id = str(paper.get("id", ""))
    arxiv = is_arxiv_id(paper_id)
    if arxiv:
        url = OPENALEX_WORK.format(id=normalize_arxiv_id(paper_id))
    elif paper.get("doi"):  # papers added from the top-venue library (discover.py)
        url = f"https://api.openalex.org/works/doi:{paper['doi']}?select=id,authorships"
    else:
        return combine(paper, [], None)
    work = await _get(session, openalex_url(url), oa_pacer, as_json=True) or {}
    openalex = parse_openalex(work)
    names = _paper_authors(paper)
    covered = sum(1 for name in names if any(names_match(a["name"], name) and a["institutions"] for a in openalex))
    html_authors = None
    if covered < len(names) and arxiv:
        page = await _get(session, ARXIV_HTML.format(id=normalize_arxiv_id(paper_id)), html_pacer, as_json=False)
        html_authors = parse_arxiv_html(page) if page else None
    return combine(paper, openalex, html_authors)


async def enrich_institutions(papers: List[Dict[str, Any]], today: Optional[date] = None) -> Dict[str, int]:
    """Look up institutions for the papers that need it (in place). Returns counts."""
    todo = [p for p in papers if needs_lookup(p, today)]
    counts = {"looked_up": len(todo), "with_institution": 0, "all_authors": 0, "html_used": 0}
    if not todo:
        return counts
    progress = Progress("institutions", len(todo), logger)
    oa_pacer, html_pacer = _Pacer(1 / OPENALEX_RATE), _Pacer(ARXIV_DELAY)
    timeout = aiohttp.ClientTimeout(total=40)
    # trust_env: honour HTTPS_PROXY etc. like curl does (needed behind a proxy).
    async with aiohttp.ClientSession(timeout=timeout, headers={"User-Agent": USER_AGENT}, trust_env=True) as session:
        semaphore = asyncio.Semaphore(8)

        async def one(paper: Dict[str, Any]) -> None:
            async with semaphore:
                try:
                    paper.update(await lookup_paper(session, paper, oa_pacer, html_pacer))
                except Exception as exc:  # one paper must not stop the run
                    logger.warning("Institution lookup failed for %s: %s", paper.get("id"), redact(repr(exc)))
            progress.update(ok=bool(paper.get("institutions")))

        await asyncio.gather(*(one(p) for p in todo))

    for paper in todo:
        if paper.get("institutions"):
            counts["with_institution"] += 1
            if all(paper.get("author_affiliations") or [[]]):
                counts["all_authors"] += 1
        if "html" in str(paper.get("affiliation_source")):
            counts["html_used"] += 1
    logger.info("Institutions: %s", counts)
    return counts
