// Incremental paper embeddings for the arXiv Radar.
//
// Input : data/papers.json            (full history, restored by data_store.py)
//         data/embeddings.f32 + .meta.json  (previous vectors, optional)
// Output: data/embeddings.f32         raw little-endian float32, one row per paper
//         data/embeddings.meta.json   ids (row order), text hashes, model, theme vectors
//
// Only papers that are new, or whose embedded text changed, are re-embedded.
// Vectors built with an older text recipe (or imported from the legacy JSON, which
// carries no hash) are reused but marked stale (empty hash), and refreshed
// gradually: at most RADAR_EMBED_REFRESH_LIMIT of them per run, newest papers first.
// The site gets an int8 copy built by build_site_data.py; this full-precision
// matrix only goes to the Parquet export (Hugging Face / GitHub Release).
import crypto from 'node:crypto'
import fs from 'node:fs/promises'
import path from 'node:path'
import { fileURLToPath } from 'node:url'

import { env, pipeline } from '@xenova/transformers'

const __filename = fileURLToPath(import.meta.url)
const __dirname = path.dirname(__filename)
const BASE_DIR = path.resolve(__dirname, '..', '..')
const DATA_DIR = path.join(BASE_DIR, 'data')

const MODEL_NAME = 'Xenova/all-MiniLM-L6-v2'
const PAPERS_FILE = path.join(DATA_DIR, 'papers.json')
const EMB_BIN = path.join(DATA_DIR, 'embeddings.f32')
const EMB_META = path.join(DATA_DIR, 'embeddings.meta.json')
const BATCH_SIZE = 24
// Bump when buildPaperText() changes: every stored vector then becomes stale and
// is refreshed gradually instead of all at once.
const TEXT_RECIPE = 'v1'
const REFRESH_LIMIT = Number.parseInt(process.env.RADAR_EMBED_REFRESH_LIMIT || '3000', 10)

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

const textHash = (text) => crypto.createHash('sha1').update(text).digest('hex').slice(0, 16)

async function readPrevious() {
  try {
    const meta = JSON.parse(await fs.readFile(EMB_META, 'utf-8'))
    const buffer = await fs.readFile(EMB_BIN)
    const matrix = new Float32Array(buffer.buffer, buffer.byteOffset, buffer.byteLength / 4)
    const dim = meta.dimension || 0
    if (!dim || matrix.length !== dim * (meta.ids || []).length) {
      console.warn('Previous embeddings are inconsistent; recomputing everything')
      return null
    }
    return { meta, matrix, dim }
  } catch {
    return null
  }
}

async function embedTexts(extractor, texts) {
  const output = await extractor(texts, { pooling: 'mean', normalize: true })
  return output.tolist()
}

async function main() {
  const papers = (JSON.parse(await fs.readFile(PAPERS_FILE, 'utf-8')).papers || []).filter((p) => p.id)
  const previous = await readPrevious()
  const reuseAllowed = previous && previous.meta.model === MODEL_NAME

  const sameRecipe = reuseAllowed && previous.meta.text_recipe === TEXT_RECIPE
  const previousRows = new Map()
  if (reuseAllowed) {
    previous.meta.ids.forEach((id, row) => {
      // A different recipe makes every old hash meaningless: treat the vector as stale.
      const hash = sameRecipe ? previous.meta.text_hashes?.[row] ?? '' : ''
      previousRows.set(id, { row, hash })
    })
  }

  const currentHashes = papers.map((paper) => textHash(buildPaperText(paper)))
  const hashes = new Array(papers.length)
  const todo = []
  const stale = []
  papers.forEach((paper, index) => {
    const prior = previousRows.get(paper.id)
    if (!prior) {
      todo.push(index) // new paper
    } else if (prior.hash === '') {
      stale.push(index) // reusable, but built from unknown / older text
    } else if (prior.hash !== currentHashes[index]) {
      todo.push(index) // text changed (e.g. new tags or summary)
    }
  })
  // papers.json is sorted newest first, so the site's recent window is refreshed first.
  const refresh = stale.slice(0, Math.max(0, REFRESH_LIMIT))
  todo.push(...refresh)
  const refreshed = new Set(refresh)
  papers.forEach((_, index) => {
    const prior = previousRows.get(papers[index].id)
    const keptStale = prior && prior.hash === '' && !refreshed.has(index)
    hashes[index] = keptStale ? '' : currentHashes[index]
  })

  const sameThemes = reuseAllowed
    && JSON.stringify(previous.meta.theme_queries || {}) === JSON.stringify(THEME_QUERIES)
    && Object.keys(previous.meta.theme_vectors || {}).length === Object.keys(THEME_QUERIES).length

  console.log(
    `Papers: ${papers.length}; reusing ${papers.length - todo.length} vectors; embedding ${todo.length}`
      + ` (${todo.length - refresh.length} new/changed, ${refresh.length} stale refreshed,`
      + ` ${stale.length - refresh.length} stale left for later runs)`
  )

  let extractor = null
  if (todo.length > 0 || !sameThemes) {
    console.log(`Loading embedding model: ${MODEL_NAME}`)
    extractor = await pipeline('feature-extraction', MODEL_NAME)
  }

  const fresh = new Map()
  for (let start = 0; start < todo.length; start += BATCH_SIZE) {
    const batch = todo.slice(start, start + BATCH_SIZE)
    const vectors = await embedTexts(extractor, batch.map((index) => buildPaperText(papers[index])))
    batch.forEach((index, offset) => fresh.set(index, vectors[offset]))
    if ((start / BATCH_SIZE) % 20 === 0 || start + BATCH_SIZE >= todo.length) {
      console.log(`Embedded ${Math.min(start + BATCH_SIZE, todo.length)}/${todo.length}`)
    }
  }

  const dim = fresh.size ? fresh.values().next().value.length : previous?.dim || 384
  const matrix = new Float32Array(papers.length * dim)
  papers.forEach((paper, index) => {
    const vector = fresh.get(index)
    if (vector) {
      matrix.set(vector, index * dim)
    } else {
      const { row } = previousRows.get(paper.id)
      matrix.set(previous.matrix.subarray(row * dim, (row + 1) * dim), index * dim)
    }
  })

  let themeVectors = previous?.meta?.theme_vectors || {}
  if (!sameThemes) {
    const entries = Object.entries(THEME_QUERIES)
    const vectors = await embedTexts(extractor, entries.map(([, query]) => query))
    themeVectors = Object.fromEntries(entries.map(([id], index) => [id, vectors[index].map((v) => Number(v.toFixed(6)))]))
  }

  const meta = {
    model: MODEL_NAME,
    generated_at: new Date().toISOString(),
    dimension: dim,
    text_recipe: TEXT_RECIPE,
    theme_queries: THEME_QUERIES,
    theme_vectors: themeVectors,
    ids: papers.map((paper) => paper.id),
    text_hashes: hashes,
  }

  await fs.mkdir(DATA_DIR, { recursive: true })
  await fs.writeFile(`${EMB_BIN}.tmp`, Buffer.from(matrix.buffer))
  await fs.rename(`${EMB_BIN}.tmp`, EMB_BIN)
  await fs.writeFile(EMB_META, JSON.stringify(meta))
  console.log(`Saved ${papers.length} x ${dim} embeddings to ${EMB_BIN}`)
}

main().catch((error) => {
  console.error(error)
  process.exit(1)
})
