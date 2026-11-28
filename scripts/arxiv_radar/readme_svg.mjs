// README 里的三张图：顶部横幅、论文雷达快照卡、雷达流程图。
// update_readme.mjs 每天用 data/stats.json 重画，写到 assets/readme/。
// 配色取自网站 docs/.vitepress/theme/tokens.css：墨绿底、浅色字、黄色只用在数据和小圆点上；
// 不用渐变和阴影，图形小圆角。墨绿底在 GitHub 浅色、深色模式下都能看，所以每张图只出一份。
// SVG 作为 <img> 显示时加载不了网页字体，字体栈退回系统字体，中文照常显示。

const C = {
  bg: '#0d2a1c',
  tile: '#123526',
  track: '#1c3d2e',
  rule: '#2a4a3c',
  fg: '#f7f7f7',
  muted: '#a7b6ad',
  accent: '#f6e016',
}
const FONT = "Jost, -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Hiragino Sans GB', 'Noto Sans SC', 'Microsoft YaHei', sans-serif"
const WEEKDAY_ZH = '日一二三四五六'

export const SITE_URL = 'https://quant.hfthnu.com/'

export function esc(value) {
  return String(value ?? '').replace(/[&<>"']/g, (ch) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[ch])
}

export function fmt(n) {
  return Number.isFinite(Number(n)) ? Number(n).toLocaleString('en-US') : '—'
}

// "2026-11-26" -> { md: "11 月 26 日", wd: "周四" }; plain calendar dates, no time zone involved.
export function zhDay(isoDate) {
  const [y, m, d] = String(isoDate).slice(0, 10).split('-').map(Number)
  if (!y || !m || !d) return { md: '', wd: '' }
  return { md: `${m} 月 ${d} 日`, wd: `周${WEEKDAY_ZH[new Date(Date.UTC(y, m - 1, d)).getUTCDay()]}` }
}

function text(x, y, body, { size = 16, fill = C.fg, weight = 400, anchor = 'start', spacing = 0 } = {}) {
  const ls = spacing ? ` letter-spacing="${spacing}"` : ''
  return `<text x="${x}" y="${y}" fill="${fill}" font-family="${FONT}" font-size="${size}" font-weight="${weight}" text-anchor="${anchor}"${ls}>${body}</text>`
}

function frame(width, height, title, desc, body) {
  return [
    `<svg xmlns="http://www.w3.org/2000/svg" width="${width}" height="${height}" viewBox="0 0 ${width} ${height}" role="img" aria-labelledby="t d">`,
    `<title id="t">${esc(title)}</title>`,
    `<desc id="d">${esc(desc)}</desc>`,
    `<rect width="${width}" height="${height}" rx="16" fill="${C.bg}"/>`,
    ...body,
    '</svg>',
    '',
  ].join('\n')
}

// The site's mark: a yellow dot before the name.
function mark(x, y, label, opts = {}) {
  return [`<circle cx="${x + 8}" cy="${y - 6}" r="8" fill="${C.accent}"/>`, text(x + 26, y, esc(label), { size: 18, fill: C.muted, weight: 500, ...opts })]
}

function number(x, y, value, unit, size = 40) {
  const u = unit ? `<tspan font-size="${Math.round(size * 0.5)}" font-weight="500" fill="${C.muted}" dx="6">${esc(unit)}</tspan>` : ''
  return text(x, y, `${esc(value)}${u}`, { size, fill: C.accent, weight: 600 })
}

/** Top banner: name and what is here on the left, four numbers in 2x2 tiles on the right.
 * `facts`: { lectures, reports, sitePapers, datasetPapers, latest }. */
export function heroSvg(facts) {
  const cells = [
    { value: fmt(facts.lectures), unit: '讲', label: '讲义，每讲一个完整项目' },
    { value: fmt(facts.reports), unit: '份', label: '卖方金工研报' },
    { value: fmt(facts.sitePapers), unit: '篇', label: '雷达收录 AI × 金融论文' },
    { value: fmt(facts.datasetPapers), unit: '篇', label: '开放数据集论文' },
  ]
  const lines = ['量化课程讲义、研报与论文目录，', '和每天更新的 AI × 金融论文雷达']
  const fresh = `每天自动更新 · 论文数据截至 ${facts.latest || '—'}`
  const desc = `${lines.join('')}。${cells.map((c) => `${c.label} ${c.value} ${c.unit}`).join('，')}。${fresh}。`
  const tiles = cells.flatMap((c, i) => {
    const x = 680 + (i % 2) * 242, y = 44 + Math.floor(i / 2) * 144
    return [
      `<rect x="${x}" y="${y}" width="226" height="128" rx="6" fill="${C.tile}"/>`,
      number(x + 22, y + 62, c.value, c.unit, 38),
      text(x + 22, y + 100, esc(c.label), { size: 17, fill: C.muted }),
    ]
  })
  return frame(1200, 360, '量化研究入门 · Introduction to Quantitative Finance', desc, [
    ...mark(52, 70, 'quant.hfthnu.com', { size: 20 }),
    text(52, 156, '量化研究入门', { size: 60, weight: 700, spacing: -1 }),
    text(52, 196, 'Introduction to Quantitative Finance', { size: 21, fill: C.muted }),
    ...lines.map((line, i) => text(52, 248 + i * 32, esc(line), { size: 21 })),
    text(52, 326, esc(fresh), { size: 17, fill: C.muted }),
    ...tiles,
  ])
}

/** One line on why the newest date stands still, built from stats.arxiv_schedule; '' when arXiv is on schedule. */
export function pauseLine(schedule) {
  if (!schedule?.level) return ''
  const next = zhDay(schedule.next_bj)
  const nextText = next.md ? `下一期预计北京时间 ${next.md}（${next.wd}）上午。` : ''
  const skipped = [...(schedule.skipped || [])].sort((a, b) => String(a.date).localeCompare(String(b.date)))
  const special = skipped.filter((s) => s.reason !== 'weekend').map((s) => {
    const d = zhDay(s.date)
    return s.reason === 'holiday' ? `${d.md}（${d.wd}）${s.name_zh}` : `${d.md}（${d.wd}）临时停发（${s.reason_zh || '见 arXiv 公告'}）`
  })
  const weekend = skipped.some((s) => s.reason === 'weekend')
  if (!special.length) return `arXiv 周五、周六不发新论文。${nextText}`
  return `arXiv 停发：${special.join('；')}${weekend ? '；周五、周六本来不发' : ''}。${nextText}`
}

/** Radar snapshot card from stats.json: big numbers left, papers per finance domain right. */
export function radarSnapshotSvg(stats, { topDomains = 6 } = {}) {
  const site = stats.site_summary || {}
  const summary = stats.summary || {}
  const domains = (site.domains || []).slice(0, topDomains)
  const pause = pauseLine(stats.arxiv_schedule)
  const holiday = stats.arxiv_schedule?.level === 'holiday'
  const W = 1200, H = pause ? 384 : 330
  const since = site.since ? `${String(site.since).slice(0, 4)} 年起` : ''

  const max = Math.max(1, ...domains.map((d) => d.papers || 0))
  const barX = 712, barW = 360, rowH = 30, top = 136
  const bars = domains.flatMap((d, i) => {
    const y = top + i * rowH
    const w = Math.max(4, Math.round((barW * (d.papers || 0)) / max))
    return [
      text(536, y + 14, esc(d.zh), { size: 18 }),
      `<rect x="${barX}" y="${y}" width="${barW}" height="14" rx="3" fill="${C.track}"/>`,
      `<rect x="${barX}" y="${y}" width="${w}" height="14" rx="3" fill="${C.accent}"/>`,
      text(1148, y + 14, fmt(d.papers), { size: 18, anchor: 'end', weight: 500 }),
    ]
  })

  const body = [
    ...mark(52, 66, 'FinPaperRadar · AI × 金融论文雷达', { fill: C.fg, weight: 600 }),
    text(1148, 66, `数据截至 ${esc(site.latest || '—')}`, { size: 18, fill: C.muted, anchor: 'end' }),
    text(52, 176, fmt(site.papers), { size: 76, fill: C.accent, weight: 600, spacing: -1 }),
    text(52, 216, '篇 AI × 金融论文在网站上', { size: 21 }),
    text(52, 246, esc(`其中核心论文 ${fmt(site.core_papers)} 篇${since ? ` · ${since}` : ''}`), { size: 18, fill: C.muted }),
    text(52, 274, esc(`监控 ${fmt(summary.monitored_categories ?? 15)} 个 arXiv 分类，每天更新`), { size: 18, fill: C.muted }),
    domains.length ? text(536, 112, '按金融领域（前 6 个，一篇可属多个领域）', { size: 17, fill: C.muted }) : '',
    ...bars,
  ]
  if (pause) {
    body.push(`<line x1="52" y1="320" x2="1148" y2="320" stroke="${C.rule}" stroke-width="1"/>`)
    if (holiday) body.push(`<circle cx="60" cy="350" r="6" fill="${C.accent}"/>`)
    body.push(text(holiday ? 76 : 52, 357, esc(pause), { size: 19, fill: holiday ? C.fg : C.muted }))
  }
  return frame(W, H, 'FinPaperRadar 论文雷达快照', snapshotDescription(stats, { topDomains }), body.filter(Boolean))
}

/** What the snapshot card says, as one sentence: its <desc> and the README alt text. */
export function snapshotDescription(stats, { topDomains = 6 } = {}) {
  const site = stats.site_summary || {}
  const domains = (site.domains || []).slice(0, topDomains)
  return `论文雷达快照：网站收录 ${fmt(site.papers)} 篇 AI × 金融论文，核心 ${fmt(site.core_papers)} 篇，最新论文 ${site.latest || '—'}。`
    + (domains.length ? `按金融领域：${domains.map((d) => `${d.zh} ${d.papers}`).join('，')}。` : '')
    + pauseLine(stats.arxiv_schedule)
}

/** How the Radar updates every day. Only the category count changes. */
export function radarPipelineSvg({ categories = 15 } = {}) {
  const W = 1200, H = 276, y = 96, h = 140, boxW = 240, gap = 48
  const boxes = [
    { title: 'arXiv', lines: [`${categories} 个分类的新论文`, 'cs.LG、stat.ML 只收金融的'] },
    { title: '每日抓取', lines: ['GitHub Actions', '每天自动运行一次'] },
    { title: '大模型处理', lines: ['打研究标签、提取关键词', '写中文摘要、评相关度'] },
  ]
  const outs = ['网站 quant.hfthnu.com', 'Hugging Face 数据集', '本 README']
  const arrow = (x1, x2, ay) => [
    `<line x1="${x1 + 8}" y1="${ay}" x2="${x2 - 12}" y2="${ay}" stroke="${C.muted}" stroke-width="1.5"/>`,
    `<path d="M${x2 - 14} ${ay - 5} L${x2 - 6} ${ay} L${x2 - 14} ${ay + 5} Z" fill="${C.muted}"/>`,
  ]
  const body = [...mark(52, 62, '论文雷达每天怎么更新', { fill: C.fg, size: 20, weight: 600 })]
  boxes.forEach((b, i) => {
    const x = 52 + i * (boxW + gap)
    body.push(`<rect x="${x}" y="${y}" width="${boxW}" height="${h}" rx="6" fill="${C.tile}"/>`)
    body.push(text(x + 20, y + 42, esc(b.title), { size: 21, weight: 600 }))
    b.lines.forEach((line, j) => body.push(text(x + 20, y + 80 + j * 28, esc(line), { size: 17, fill: C.muted })))
    body.push(...arrow(x + boxW, x + boxW + gap, y + h / 2))
  })
  const ox = 52 + 3 * (boxW + gap), oh = 40, og = 10
  outs.forEach((label, i) => {
    const oy = y + i * (oh + og)
    body.push(`<rect x="${ox}" y="${oy}" width="${1148 - ox}" height="${oh}" rx="6" fill="${C.tile}"/>`)
    body.push(`<circle cx="${ox + 18}" cy="${oy + oh / 2}" r="4" fill="${C.accent}"/>`)
    body.push(text(ox + 32, oy + 26, esc(label), { size: 17 }))
  })
  return frame(W, H, '论文雷达每天怎么更新', `arXiv ${categories} 个分类 → 每日抓取（GitHub Actions）→ 大模型打标签、写中文摘要、评相关度 → 网站、Hugging Face 数据集、本 README。`, body)
}
