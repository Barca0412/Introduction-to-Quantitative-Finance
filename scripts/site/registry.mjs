// Loads and validates the resource registry in data/registry/.
// Used by scripts/site/gen_resources.mjs (page generation) and by
// docs/.vitepress/config.ts (sidebar), so both see the same rules.
//
// Layout:
//   data/registry/sources.yaml       upstream lists we credit (+ licence, how we use them)
//   data/registry/pages.yaml         resource pages: key, kind, title, subs …
//   data/registry/items/<page>.yaml  the entries of one page
//   data/registry/stats.json         machine-written GitHub stats (refresh_stats.mjs)
import { existsSync, readFileSync, readdirSync } from 'node:fs'
import { join, basename } from 'node:path'
import { ROOT, readYaml } from './lib.mjs'

export const DEFAULT_DIR = join(ROOT, 'data', 'registry')

export const KINDS = {
  project: { required: ['url'] },
  data: { required: ['url', 'pricing'] },
  book: { required: ['authors'] },
  course: { required: ['url', 'provider'] },
  community: { required: ['url', 'type'] },
}
const TIERS = ['A', 'B']
const PRICING = ['free', 'freemium', 'paid']
const STATUS = ['active', 'stale', 'archived']
const COMMUNITY_TYPES = ['forum', 'blog', 'newsletter', 'podcast', 'video', 'wechat', 'research-center', 'exchange', 'regulator', 'jobs', 'question-bank', 'other']
export const WHY_MAX = 60
// Months without a push before a GitHub project is shown as 已停更.
export const STALE_MONTHS = 18

// Pirate / unauthorised-copy hosts. Any URL on these fails the build.
export const BLOCKED_HOSTS = [
  'welib.org', 'oceanofpdf.com', 'dokumen.pub', 'scribd.com', 'libgen', 'library.lol',
  'z-lib', 'zlibrary', 'z-library', '1lib', 'b-ok.', 'pdfdrive.com', 'pdf4pro.com', 'vdoc.pub', 'epdf.pub',
]

const DATE_RE = /^\d{4}-\d{2}-\d{2}$/
const ID_RE = /^[A-Za-z0-9][A-Za-z0-9._\-/]*$/

const asList = (v) => (Array.isArray(v) ? v : v == null ? [] : [v])
const dateText = (v) => (v instanceof Date ? v.toISOString().slice(0, 10) : v == null ? null : String(v))

export function isBlockedUrl(url) {
  let host = ''
  try {
    host = new URL(url).hostname.toLowerCase()
  } catch {
    return false
  }
  return BLOCKED_HOSTS.some((bad) => host.includes(bad))
}

function checkUrl(value, where, errors) {
  if (value == null || value === '') return
  if (!/^https?:\/\/[^\s]+$/.test(String(value))) errors.push(`${where}: 不是有效的 http(s) 链接: ${value}`)
  else if (isBlockedUrl(value)) errors.push(`${where}: 链接指向盗版或未授权转载站点: ${value}`)
}

