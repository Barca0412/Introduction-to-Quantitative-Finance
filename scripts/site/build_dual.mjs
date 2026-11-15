// Both deployments use one already-generated data snapshot.
import { spawnSync, execFileSync } from 'node:child_process'
import { mkdirSync, readFileSync, writeFileSync } from 'node:fs'
import { resolve, join } from 'node:path'
import { createHash } from 'node:crypto'
const output = resolve('.site-build')
mkdirSync(output, { recursive: true })
function run(command, args, env = {}) {
  const result = spawnSync(command, args, { stdio: 'inherit', env: { ...process.env, ...env } })
  if (result.error) throw result.error
  if (result.status !== 0) process.exit(result.status || 1)
}
run(process.execPath, ['scripts/site/prepare_site.mjs'])
run(process.execPath, ['scripts/site/prepare_search_model.mjs'])
const manifest = readFileSync('docs/public/arxiv-data/manifest.json')
const digest = createHash('sha256').update(manifest).digest('hex')
const siteUrl = process.env.SITE_URL || 'https://quant.hfthnu.com'
const builtAt = new Date().toISOString()
for (const [name, base] of [['server', '/'], ['pages', '/Introduction-to-Quantitative-Finance/']]) {
  const outDir = join(output, name)
  run('npm', ['run', 'docs:build', '--', '--outDir', outDir], { SITE_BASE: base, SITE_URL: siteUrl })
  const actual = createHash('sha256').update(readFileSync(join(outDir, 'arxiv-data/manifest.json'))).digest('hex')
  if (actual !== digest) throw new Error('Data changed between the two site builds')
  writeFileSync(join(outDir, 'build-info.json'), JSON.stringify({ commit: execFileSync('git', ['rev-parse', 'HEAD'], { encoding: 'utf8' }).trim(), built_at: builtAt, manifest_sha256: digest, latest_published_date: JSON.parse(manifest).latest_published_date, site_url: siteUrl, base }) + '\n')
  run(process.execPath, ['scripts/site/check_build.mjs', outDir])
  run(process.env.SITE_PYTHON || 'python3', ['scripts/site/check_links.py', outDir, '--base', base])
}
console.log(`Both site builds use manifest SHA256 ${digest}`)
