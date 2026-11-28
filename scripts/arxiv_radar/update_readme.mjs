import fs from 'node:fs/promises'
import path from 'node:path'
import { fileURLToPath } from 'node:url'

import { esc, fmt, heroSvg, pauseLine, radarPipelineSvg, radarSnapshotSvg, snapshotDescription } from './readme_svg.mjs'

const __filename = fileURLToPath(import.meta.url)
const __dirname = path.dirname(__filename)
const BASE_DIR = path.resolve(__dirname, '..', '..')

const README_FILE = path.join(BASE_DIR, 'README.md')
const PAPERS_FILE = path.join(BASE_DIR, 'data', 'papers.json')
const STATS_FILE = path.join(BASE_DIR, 'data', 'stats.json')
const SVG_DIR = path.join(BASE_DIR, 'assets', 'readme')
const TUTORIALS_DIR = path.join(BASE_DIR, 'docs', 'tutorials')
const REPORTS_DIR = path.join(BASE_DIR, '资料', '卖方金工研报')

// Dataset locations come from the environment so the HF namespace is never hard-coded.
const HF_DATASET_REPO = (process.env.HF_DATASET_REPO || '').trim()
const GITHUB_REPOSITORY = (process.env.GITHUB_REPOSITORY || 'Barca0412/Introduction-to-Quantitative-Finance').trim()
const RADAR_RELEASE_TAG = (process.env.RADAR_RELEASE_TAG || 'radar-data').trim()
const RADAR_URL = 'https://quant.hfthnu.com/arxiv/'

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
  return `- Full dataset (CC BY 4.0 for FinPaperRadar additions): ${links.join(' · ')}`
}

/** The Chinese sentence under the snapshot card; the arXiv-holiday notice links to arXiv's list. */
export function summaryZh(statsPayload, latestUpdate) {
  const site = statsPayload.site_summary || {}
  const since = site.since ? `，${String(site.since).slice(0, 4)} 年起` : ''
  let text = `截至 ${latestUpdate}，网站收录 ${fmt(site.papers ?? 0)} 篇 AI × 金融论文（核心 ${fmt(site.core_papers ?? 0)} 篇${since}），最新一篇发表于 ${site.latest || 'N/A'}。`
  const schedule = statsPayload.arxiv_schedule
  if (schedule?.level === 'holiday' && schedule.notice_zh) {
    const link = schedule.link_text_zh
    text += link && schedule.source_url ? schedule.notice_zh.replace(link, `[${link}](${schedule.source_url})`) : schedule.notice_zh
  } else if (schedule?.level) {
    text += pauseLine(schedule)
  }
  return text
}

export function buildStatusBlock(statsPayload, papersPayload) {
  const summary = statsPayload.summary || {}
  const site = statsPayload.site_summary || {}
  const papers = papersPayload.papers || []
  const latestPaperDate = summary.latest_published_date || papers[0]?.published_date || 'N/A'
  const latestUpdate = formatDate(statsPayload.last_updated || papersPayload.last_updated)
  // Written by arxiv_calendar.py when arXiv itself paused (weekend, holiday list, deferral).
  const schedule = statsPayload.arxiv_schedule
  const scheduleLine = schedule?.notice_en ? [`- arXiv schedule: ${schedule.notice_en}`] : []

  return [
    START_MARKER,
    '<p align="center">',
    `  <a href="${RADAR_URL}"><img src="./assets/readme/radar-snapshot.svg" width="100%" alt="${esc(snapshotDescription(statsPayload))}"></a>`,
    '</p>',
    '',
    summaryZh(statsPayload, latestUpdate),
    '',
    '<details>',
    '<summary>FinPaperRadar machine-updated status (English)</summary>',
    '',
    `- Latest update: ${latestUpdate}`,
    `- AI × finance papers on the site: ${site.papers ?? 0} (core ${site.core_papers ?? 0}; relevance ≥ 2 with an AI/ML method, since ${site.since || 'N/A'})`,
    `- Latest publication date: ${site.latest || latestPaperDate}`,
    ...scheduleLine,
    `- Monitored arXiv categories: ${summary.monitored_categories ?? 15} (plus finance papers from cs.LG and stat.ML)`,
    `- Papers in the open dataset (all fetched, incl. not relevant): ${summary.total_papers ?? papers.length}`,
    datasetLine(),
    '',
    '</details>',
    END_MARKER,
  ].join('\n')
}

async function countLectures() {
  const entries = await fs.readdir(TUTORIALS_DIR, { withFileTypes: true }).catch(() => [])
  return entries.filter((e) => e.isDirectory() && /^\d+-/.test(e.name)).length
}

// Same rule as scripts/site/gen_library.mjs: every PDF under 资料/卖方金工研报.
async function countReports(dir = REPORTS_DIR) {
  const entries = await fs.readdir(dir, { withFileTypes: true }).catch(() => [])
  let n = 0
  for (const e of entries) {
    if (e.isDirectory()) n += await countReports(path.join(dir, e.name))
    else if (path.extname(e.name).toLowerCase() === '.pdf') n += 1
  }
  return n
}

export async function writeSvgs(statsPayload, dir = SVG_DIR) {
  const site = statsPayload.site_summary || {}
  const summary = statsPayload.summary || {}
  const facts = {
    lectures: await countLectures(),
    reports: await countReports(),
    sitePapers: site.papers ?? 0,
    datasetPapers: summary.total_papers ?? 0,
    latest: site.latest || summary.latest_published_date || '',
  }
  await fs.mkdir(dir, { recursive: true })
  await Promise.all([
    fs.writeFile(path.join(dir, 'hero.svg'), heroSvg(facts)),
    fs.writeFile(path.join(dir, 'radar-snapshot.svg'), radarSnapshotSvg(statsPayload)),
    fs.writeFile(path.join(dir, 'radar-pipeline.svg'), radarPipelineSvg({ categories: summary.monitored_categories ?? 15 })),
  ])
  return facts
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

  // A function replacement, so "$" in the text is never read as a regex group.
  const next = readme.replace(pattern, () => replacement)
  await fs.writeFile(README_FILE, next)
  const facts = await writeSvgs(statsPayload)
  console.log(`Updated README arXiv radar status block and assets/readme/*.svg (${JSON.stringify(facts)})`)
}

if (process.argv[1] && path.resolve(process.argv[1]) === __filename) {
  main().catch((error) => {
    console.error(error)
    process.exit(1)
  })
}
