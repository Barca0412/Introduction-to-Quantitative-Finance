// Generates the resource pages from the registry in data/registry/.
//
//   node scripts/site/gen_resources.mjs            validate, then write pages
//   node scripts/site/gen_resources.mjs --check    validate only (CI / tests)
//   node scripts/site/gen_resources.mjs --readme   also rewrite the README block
//   node scripts/site/gen_resources.mjs --urls     print every URL (drafts included) for link checking
//
// Output (git-ignored): docs/resources/<page>.md for every page with published
// entries, plus docs/resources/credits.md. Only entries with `reviewed` set are
// published. Any validation error exits with code 1, so a bad registry fails the build.
//
// Overrides for tests: REGISTRY_DIR, RESOURCES_OUT_DIR, README_FILE.
import { writeFileSync, mkdirSync, readFileSync, existsSync } from 'node:fs'
import { join } from 'node:path'
import { execFileSync } from 'node:child_process'
import { ROOT, escapeText, anchor, replaceBlock } from './lib.mjs'
import { DEFAULT_DIR, loadRegistry, isPublished, effectiveStatus, publishedPages } from './registry.mjs'

const args = new Set(process.argv.slice(2))
const REGISTRY_DIR = process.env.REGISTRY_DIR || DEFAULT_DIR
const OUT_DIR = process.env.RESOURCES_OUT_DIR || join(ROOT, 'docs', 'resources')
const README_FILE = process.env.README_FILE || join(ROOT, 'README.md')
const SITE = 'https://barca0412.github.io/Introduction-to-Quantitative-Finance'
const README_BLOCK = 'RESOURCES'

const registry = loadRegistry(REGISTRY_DIR)
for (const w of registry.warnings) console.warn(`registry warning: ${w}`)
if (registry.errors.length) {
  console.error(`registry: ${registry.errors.length} 个错误，构建中止：`)
  for (const e of registry.errors) console.error(`  - ${e}`)
  process.exit(1)
}

if (args.has('--urls')) {
  const urls = new Set()
  for (const s of registry.sources) urls.add(s.url)
  for (const it of registry.items) for (const f of ['url', 'publisher_url', 'free_url']) if (it[f]) urls.add(it[f])
  process.stdout.write([...urls].filter(Boolean).sort().join('\n') + '\n')
  process.exit(0)
}

const published = registry.items.filter(isPublished)
const pages = publishedPages(registry)
console.log(`registry: ${registry.items.length} 条（已审 ${published.length}，待审 ${registry.items.length - published.length}），${pages.length} 个页面有内容`)
if (args.has('--check')) process.exit(0)

// ---------- rendering ----------

const STATUS_LABEL = { active: '', stale: '已停更', archived: '已归档' }
const PRICING_LABEL = { free: '免费', freemium: '部分免费', paid: '收费' }
const fmtStars = (n) => (n == null ? '' : n >= 1000 ? `${(n / 1000).toFixed(n >= 10000 ? 0 : 1)}k` : String(n))
const link = (text, url) => (url ? `[${escapeText(text)}](${url})` : escapeText(text))
const cell = (text) => escapeText(text).replace(/\n/g, ' ')
const sourceById = new Map(registry.sources.map((s) => [s.id, s]))

function badges(item) {
  const out = []
  const st = STATUS_LABEL[effectiveStatus(item, registry.stats)]
  if (st) out.push(`<Badge type="warning" text="${st}" />`)
  if (item.pricing && item.pricing !== 'free') out.push(`<Badge type="info" text="${PRICING_LABEL[item.pricing]}" />`)
  if (item.lang === 'en') out.push('<Badge type="tip" text="英文" />')
  return out.join(' ')
}

function nameCell(item) {
  const b = badges(item)
  return `${link(item.name, item.url || item.publisher_url)}${b ? ` ${b}` : ''}`
}

function row(item, kind) {
  const stats = item.repo ? registry.stats.repos[item.repo] : null
  switch (kind) {
    case 'book':
      return [
        nameCell(item),
        cell([].concat(item.authors).join('、')),
        item.year ?? '',
        cell(item.why_zh ?? ''),
        item.free_url ? `[免费版](${item.free_url})` : '',
      ]
    case 'course':
      return [nameCell(item), cell(item.provider), cell(item.why_zh ?? ''), item.free === false ? '收费' : '免费']
    case 'community':
      return [nameCell(item), cell(item.why_zh ?? '')]
    default:
      return [nameCell(item), cell(item.why_zh ?? ''), fmtStars(stats?.stars)]
  }
}

const HEADERS = {
  book: ['书', '作者', '年份', '推荐理由', '免费版'],
  course: ['课程', '提供方', '推荐理由', '费用'],
  community: ['名称', '推荐理由'],
  project: ['项目', '推荐理由', '★'],
  data: ['数据源', '推荐理由', '★'],
}

function table(items, kind) {
  const head = HEADERS[kind]
  return [
    `| ${head.join(' | ')} |`,
    `| ${head.map(() => '---').join(' | ')} |`,
    ...items.map((it) => `| ${row(it, kind).join(' | ')} |`),
  ].join('\n')
}

const byOrder = (a, b) => (b.pick === true) - (a.pick === true) || String(a.name).localeCompare(String(b.name), 'zh-CN')

