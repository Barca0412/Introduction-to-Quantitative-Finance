---
title: 方法说明 · FinPaperRadar
description: FinPaperRadar 的收录范围、10 个 arXiv 分类、标签体系、大模型打标签和中文摘要的生成方式、数据流程与授权，以及已知的局限。
---

# About FinPaperRadar

## Purpose and editorial scope

FinPaperRadar（AI × 金融论文雷达）is an educational discovery tool, not an investment-research recommendation engine. It helps readers find recent work at the intersection of AI, LLM and agent systems with finance and quantitative research. Each paper should be evaluated through its original arXiv record, methods, data and limitations.

This subsection is a focused arXiv monitoring stack for the overlap of:

- AI / LLM / agent systems
- finance applications and quantitative research workflows
- agent planning, deep research, multi-agent coordination, tool use, reasoning, and memory

## What the pipeline does

1. Pulls recent papers from 10 monitored arXiv categories.
2. Uses an LLM (currently DeepSeek, via an OpenAI-compatible API) to assign research tags, extract keywords, and generate Chinese summaries. Without an API key it falls back to rule-based tags.
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

## Data and storage

- The daily job restores the full history from external storage, adds the new papers, and never commits generated data to git.
- Full history (metadata, abstracts, tags, embeddings) is published as Parquet to a Hugging Face dataset, with a mirror on the GitHub Release `radar-data`. <RadarDatasetLinks />
- The site only ships light data in `docs/public/arxiv-data/`: the last ~90 days of metadata with short abstract snippets on first load; full abstracts, int8 embeddings and older months (split by month) load on demand.
- Working files during a run: `data/papers.json`, `data/stats.json`, `data/embeddings.f32` (all git-ignored).
- Pipeline code: `scripts/arxiv_radar/`

## Use of arXiv data

Thank you to arXiv for use of its open access interoperability.

FinPaperRadar uses the arXiv API for metadata only. It publishes titles, authors, abstracts, categories and links back to arXiv; it does not host full texts, PDFs or figures. Please follow each paper's own license when reusing it.

## License of the dataset

The tags, keywords, Chinese summaries, affiliation normalisation, focus scores, embeddings, statistics and the curation of the dataset are released under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). The arXiv metadata itself (titles, authors, abstracts, categories) is CC0 and not restricted by this license.
