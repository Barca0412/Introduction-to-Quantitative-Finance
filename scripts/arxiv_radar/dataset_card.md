---
license: cc-by-4.0
language:
  - en
  - zh
pretty_name: "FinPaperRadar · AI × 金融论文雷达"
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

# FinPaperRadar · AI × 金融论文雷达

FinPaperRadar is a daily-updated index of recent arXiv papers from 10 categories (cs.AI, cs.CL,
cs.MA, cs.IR, cs.SE, cs.CE, q-fin.ST, q-fin.CP, q-fin.PM, q-fin.TR), with machine-generated
research tags, focus scores and embeddings for AI + Finance, agent planning and deep research.
It is the full history behind the [FinPaperRadar pages](https://barca0412.github.io/Introduction-to-Quantitative-Finance/arxiv/)
of [Introduction-to-Quantitative-Finance](https://github.com/Barca0412/Introduction-to-Quantitative-Finance).

FinPaperRadar（AI × 金融论文雷达）每天从上述 10 个 arXiv 分类收录新论文，并附上机器生成的研究标签、
关注度评分和语义向量，是"量化研究入门"站点论文雷达页面背后的完整数据。

Thank you to arXiv for use of its open access interoperability.

## Snapshot

| | |
|---|---|
| Generated at (UTC) | {{generated_at}} |
| Papers | {{papers}} |
| Papers with embeddings | {{embedded_papers}} |
| Published-date range | {{first_date}} – {{last_date}} |
| Embedding model | `{{embedding_model}}` (384-d, mean pooling, L2-normalised) |

## Where to get it

{{download_lines}}

## Files

- `papers.parquet`: one row per paper: `id`, `title`, `abstract`, `authors` (name, affiliation),
  `categories`, `published_date`, `pdf_link`, `abs_link`, `tags`, `keywords`, `summary_zh`,
  `affiliation`, `affiliations`, `focus` (score, is_focus, primary_topic, topics, labels,
  matched_tags, matched_categories, reasons).
- `embeddings.parquet`: `id`, `text_hash`, `vector` (float32[384]). The Parquet schema metadata
  key `radar_embeddings` holds the model name and the six theme query vectors.
- `stats.json`: daily / cumulative tag and keyword counts used by the Trends page.
- `export_info.json`: counts, sizes and SHA-256 of the files above.

## How it is built

A GitHub Actions job runs daily: it restores the newest copy of this dataset, fetches the last
7 days from the arXiv API (3-second request spacing), tags new papers with an LLM (rule-based
fallback when no key is configured), embeds new or changed papers incrementally, and uploads
the merged result.

## License

This dataset mixes two kinds of content under different terms:

| Part | Fields | Terms |
|---|---|---|
| arXiv metadata | `id`, `title`, `abstract`, `authors`, `categories`, `published_date`, `pdf_link`, `abs_link` | CC0 1.0, as released by arXiv. Not restricted by this dataset's license. |
| FinPaperRadar additions | `tags`, `keywords`, `summary_zh` (Chinese summaries), `affiliation(s)` normalisation, `focus` scores, `embeddings.parquet`, `stats.json`, and the curation / compilation of the dataset | [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Please credit "FinPaperRadar" and cite as below. |

The papers themselves (full texts, PDFs, figures) are **not** included; each paper keeps its own
license on arXiv.

许可说明：标签、关键词、中文摘要、机构规范化、focus 评分、向量、统计数据以及数据集的整理与汇编按
CC BY 4.0 授权；arXiv 元数据（标题、作者、摘要、分类等）本身为 CC0，不受此限制。论文全文不在本数据集中。

## Limitations

- Only metadata and abstracts are included. No full texts, PDFs or figures.
- Tags, summaries, affiliations and focus scores are machine-generated navigation aids and may
  be wrong. Check every claim against the original arXiv record.
- Coverage is limited by the categories above and by `MAX_RESULTS_PER_CATEGORY` per run.

## Citation

```bibtex
@misc{finpaperradar_{{year}},
  title        = {{FinPaperRadar}: {AI} $\times$ Finance {arXiv} Paper Radar},
  author       = {Qi, Guohao and {Quant Group, FinTech Association of Hunan University}},
  year         = {{{year}}},
  howpublished = {\url{{{dataset_url}}}},
  note         = {Snapshot {{generated_date}}. Dataset licensed under CC BY 4.0},
  doi          = {10.XXXX/TBD}
}
```

The DOI above is a placeholder until one is minted.

## Acknowledgement

Thank you to arXiv for use of its open access interoperability.
