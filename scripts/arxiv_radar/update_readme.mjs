import fs from 'node:fs/promises'
import path from 'node:path'
import { fileURLToPath } from 'node:url'

const __filename = fileURLToPath(import.meta.url)
const __dirname = path.dirname(__filename)
const BASE_DIR = path.resolve(__dirname, '..', '..')

const README_FILE = path.join(BASE_DIR, 'README.md')
const PAPERS_FILE = path.join(BASE_DIR, 'data', 'papers.json')
const STATS_FILE = path.join(BASE_DIR, 'data', 'stats.json')

// Dataset locations come from the environment so the HF namespace is never hard-coded.
const HF_DATASET_REPO = (process.env.HF_DATASET_REPO || '').trim()
const GITHUB_REPOSITORY = (process.env.GITHUB_REPOSITORY || 'Barca0412/Introduction-to-Quantitative-Finance').trim()
const RADAR_RELEASE_TAG = (process.env.RADAR_RELEASE_TAG || 'radar-data').trim()

const START_MARKER = '<!-- ARXIV_RADAR_STATUS:START -->'
const END_MARKER = '<!-- ARXIV_RADAR_STATUS:END -->'

function formatDate(value) {
  if (!value) return 'N/A'
  return new Date(value).toISOString().slice(0, 10)
}

function datasetLine() {
  const links = []
  if (HF_DATASET_REPO) links.push(`[Hugging Face](https://huggingface.co/datasets/${HF_DATASET_REPO})`)
  links.push(`[GitHub Release mirror](https://github.com/${GITHUB_REPOSITORY}/releases/tag/${RADAR_RELEASE_TAG})`)
  return `> - Full dataset (CC BY 4.0 for FinPaperRadar additions): ${links.join(' · ')}`
}

function buildStatusBlock(statsPayload, papersPayload) {
  const summary = statsPayload.summary || {}
  const papers = papersPayload.papers || []
  const latestPaperDate = summary.latest_published_date || papers[0]?.published_date || 'N/A'
  const latestUpdate = formatDate(statsPayload.last_updated || papersPayload.last_updated)

  return [
    START_MARKER,
    '> [!NOTE]',
    '> FinPaperRadar（AI × 金融论文雷达）machine-updated status',
    `> - Latest update: ${latestUpdate}`,
    `> - Indexed papers: ${summary.total_papers ?? papers.length}`,
    `> - Focus papers: ${summary.focus_papers ?? 0}`,
    `> - Latest publication date: ${latestPaperDate}`,
    `> - Monitored categories: ${summary.monitored_categories ?? 10}`,
    datasetLine(),
    END_MARKER,
  ].join('\n')
}

async function main() {
  // papers.json is optional: the post-deploy README job only receives stats.json,
  // whose summary already carries the totals and the latest publication date.
  const [readme, papersPayload, statsPayload] = await Promise.all([
    fs.readFile(README_FILE, 'utf8'),
    fs.readFile(PAPERS_FILE, 'utf8').then(JSON.parse).catch(() => ({ papers: [] })),
    fs.readFile(STATS_FILE, 'utf8').then(JSON.parse),
  ])

  const replacement = buildStatusBlock(statsPayload, papersPayload)
  const pattern = new RegExp(`${START_MARKER}[\\s\\S]*?${END_MARKER}`)

  if (!pattern.test(readme)) {
    throw new Error('README status block markers not found')
  }

  const next = readme.replace(pattern, replacement)
  await fs.writeFile(README_FILE, next)
  console.log('Updated README arXiv radar status block')
}

main().catch((error) => {
  console.error(error)
  process.exit(1)
})
