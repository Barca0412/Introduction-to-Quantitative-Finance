// README 横幅、雷达快照卡和状态块（scripts/arxiv_radar/readme_svg.mjs、update_readme.mjs）。
import test from 'node:test'
import assert from 'node:assert/strict'
import { mkdtempSync, readFileSync, rmSync } from 'node:fs'
import { tmpdir } from 'node:os'
import { join } from 'node:path'
import { esc, heroSvg, pauseLine, radarPipelineSvg, radarSnapshotSvg, zhDay } from '../../arxiv_radar/readme_svg.mjs'
import { buildStatusBlock, summaryZh, writeSvgs } from '../../arxiv_radar/update_readme.mjs'

const HOLIDAY = {
  level: 'holiday',
  skipped: [
    { date: '2026-11-27', reason: 'weekend' },
    { date: '2026-11-26', reason: 'holiday', name_zh: '美国感恩节', name_en: 'US Thanksgiving' },
  ],
  next_bj: '2026-11-30T09:00+08:00',
  source_url: 'https://info.arxiv.org/help/availability.html',
  notice_zh: '11 月 26 日（周四）是美国感恩节，在 arXiv 官方的 2026 假期名单上，当天晚上那一期停发了。',
  link_text_zh: 'arXiv 官方的 2026 假期名单',
  notice_en: 'No announcement on 2026-11-26.',
}
const WEEKEND = { level: 'weekend', skipped: [{ date: '2026-11-20', reason: 'weekend' }], next_bj: '2026-11-23T09:00+08:00' }

function stats(schedule = null) {
  return {
    last_updated: '2026-11-28T11:42:19.660389',
    summary: { total_papers: 34461, monitored_categories: 15, latest_published_date: '2026-11-25' },
    site_summary: {
      papers: 471, core_papers: 325, since: '2022-01-01', latest: '2026-11-25',
      domains: [
        { id: 'asset-pricing', zh: '资产定价与因子', papers: 84 },
        { id: 'credit-banking', zh: '信用、银行与支付', papers: 78 },
        { id: 'x', zh: 'R&D <测试>', papers: 7 },
      ],
    },
    arxiv_schedule: schedule,
  }
}

function wellFormed(svg) {
  assert.ok(svg.startsWith('<svg xmlns="http://www.w3.org/2000/svg"'))
  assert.ok(svg.trimEnd().endsWith('</svg>'))
  assert.equal((svg.match(/<text /g) || []).length, (svg.match(/<\/text>/g) || []).length)
  // Every "&" starts an entity; no raw "<" inside text.
  assert.doesNotMatch(svg, /&(?!(amp|lt|gt|quot|#39);)/)
  assert.ok(svg.includes('<title id="t">') && svg.includes('<desc id="d">'))
}

test('esc and zhDay', () => {
  assert.equal(esc(`a & <b> "c" 'd'`), 'a &amp; &lt;b&gt; &quot;c&quot; &#39;d&#39;')
  assert.deepEqual(zhDay('2026-11-26'), { md: '11 月 26 日', wd: '周四' })
  assert.deepEqual(zhDay('2026-11-30T09:00+08:00'), { md: '11 月 30 日', wd: '周一' })
  assert.deepEqual(zhDay(''), { md: '', wd: '' })
})

test('hero shows the four numbers and the tagline', () => {
  const svg = heroSvg({ lectures: 2, reports: 194, sitePapers: 471, datasetPapers: 34461, latest: '2026-11-25' })
  wellFormed(svg)
  for (const s of ['>2<', '>194<', '>471<', '>34,461<', '量化课程讲义、研报与论文目录，', '和每天更新的 AI × 金融论文雷达', '论文数据截至 2026-11-25']) {
    assert.ok(svg.includes(s), s)
  }
})

test('pause line: holiday, weekend, on schedule', () => {
  assert.equal(pauseLine(HOLIDAY), 'arXiv 停发：11 月 26 日（周四）美国感恩节；周五、周六本来不发。下一期预计北京时间 11 月 30 日（周一）上午。')
  assert.equal(pauseLine(WEEKEND), 'arXiv 周五、周六不发新论文。下一期预计北京时间 11 月 23 日（周一）上午。')
  assert.equal(pauseLine(null), '')
  const deferred = { level: 'holiday', skipped: [{ date: '2026-11-18', reason: 'deferred', reason_zh: '系统维护' }], next_bj: '2026-11-20T09:00+08:00' }
  assert.match(pauseLine(deferred), /11 月 18 日（周三）临时停发（系统维护）/)
})

test('snapshot card: numbers, escaped domains, pause row only when arXiv paused', () => {
  const holiday = radarSnapshotSvg(stats(HOLIDAY))
  wellFormed(holiday)
  assert.ok(holiday.includes('>471<') && holiday.includes('资产定价与因子') && holiday.includes('R&amp;D &lt;测试&gt;'))
  assert.ok(holiday.includes('美国感恩节') && holiday.includes('height="384"'))
  const normal = radarSnapshotSvg(stats())
  wellFormed(normal)
  assert.ok(!normal.includes('停发') && normal.includes('height="330"'))
  // Before the first run with site_summary.domains, the card still renders, without bars.
  const old = stats(); delete old.site_summary.domains
  const bare = radarSnapshotSvg(old)
  wellFormed(bare)
  assert.ok(!bare.includes('按金融领域'))
})

test('pipeline diagram', () => {
  const svg = radarPipelineSvg({ categories: 15 })
  wellFormed(svg)
  assert.ok(svg.includes('15 个分类的新论文') && svg.includes('Hugging Face 数据集'))
})

test('status block: card, Chinese summary with the arXiv link, English details', () => {
  const block = buildStatusBlock(stats(HOLIDAY), { papers: [] })
  assert.ok(block.startsWith('<!-- ARXIV_RADAR_STATUS:START -->') && block.endsWith('<!-- ARXIV_RADAR_STATUS:END -->'))
  assert.ok(block.includes('src="./assets/readme/radar-snapshot.svg"'))
  assert.ok(block.includes('alt="论文雷达快照：网站收录 471 篇') && block.includes('R&amp;D &lt;测试&gt;'))
  assert.ok(block.includes('[arXiv 官方的 2026 假期名单](https://info.arxiv.org/help/availability.html)上'))
  assert.ok(block.includes('<details>') && block.includes('- arXiv schedule: No announcement on 2026-11-26.'))
  assert.equal(summaryZh(stats(), '2026-11-28'), '截至 2026-11-28，网站收录 471 篇 AI × 金融论文（核心 325 篇，2022 年起），最新一篇发表于 2026-11-25。')
  assert.match(summaryZh(stats(WEEKEND), '2026-11-21'), /。arXiv 周五、周六不发新论文。下一期预计北京时间 11 月 23 日（周一）上午。$/)
})

test('writeSvgs counts lectures and reports from the repo and writes three files', async () => {
  const dir = mkdtempSync(join(tmpdir(), 'readme-svg-'))
  try {
    const facts = await writeSvgs(stats(HOLIDAY), dir)
    assert.ok(facts.lectures >= 2 && facts.reports >= 100)
    for (const f of ['hero.svg', 'radar-snapshot.svg', 'radar-pipeline.svg']) wellFormed(readFileSync(join(dir, f), 'utf8'))
  } finally {
    rmSync(dir, { recursive: true, force: true })
  }
})
