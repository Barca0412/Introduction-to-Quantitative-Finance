import fs from 'node:fs/promises'
import path from 'node:path'
import { fileURLToPath } from 'node:url'

import { env, pipeline } from '@xenova/transformers'

const __filename = fileURLToPath(import.meta.url)
const __dirname = path.dirname(__filename)
const BASE_DIR = path.resolve(__dirname, '..', '..')
const DATA_DIR = path.join(BASE_DIR, 'data')
const PUBLIC_DATA_DIR = path.join(BASE_DIR, 'docs', 'public', 'arxiv-data')

const MODEL_NAME = 'Xenova/all-MiniLM-L6-v2'
const OUTPUT_FILE = path.join(DATA_DIR, 'embeddings_index.json')
const PUBLIC_OUTPUT_FILE = path.join(PUBLIC_DATA_DIR, 'embeddings_index.json')
const BATCH_SIZE = 24

const THEME_QUERIES = {
  'ai-finance': 'AI agents and large language models for finance, trading, portfolio management, risk forecasting, quantitative research, financial analysis, market intelligence',
  'agent-planning': 'autonomous agent planning, workflow decomposition, long-horizon execution, reasoning and acting, replanning, tool orchestration',
  'deep-research': 'deep research agent, literature review, evidence gathering, report synthesis, multi-step search, research workflow, survey generation',
  'multi-agent': 'multi-agent systems, coordinating multiple AI agents, agent teams, debate, communication, collaboration',
  'tool-use': 'tool use by language models, function calling, browser use, computer use, API use, external tools',
  'reasoning': 'reasoning language models, chain of thought, inference-time reasoning, step by step problem solving',
}

env.allowLocalModels = false
env.useBrowserCache = false

function buildPaperText(paper) {
  return [
    paper.title,
    paper.abstract,
    paper.summary_zh,
    Array.isArray(paper.keywords) ? paper.keywords.join(', ') : '',
    Array.isArray(paper.tags) ? paper.tags.join(', ') : '',
    Array.isArray(paper.categories) ? paper.categories.join(', ') : '',
    Array.isArray(paper.affiliations) ? paper.affiliations.join(', ') : paper.affiliation || '',
  ]
    .filter(Boolean)
    .join('\n')
}

function dotProduct(left, right) {
  let total = 0
  for (let index = 0; index < left.length; index += 1) {
    total += left[index] * right[index]
  }
  return Number(total.toFixed(6))
}

function roundVector(vector) {
  return vector.map((value) => Number(value.toFixed(6)))
}

async function embedTexts(extractor, texts) {
  const output = await extractor(texts, { pooling: 'mean', normalize: true })
  const vectors = output.tolist()
  return Array.isArray(texts) ? vectors.map(roundVector) : [roundVector(vectors)]
}

async function main() {
  const papersFile = path.join(DATA_DIR, 'papers.json')
  const papersPayload = JSON.parse(await fs.readFile(papersFile, 'utf-8'))
  const papers = papersPayload.papers || []

  await fs.mkdir(PUBLIC_DATA_DIR, { recursive: true })

  if (papers.length === 0) {
    const emptyPayload = {
      model: MODEL_NAME,
      generated_at: new Date().toISOString(),
      dimension: 0,
      theme_queries: THEME_QUERIES,
      theme_vectors: {},
      papers: [],
    }
    await fs.writeFile(OUTPUT_FILE, JSON.stringify(emptyPayload))
    await fs.writeFile(PUBLIC_OUTPUT_FILE, JSON.stringify(emptyPayload))
    console.log(`No papers found in ${papersFile}; wrote empty embedding index`)
    return
  }

  console.log(`Loading embedding model: ${MODEL_NAME}`)
  const extractor = await pipeline('feature-extraction', MODEL_NAME)

  console.log(`Embedding ${papers.length} papers...`)
  const paperEmbeddings = []

  for (let index = 0; index < papers.length; index += BATCH_SIZE) {
    const batch = papers.slice(index, index + BATCH_SIZE)
    const texts = batch.map(buildPaperText)
    const vectors = await embedTexts(extractor, texts)
    batch.forEach((paper, batchIndex) => {
      paperEmbeddings.push({
        id: paper.id,
        vector: vectors[batchIndex],
      })
    })
    console.log(`Embedded ${Math.min(index + BATCH_SIZE, papers.length)}/${papers.length}`)
  }

  const themeEntries = Object.entries(THEME_QUERIES)
  const themeVectorsList = await embedTexts(extractor, themeEntries.map(([, query]) => query))
  const themeVectors = Object.fromEntries(
    themeEntries.map(([themeId], index) => [themeId, themeVectorsList[index]])
  )

  const themeScores = {}
  for (const embedding of paperEmbeddings) {
    themeScores[embedding.id] = Object.fromEntries(
      Object.entries(themeVectors).map(([themeId, vector]) => [themeId, dotProduct(embedding.vector, vector)])
    )
  }

  const payload = {
    model: MODEL_NAME,
    generated_at: new Date().toISOString(),
    dimension: paperEmbeddings[0]?.vector?.length || 0,
    theme_queries: THEME_QUERIES,
    theme_vectors: themeVectors,
    papers: paperEmbeddings.map((embedding) => ({
      id: embedding.id,
      vector: embedding.vector,
      theme_scores: themeScores[embedding.id],
    })),
  }

  await fs.writeFile(OUTPUT_FILE, JSON.stringify(payload))
  await fs.writeFile(PUBLIC_OUTPUT_FILE, JSON.stringify(payload))
  console.log(`Saved embeddings index to ${OUTPUT_FILE}`)
}

main().catch((error) => {
  console.error(error)
  process.exit(1)
})
