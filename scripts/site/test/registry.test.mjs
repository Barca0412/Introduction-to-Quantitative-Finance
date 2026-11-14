// Tests for the resource registry generator. Run with `npm run test:site`.
// Each case writes a small registry into a temp dir and runs gen_resources.mjs on it.
import { test } from 'node:test'
import assert from 'node:assert/strict'
import { mkdtempSync, mkdirSync, writeFileSync, readFileSync, existsSync } from 'node:fs'
import { tmpdir } from 'node:os'
import { join } from 'node:path'
import { spawnSync } from 'node:child_process'
import { fileURLToPath } from 'node:url'

const SCRIPT = fileURLToPath(new URL('../gen_resources.mjs', import.meta.url))

const PAGES = `pages:
  - key: backtest
    kind: project
    title: 回测与研究框架
    description: 测试页面
    subs:
      - { key: vectorized, title: 向量化与轻量回测 }
      - { key: event-driven, title: 事件驱动与实盘一体 }
  - key: books
    kind: book
    title: 量化书单
    description: 测试书单
    subs:
      - { key: math, title: 数学 }
`
const SOURCES = `sources:
  - { id: list-a, name: owner/list-a, url: https://github.com/owner/list-a, license: MIT, use: adapt-with-credit }
`
const GOOD_ITEMS = `items:
  - id: kernc/backtesting.py
    name: backtesting.py
    url: https://github.com/kernc/backtesting.py
    repo: kernc/backtesting.py
    sub: vectorized
    tier: A
    why_zh: 轻量的单资产回测库，接口简单，适合入门快速验证想法。
    pick: true
    sources: [list-a]
    added: 2026-11-16
    reviewed: 2026-11-16
  - id: old/stale-engine
    name: Stale Engine
    url: https://github.com/old/stale-engine
    repo: old/stale-engine
    sub: event-driven
    tier: B
    sources: []
    added: 2026-11-16
    reviewed: 2026-11-16
  - id: draft/not-reviewed
    name: Draft Only
    url: https://github.com/draft/not-reviewed
    sub: vectorized
    tier: A
    why_zh: 这条还没审核，不应该出现在页面上。
    sources: []
    added: 2026-11-16
`
const STATS = JSON.stringify({
  generated_at: '2026-11-16T00:00:00Z',
  repos: {
    'kernc/backtesting.py': { stars: 7900, pushed_at: '2026-10-01T00:00:00Z', archived: false },
    'old/stale-engine': { stars: 900, pushed_at: '2020-01-01T00:00:00Z', archived: false },
  },
})

function makeRegistry({ items = GOOD_ITEMS, books = null, pages = PAGES, sources = SOURCES } = {}) {
  const dir = mkdtempSync(join(tmpdir(), 'registry-'))
  mkdirSync(join(dir, 'items'))
  writeFileSync(join(dir, 'pages.yaml'), pages)
  writeFileSync(join(dir, 'sources.yaml'), sources)
  writeFileSync(join(dir, 'stats.json'), STATS)
  writeFileSync(join(dir, 'items', 'backtest.yaml'), items)
  if (books) writeFileSync(join(dir, 'items', 'books.yaml'), books)
  return dir
}

function run(dir, args = [], extraEnv = {}) {
  const out = join(dir, 'out')
  const res = spawnSync(process.execPath, [SCRIPT, ...args], {
    env: { ...process.env, REGISTRY_DIR: dir, RESOURCES_OUT_DIR: out, ...extraEnv },
    encoding: 'utf8',
  })
  return { ...res, out }
}

test('valid registry renders reviewed entries only', () => {
  const dir = makeRegistry()
  const res = run(dir)
  assert.equal(res.status, 0, res.stderr)
  const page = readFileSync(join(res.out, 'backtest.md'), 'utf8')
  assert.match(page, /backtesting\.py/)
  assert.match(page, /7\.9k/)
  assert.doesNotMatch(page, /Draft Only/)
  assert.match(page, /已停更/) // derived from stats: no push since 2020
  assert.match(page, /更多同类/) // the B-tier entry
  assert.ok(existsSync(join(res.out, 'credits.md')))
  assert.ok(!existsSync(join(res.out, 'books.md')), 'pages without reviewed entries are not generated')
})

