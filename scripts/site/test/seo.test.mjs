import test from 'node:test'
import assert from 'node:assert/strict'
import { mkdtempSync, readFileSync, rmSync } from 'node:fs'
import { tmpdir } from 'node:os'
import { join } from 'node:path'
import { siteBase, siteOrigin, redirectPage, writeSeoFiles } from '../seo.mjs'
import { METHOD_ROUTES, LEGACY_ROUTES } from '../routes.mjs'

test('mirror resources use its own base while canonical stays at the main origin', () => {
  for (const base of ['/', '/Introduction-to-Quantitative-Finance/']) {
    const html = redirectPage('resources/method-factors', base, 'https://quant.hfthnu.com')
    assert.ok(html.includes('href="https://quant.hfthnu.com/resources/method-factors"'))
    assert.ok(html.includes(`location.replace("${base}resources/method-factors" + location.search + location.hash)`))
  }
})
test('every former wiki and older route redirects directly to a resource destination', () => {
  assert.equal(Object.keys(METHOD_ROUTES).length, 11)
  assert.ok(Object.values(LEGACY_ROUTES).every(path => path.startsWith('resources/')))
  const root = mkdtempSync(join(tmpdir(), 'quant-seo-'))
  try {
    writeSeoFiles(root, '/mirror/', 'https://quant.hfthnu.com')
    assert.match(readFileSync(join(root, 'wiki/factors/index.html'), 'utf8'), /\/mirror\/resources\/method-factors/)
    assert.match(readFileSync(join(root, 'robots.txt'), 'utf8'), /https:\/\/quant.hfthnu.com\/sitemap.xml/)
    assert.doesNotMatch(readFileSync(join(root, 'llms.txt'), 'utf8'), /项目式|免费数据|barca0412.github.io/)
  } finally { rmSync(root, { recursive: true }) }
})
test('deployment origin and asset base cannot be accidentally conflated', () => {
  assert.equal(siteBase(), '/Introduction-to-Quantitative-Finance/')
  assert.equal(siteOrigin(), 'https://quant.hfthnu.com')
  assert.throws(() => siteOrigin('https://quant.hfthnu.com/mirror/'))
  assert.throws(() => siteBase('https://quant.hfthnu.com/'))
})
