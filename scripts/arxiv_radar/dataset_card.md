---
# DRAFT dataset card. Review before the first upload:
# - license: arXiv distributes its metadata under CC0, but please confirm the
#   licence you want for the derived fields (tags, Chinese summaries, focus scores).
license: other
language:
  - en
  - zh
pretty_name: AI + Finance arXiv Radar
size_categories:
  - 10K<n<100K
task_categories:
  - text-classification
  - feature-extraction
tags:
  - arxiv
  - finance
  - llm
  - agents
configs:
  - config_name: papers
    data_files: papers.parquet
  - config_name: embeddings
    data_files: embeddings.parquet
---

# AI + Finance arXiv Radar

Daily-updated metadata for recent arXiv papers from 10 categories (cs.AI, cs.CL,
cs.MA, cs.IR, cs.SE, cs.CE, q-fin.ST, q-fin.CP, q-fin.PM, q-fin.TR), with machine-generated
research tags and focus scores for AI + Finance, agent planning and deep research.
It is the full history behind the Radar pages of
[Introduction-to-Quantitative-Finance](https://github.com/Barca0412/Introduction-to-Quantitative-Finance)
([website](https://barca0412.github.io/Introduction-to-Quantitative-Finance/arxiv/)).

Thank you to arXiv for use of its open access interoperability.

## Snapshot

| | |
|---|---|
| Generated at (UTC) | {{generated_at}} |
| Papers | {{papers}} |
| Papers with embeddings | {{embedded_papers}} |
| Published-date range | {{first_date}} – {{last_date}} |
| Embedding model | `{{embedding_model}}` (384-d, mean pooling, L2-normalised) |

## Files

- `papers.parquet`: one row per paper: `id`, `title`, `abstract`, `authors` (name, affiliation),
  `categories`, `published_date`, `pdf_link`, `abs_link`, `tags`, `keywords`, `summary_zh`,
  `affiliation`, `affiliations`, `focus` (score, is_focus, primary_topic, topics, labels,
  matched_tags, matched_categories, reasons).
- `embeddings.parquet`: `id`, `text_hash`, `vector` (float32[384]). The Parquet schema metadata
  key `radar_embeddings` holds the model name and the six theme query vectors.
- `stats.json`: daily / cumulative tag and keyword counts used by the Trends page.
- `export_info.json`: counts, sizes and SHA-256 of the files above.

The same files are mirrored on the GitHub Release `radar-data` of the repository.

## How it is built

A GitHub Actions job runs daily: it restores this dataset, fetches the last 7 days from the
arXiv API (3-second request spacing), tags new papers with an LLM (rule-based fallback when no
key is configured), embeds new or changed papers incrementally, and uploads the merged result.

## Limitations

- Only metadata and abstracts are included. No full texts, PDFs or figures.
- Tags, summaries, affiliations and focus scores are machine-generated navigation aids and may
  be wrong. Check every claim against the original arXiv record.
- Coverage is limited by the categories above and by `MAX_RESULTS_PER_CATEGORY` per run.