// Commit time of the newest change to this page's data file, for "最后更新" and sitemap <lastmod>.
function dataLastUpdated(pageKey) {
  try {
    const out = execFileSync('git', ['log', '-1', '--format=%cI', '--', join(REGISTRY_DIR, 'items', `${pageKey}.yaml`)], { cwd: ROOT, encoding: 'utf8' }).trim()
    return out || null
  } catch {
    return null
  }
}

function renderPage(page) {
  const items = published.filter((it) => it.page === page.key)
  const lines = []
  const updated = dataLastUpdated(page.key)
  lines.push('---', `title: ${page.title}`, `description: ${page.description}`)
  if (updated) lines.push(`lastUpdated: ${updated}`)
  lines.push('---', '', '<!-- Generated by scripts/site/gen_resources.mjs from data/registry/. Edit the YAML, not this file. -->', '')
  lines.push(`# ${page.title}`, '')
  if (page.intro) lines.push(page.intro.trim(), '')
  lines.push(`本页收录 ${items.length} 项，每一项都经过人工审核；推荐理由由本项目自己撰写。条目的来源见[致谢](/resources/credits)。`, '')
  const subs = page.subs.filter((s) => items.some((it) => it.sub === s.key))
  if (subs.length > 1) {
    lines.push(subs.map((s) => `[${s.title}](#${anchor(s.title)})`).join(' · '), '')
  }
  for (const sub of subs) {
    const inSub = items.filter((it) => it.sub === sub.key)
    const a = inSub.filter((it) => it.tier === 'A').sort(byOrder)
    const b = inSub.filter((it) => it.tier === 'B').sort(byOrder)
    lines.push(`## ${sub.title}`, '')
    if (sub.intro) lines.push(sub.intro.trim(), '')
    if (a.length) lines.push(table(a, page.kind), '')
    if (b.length) {
      lines.push(`**更多同类**`, '')
      for (const it of b) lines.push(`- ${nameCell(it)}${it.why_zh ? `：${cell(it.why_zh)}` : ''}`)
      lines.push('')
    }
  }
  return lines.join('\n')
}

function renderCredits() {
  const counts = new Map()
  for (const it of published) for (const s of it.sources) counts.set(s, (counts.get(s) ?? 0) + 1)
  const USE = { 'link-only': '只引用名称和链接，说明文字由本项目自写', 'adapt-with-credit': '可改编，已署名' }
  const rows = registry.sources
    .filter((s) => counts.get(s.id))
    .sort((x, y) => counts.get(y.id) - counts.get(x.id))
    .map((s) => `| ${link(s.name, s.url)} | ${cell(s.license)} | ${USE[s.use]} | ${counts.get(s.id)} |`)
  return [
    '---',
    'title: 资源致谢与来源',
    'description: 资源清单参考了哪些中英文资源整合仓库和站点，各自的许可证，以及本项目如何使用它们。',
    '---',
    '',
    '<!-- Generated by scripts/site/gen_resources.mjs from data/registry/. -->',
    '',
    '# 资源致谢与来源',
    '',
    '资源清单在整理时参考了下面这些清单和站点。我们只沿用条目的名称和链接这类事实信息；每条的推荐理由都由本项目重新撰写，不翻译或照搬原文。想看更完整的清单，请直接访问这些来源。',
    '',
    '| 来源 | 许可证 | 使用方式 | 参考条目数 |',
    '| --- | --- | --- | --- |',
    ...rows,
    '',
    '本项目自写的资源点评按 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/deed.zh-hans) 授权，代码按 MIT 授权，详见[关于](/about#授权)。',
    '',
  ].join('\n')
}

function renderReadmeBlock() {
  const picks = published.filter((it) => it.pick)
  const lines = []
  for (const page of pages) {
    const ps = picks.filter((it) => it.page === page.key).sort(byOrder)
    if (!ps.length) continue
    lines.push(`**[${page.title}](${SITE}/resources/${page.key})**`, '')
    for (const it of ps) lines.push(`- ${link(it.name, it.url || it.publisher_url)}${it.why_zh ? ` - ${cell(it.why_zh)}` : ''}`)
    lines.push('')
  }
  lines.push('| 分类 | 条目数 |', '| --- | --- |')
  for (const page of pages) lines.push(`| [${page.title}](${SITE}/resources/${page.key}) | ${published.filter((it) => it.page === page.key).length} |`)
  lines.push('', `完整清单与推荐理由见[资源页](${SITE}/resources/)。`)
  return `<!-- Generated by scripts/site/gen_resources.mjs; edit data/registry/ instead. -->\n${lines.join('\n')}`
}

mkdirSync(OUT_DIR, { recursive: true })
for (const page of pages) writeFileSync(join(OUT_DIR, `${page.key}.md`), renderPage(page))
if (pages.length) writeFileSync(join(OUT_DIR, 'credits.md'), renderCredits())
console.log(`resources: ${pages.map((p) => p.key).join(', ') || '（还没有已审页面）'} -> ${OUT_DIR}`)

if (args.has('--readme')) {
  if (!existsSync(README_FILE)) {
    console.warn(`readme: 找不到 ${README_FILE}，跳过`)
  } else if (!pages.length) {
    console.log('readme: 还没有已审条目，README 保持不变')
  } else {
    const next = replaceBlock(readFileSync(README_FILE, 'utf8'), README_BLOCK, renderReadmeBlock())
    if (next == null) console.warn(`readme: README 里没有 <!-- ${README_BLOCK}:START/END --> 标记，跳过`)
    else writeFileSync(README_FILE, next)
  }
}
