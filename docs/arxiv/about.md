# About ArXiv Radar

This subsection is a focused arXiv monitoring stack for the overlap of:

- AI / LLM / agent systems
- finance applications and quantitative research workflows
- agent planning, deep research, multi-agent coordination, tool use, reasoning, and memory

## What the pipeline does

1. Pulls recent papers from 10 monitored arXiv categories.
2. Uses DashScope / Qwen to assign research tags, extract keywords, and generate Chinese summaries.
3. Normalizes affiliations, computes trend statistics, generates embeddings, and publishes static JSON.
4. Powers a VitePress browsing experience under `/arxiv/`.

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