// Returns { sources, pages, items, stats, errors, warnings }. Never throws on bad data;
// callers decide whether errors are fatal.
export function loadRegistry(dir = DEFAULT_DIR) {
  const errors = []
  const warnings = []
  const result = { dir, options: { credits_page: true }, sources: [], pages: [], items: [], stats: { repos: {} }, errors, warnings }
  if (!existsSync(dir)) return result

  const sourcesFile = join(dir, 'sources.yaml')
  const pagesFile = join(dir, 'pages.yaml')
  result.sources = existsSync(sourcesFile) ? asList(readYaml(sourcesFile).sources) : []
  const pagesDoc = existsSync(pagesFile) ? readYaml(pagesFile) : {}
  result.pages = asList(pagesDoc.pages)
  result.options = { ...result.options, ...(pagesDoc.options ?? {}) }
  const statsFile = join(dir, 'stats.json')
  if (existsSync(statsFile)) result.stats = JSON.parse(readFileSync(statsFile, 'utf8'))
  result.stats.repos ??= {}

  const sourceIds = new Set()
  for (const s of result.sources) {
    if (!s?.id) { errors.push(`sources.yaml: 有来源缺少 id`); continue }
    if (sourceIds.has(s.id)) errors.push(`sources.yaml: 来源 id 重复: ${s.id}`)
    sourceIds.add(s.id)
    checkUrl(s.url, `sources.yaml ${s.id}`, errors)
    if (!s.license) errors.push(`sources.yaml ${s.id}: 缺少 license`)
    if (!['link-only', 'adapt-with-credit'].includes(s.use)) errors.push(`sources.yaml ${s.id}: use 只能是 link-only 或 adapt-with-credit`)
  }

  const pageByKey = new Map()
  for (const p of result.pages) {
    if (!p?.key || !/^[a-z0-9-]+$/.test(p.key)) { errors.push(`pages.yaml: 页面 key 缺失或含非法字符: ${p?.key}`); continue }
    if (pageByKey.has(p.key)) errors.push(`pages.yaml: 页面 key 重复: ${p.key}`)
    if (['index', 'credits'].includes(p.key)) errors.push(`pages.yaml: 页面 key 不能用保留名 ${p.key}`)
    if (!KINDS[p.kind]) errors.push(`pages.yaml ${p.key}: kind 必须是 ${Object.keys(KINDS).join('/')}`)
    for (const f of ['title', 'description']) if (!p[f]) errors.push(`pages.yaml ${p.key}: 缺少 ${f}`)
    p.subs = asList(p.subs)
    const subKeys = new Set()
    for (const s of p.subs) {
      if (!s?.key || !s?.title) errors.push(`pages.yaml ${p.key}: 子分类缺少 key 或 title`)
      else if (subKeys.has(s.key)) errors.push(`pages.yaml ${p.key}: 子分类 key 重复: ${s.key}`)
      subKeys.add(s?.key)
    }
    pageByKey.set(p.key, p)
  }

  const itemsDir = join(dir, 'items')
  const files = existsSync(itemsDir) ? readdirSync(itemsDir).filter((f) => f.endsWith('.yaml')).sort() : []
  const ids = new Map()
  for (const file of files) {
    const pageKey = basename(file, '.yaml')
    const page = pageByKey.get(pageKey)
    const where0 = `items/${file}`
    if (!page) { errors.push(`${where0}: pages.yaml 里没有名为 ${pageKey} 的页面`); continue }
    const doc = readYaml(join(itemsDir, file))
    for (const [i, raw] of asList(doc.items).entries()) {
      const where = `${where0} 第 ${i + 1} 条${raw?.id ? ` (${raw.id})` : ''}`
      if (!raw || typeof raw !== 'object') { errors.push(`${where}: 不是对象`); continue }
      const item = { ...raw, page: pageKey, kind: page.kind }
      item.reviewed = dateText(item.reviewed)
      item.added = dateText(item.added)
      item.sources = asList(item.sources)
      item.tags = asList(item.tags)
      item.lectures = asList(item.lectures)

      if (!item.id || !ID_RE.test(item.id)) errors.push(`${where}: id 缺失或含非法字符`)
      else if (ids.has(item.id)) errors.push(`${where}: id 重复，已出现在 ${ids.get(item.id)}`)
      else ids.set(item.id, where0)
      if (!item.name) errors.push(`${where}: 缺少 name`)
      if (!TIERS.includes(item.tier)) errors.push(`${where}: tier 只能是 A 或 B`)
      if (!page.subs.some((s) => s.key === item.sub)) errors.push(`${where}: sub「${item.sub}」不在页面 ${pageKey} 的子分类里`)
      for (const f of KINDS[page.kind]?.required ?? []) {
        if (item[f] == null || item[f] === '' || (Array.isArray(item[f]) && !item[f].length)) errors.push(`${where}: ${page.kind} 类条目必须填 ${f}`)
      }
      if (item.tier === 'A' && !item.why_zh) errors.push(`${where}: A 级条目必须写 why_zh`)
      if (item.why_zh && [...String(item.why_zh)].length > WHY_MAX) errors.push(`${where}: why_zh 超过 ${WHY_MAX} 字`)
      for (const f of ['url', 'publisher_url', 'free_url']) checkUrl(item[f], `${where} ${f}`, errors)
      if (item.repo && !/^[^/\s]+\/[^/\s]+$/.test(item.repo)) errors.push(`${where}: repo 必须写成 owner/name`)
      if (item.pricing && !PRICING.includes(item.pricing)) errors.push(`${where}: pricing 只能是 ${PRICING.join('/')}`)
      if (item.status && !STATUS.includes(item.status)) errors.push(`${where}: status 只能是 ${STATUS.join('/')}`)
      if (page.kind === 'community' && item.type && !COMMUNITY_TYPES.includes(item.type)) errors.push(`${where}: type 只能是 ${COMMUNITY_TYPES.join('/')}`)
      for (const s of item.sources) if (!sourceIds.has(s)) errors.push(`${where}: 来源 ${s} 不在 sources.yaml 里`)
      for (const f of ['added', 'reviewed']) if (item[f] != null && !DATE_RE.test(item[f])) errors.push(`${where}: ${f} 必须写成 YYYY-MM-DD`)
      if (!item.added) errors.push(`${where}: 缺少 added`)
      result.items.push(item)
    }
  }

  for (const p of result.pages) {
    const shown = result.items.filter((it) => it.page === p.key && it.reviewed)
    if (shown.length > 150) warnings.push(`页面 ${p.key} 有 ${shown.length} 条，超过 150 条上限，考虑拆页`)
    const b = shown.filter((it) => it.tier === 'B').length
    if (b > 40) warnings.push(`页面 ${p.key} 的 B 级有 ${b} 条，超过 40 条`)
  }
  for (const it of result.items) {
    if (it.repo && it.reviewed && !result.stats.repos[it.repo]) warnings.push(`${it.id}: stats.json 里没有 ${it.repo} 的数据，运行 npm run registry:stats 刷新`)
  }
  return result
}

// Only reviewed entries are published.
export const isPublished = (item) => Boolean(item.reviewed)

// 'archived' > 'stale' > 'active'. Manual status wins; otherwise derived from stats.
export function effectiveStatus(item, stats, now = new Date()) {
  if (item.status) return item.status
  const s = item.repo ? stats.repos[item.repo] : null
  if (!s) return 'active'
  if (s.archived) return 'archived'
  if (s.pushed_at) {
    const months = (now - new Date(s.pushed_at)) / (1000 * 60 * 60 * 24 * 30.44)
    if (months > STALE_MONTHS) return 'stale'
  }
  return 'active'
}

// Pages that have at least one published entry, in pages.yaml order.
export function publishedPages(registry) {
  return registry.pages.filter((p) => registry.items.some((it) => it.page === p.key && isPublished(it)))
}
