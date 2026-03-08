import fs from 'node:fs/promises'
import path from 'node:path'
import { fileURLToPath } from 'node:url'

const __filename = fileURLToPath(import.meta.url)
const __dirname = path.dirname(__filename)
const BASE_DIR = path.resolve(__dirname, '..', '..')

const README_FILE = path.join(BASE_DIR, 'README.md')
const PAPERS_FILE = path.join(BASE_DIR, 'data', 'papers.json')
const STATS_FILE = path.join(BASE_DIR, 'data', 'stats.json')

const START_MARKER = '<!-- ARXIV_RADAR_STATUS:START -->'
const END_MARKER = '<!-- ARXIV_RADAR_STATUS:END -->'

function formatDate(value) {
  if (!value) return 'N/A'
  return new Date(value).toISOString().slice(0, 10)
}

function buildStatusBlock(statsPayload, papersPayload) {
  const summary = statsPayload.summary || {}
  const papers = papersPayload.papers || []
  const latestPaperDate = summary.latest_published_date || papers[0]?.published_date || 'N/A'
  const latestUpdate = formatDate(statsPayload.last_updated || papersPayload.last_updated)

  return [
    START_MARKER,
    '> [!NOTE]',
    '> Machine-updated arXiv Radar Status',
    `> - Latest update: ${latestUpdate}`,
    `> - Indexed papers: ${summary.total_papers ?? papers.length}`,
    `> - Focus papers: ${summary.focus_papers ?? 0}`,
    `> - Latest publication date: ${latestPaperDate}`,
    `> - Monitored categories: ${summary.monitored_categories ?? 10}`,
    END_MARKER,
  ].join('\n')
}

async function main() {
  const [readme, papersPayload, statsPayload] = await Promise.all([
    fs.readFile(README_FILE, 'utf8'),
    fs.readFile(PAPERS_FILE, 'utf8').then(JSON.parse),
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
