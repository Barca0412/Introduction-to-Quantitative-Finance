"""Run S3 v2 enrichment on the hand-labelled trial papers and report agreement.

    LLM_API_KEY=... python3 -m scripts.arxiv_radar.enrich_trial [--out data/enrich-trial]

Fetches the papers in tests/fixtures/trial_papers.yaml from arXiv, enriches them with
the current prompt, compares with the hand labels and writes:
  - <out>/results.json  every model answer next to its label
  - <out>/report.md     agreement per dimension and every disagreement
and appends the report to the GitHub job summary. Nothing is stored or published.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import os
from pathlib import Path
from typing import Any, Dict, List

import arxiv
import yaml

from .config import LLM_API_KEY
from .enrich import ENRICH_VERSION
from .llm_processor import process_papers_batch
from .utils import build_paper_record, normalize_arxiv_id

FIXTURE = Path(__file__).resolve().parent / "tests" / "fixtures" / "trial_papers.yaml"
LIST_FIELDS = ("task_types", "finance_domains", "methods")


def load_labels(path: Path = FIXTURE) -> List[Dict[str, Any]]:
    with open(path, encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def fetch(ids: List[str]) -> Dict[str, Dict[str, Any]]:
    client = arxiv.Client(page_size=100, delay_seconds=3.0, num_retries=5)
    records = {}
    for result in client.results(arxiv.Search(id_list=ids, max_results=len(ids))):
        paper = build_paper_record(result)
        records[normalize_arxiv_id(paper["id"])] = paper
    return records


def compare(label: Dict[str, Any], paper: Dict[str, Any]) -> Dict[str, Any]:
    """Per-dimension agreement; lists agree when they share at least one id
    (both empty also agrees)."""
    if (paper.get("stage_versions") or {}).get("enrich") != ENRICH_VERSION:
        return {"failed": True, "error": paper.get("last_error", "")}
    out: Dict[str, Any] = {"failed": False}
    out["relevance"] = paper.get("relevance") in label["relevance"]
    out["paper_type"] = paper.get("paper_type") == label["paper_type"]
    for field in LIST_FIELDS:
        want, got = set(label.get(field) or []), set(paper.get(field) or [])
        out[field] = bool(want & got) or (not want and not got)
    if "withdrawn" in label:
        out["withdrawn"] = bool(paper.get("withdrawn")) == bool(label["withdrawn"])
    return out


DIMENSIONS = ("relevance", "paper_type", "task_types", "finance_domains", "methods")


def build_report(rows: List[Dict[str, Any]]) -> str:
    scored = [r for r in rows if not r["check"]["failed"]]
    held_out = [r for r in scored if not r["label"].get("in_prompt")]
    lines = [
        f"### Enrichment trial ({ENRICH_VERSION}, model `{os.getenv('LLM_MODEL') or 'default'}`)",
        "",
        f"{len(rows)} papers; {len(rows) - len(scored)} failed. "
        f"Agreement below counts the {len(held_out)} papers that are not few-shot examples in the prompt "
        f"(all {len(scored)} in brackets).",
        "",
        "| Dimension | Agree | Share |",
        "| --- | ---: | ---: |",
    ]
    for dim in DIMENSIONS:
        hit = sum(1 for r in held_out if r["check"][dim])
        hit_all = sum(1 for r in scored if r["check"][dim])
        share = f"{hit / len(held_out):.0%}" if held_out else "-"
        lines.append(f"| {dim} | {hit}/{len(held_out)} ({hit_all}/{len(scored)}) | {share} |")
    lines += ["", "**Disagreements**", "", "| Paper | Dimension | Label | Model |", "| --- | --- | --- | --- |"]
    for r in rows:
        if r["check"]["failed"]:
            lines.append(f"| {r['label']['name']} | failed | | {str(r['check']['error'])[:80]} |")
            continue
        for dim in DIMENSIONS + ("withdrawn",):
            if r["check"].get(dim) is False:
                want = r["label"].get(dim)
                got = r["paper"].get(dim)
                mark = " (in prompt)" if r["label"].get("in_prompt") else ""
                lines.append(f"| {r['label']['name']}{mark} | {dim} | {want} | {got} |")
    return "\n".join(lines) + "\n"


async def run(out_dir: Path) -> Dict[str, Any]:
    labels = load_labels()
    records = fetch([label["id"] for label in labels])
    missing = [label["id"] for label in labels if label["id"] not in records]
    if missing:
        raise SystemExit(f"arXiv did not return: {', '.join(missing)}")
    papers = await process_papers_batch([records[label["id"]] for label in labels])
    by_id = {normalize_arxiv_id(p["id"]): p for p in papers}
    rows = [{"label": label, "paper": by_id[label["id"]], "check": compare(label, by_id[label["id"]])} for label in labels]

    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "results.json").write_text(json.dumps(rows, ensure_ascii=False, indent=1), encoding="utf-8")
    report = build_report(rows)
    (out_dir / "report.md").write_text(report, encoding="utf-8")
    summary = os.getenv("GITHUB_STEP_SUMMARY")
    if summary:
        with open(summary, "a", encoding="utf-8") as fh:
            fh.write(report)
    print(report)
    return {"rows": len(rows)}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--out", default="data/enrich-trial", type=Path)
    args = parser.parse_args()
    if not LLM_API_KEY:
        raise SystemExit("LLM_API_KEY is not set; the trial needs the real model.")
    asyncio.run(run(args.out))


if __name__ == "__main__":
    main()