test('--urls lists drafts too', () => {
  const res = run(makeRegistry(), ['--urls'])
  assert.equal(res.status, 0, res.stderr)
  assert.match(res.stdout, /draft\/not-reviewed/)
})

test('--readme rewrites only the marked block', () => {
  const dir = makeRegistry()
  const readme = join(dir, 'README.md')
  writeFileSync(readme, 'before\n<!-- RESOURCES:START -->\nold\n<!-- RESOURCES:END -->\nafter\n')
  const res = run(dir, ['--readme'], { README_FILE: readme })
  assert.equal(res.status, 0, res.stderr)
  const text = readFileSync(readme, 'utf8')
  assert.match(text, /^before\n<!-- RESOURCES:START -->/)
  assert.match(text, /backtesting\.py/)
  assert.doesNotMatch(text, /\nold\n/)
  assert.match(text, /<!-- RESOURCES:END -->\nafter\n$/)
})

const BAD_CASES = {
  'duplicate id': [GOOD_ITEMS + `  - { id: kernc/backtesting.py, name: dup, url: https://example.com, sub: vectorized, tier: B, sources: [], added: 2026-11-16 }\n`, /id 重复/],
  'unknown sub': [`items:\n  - { id: x/y, name: y, url: https://example.com, sub: nope, tier: B, sources: [], added: 2026-11-16 }\n`, /不在页面 backtest 的子分类里/],
  'unknown source': [`items:\n  - { id: x/y, name: y, url: https://example.com, sub: vectorized, tier: B, sources: [ghost], added: 2026-11-16 }\n`, /来源 ghost 不在 sources\.yaml 里/],
  'A without why_zh': [`items:\n  - { id: x/y, name: y, url: https://example.com, sub: vectorized, tier: A, sources: [], added: 2026-11-16 }\n`, /A 级条目必须写 why_zh/],
  'why_zh too long': [`items:\n  - { id: x/y, name: y, url: https://example.com, sub: vectorized, tier: A, why_zh: "${'很'.repeat(61)}", sources: [], added: 2026-11-16 }\n`, /why_zh 超过 60 字/],
  'pirate domain': [`items:\n  - { id: x/y, name: y, url: https://oceanofpdf.com/some-book, sub: vectorized, tier: B, sources: [], added: 2026-11-16 }\n`, /盗版/],
  'bad tier': [`items:\n  - { id: x/y, name: y, url: https://example.com, sub: vectorized, tier: C, sources: [], added: 2026-11-16 }\n`, /tier 只能是 A 或 B/],
  'bad date': [`items:\n  - { id: x/y, name: y, url: https://example.com, sub: vectorized, tier: B, sources: [], added: 2026-11-16, reviewed: yesterday }\n`, /reviewed 必须写成 YYYY-MM-DD/],
  'not a url': [`items:\n  - { id: x/y, name: y, url: ftp://example.com, sub: vectorized, tier: B, sources: [], added: 2026-11-16 }\n`, /不是有效的 http\(s\) 链接/],
}

for (const [name, [items, pattern]] of Object.entries(BAD_CASES)) {
  test(`fails the build: ${name}`, () => {
    const res = run(makeRegistry({ items }), ['--check'])
    assert.equal(res.status, 1, `expected failure, got:\n${res.stdout}\n${res.stderr}`)
    assert.match(res.stderr, pattern)
  })
}

test('book entries need authors and render a book table', () => {
  const books = `items:\n  - { id: islr, name: An Introduction to Statistical Learning, publisher_url: https://www.statlearning.com/, free_url: https://www.statlearning.com/, authors: [James, Witten, Hastie, Tibshirani], year: 2021, sub: math, tier: A, why_zh: 统计学习的入门教材，作者官网提供免费电子版。, sources: [], added: 2026-11-16, reviewed: 2026-11-16 }\n`
  const ok = run(makeRegistry({ books }))
  assert.equal(ok.status, 0, ok.stderr)
  const page = readFileSync(join(ok.out, 'books.md'), 'utf8')
  assert.match(page, /\| 书 \| 作者 \| 年份 \| 推荐理由 \| 免费版 \|/)
  assert.match(page, /\[免费版\]/)
  const bad = run(makeRegistry({ books: books.replace('authors: [James, Witten, Hastie, Tibshirani], ', '') }), ['--check'])
  assert.equal(bad.status, 1)
  assert.match(bad.stderr, /book 类条目必须填 authors/)
})
