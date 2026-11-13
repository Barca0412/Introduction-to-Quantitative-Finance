# About ArXiv Radar

## Purpose and editorial scope

ArXiv Radar is an educational discovery tool, not an investment-research recommendation engine. It helps readers find recent work at the intersection of AI, LLM and agent systems with finance and quantitative research. Each paper should be evaluated through its original arXiv record, methods, data and limitations.

This subsection is a focused arXiv monitoring stack for the overlap of:

- AI / LLM / agent systems
- finance applications and quantitative research workflows
- agent planning, deep research, multi-agent coordination, tool use, reasoning, and memory

## What the pipeline does

1. Pulls recent papers from 10 monitored arXiv categories.
2. Uses DashScope / Qwen to assign research tags, extract keywords, and generate Chinese summaries.
3. Normalizes affiliations, computes trend statistics, generates embeddings, and publishes static JSON.
4. Powers a VitePress browsing experience under `/arxiv/`.

## Update policy and provenance

The automated pipeline runs daily. The displayed tags, summaries and affiliations are machine-generated navigation aids and may contain errors. The primary source for every research claim is the original arXiv paper linked in the Radar; the site reports when the generated dataset was last updated.

## Monitored categories

- `cs.AI`
- `cs.CL`
- `cs.MA`
- `cs.IR`
- `cs.SE`
- `cs.CE`
- `q-fin.ST`
- `q-fin.CP`
- `q-fin.PM`
- `q-fin.TR`

## Main research tags

- `ai-finance`
- `agent-planning`
- `deep-research`
- `multi-agent`
- `tool-use`
- `reasoning`
- `memory`
- `rag`
- `time-series`

## Output locations

- Raw generated data: `data/papers.json`, `data/stats.json`, `data/embeddings_index.json`
- Public site data: `docs/public/arxiv-data/`
- Public chart assets: `docs/public/arxiv-charts/`
- Pipeline code: `scripts/arxiv_radar/`
