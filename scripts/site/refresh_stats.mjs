// Refreshes data/registry/stats.json with GitHub stars, last push and archive state
// for every `repo:` in the registry. Machine-written; never edit stats.json by hand.
//
//   GITHUB_TOKEN=... node scripts/site/refresh_stats.mjs
//
// Falls back to `gh auth token` when GITHUB_TOKEN is unset. Repos that were renamed
// are reported (the registry should be updated to the new owner/name by a person).
import { writeFileSync } from 'node:fs'
import { join } from 'node:path'
import { execFileSync } from 'node:child_process'
import { DEFAULT_DIR, loadRegistry } from './registry.mjs'

const dir = process.env.REGISTRY_DIR || DEFAULT_DIR
const registry = loadRegistry(dir)
const repos = [...new Set(registry.items.map((it) => it.repo).filter(Boolean))].sort()

let token = process.env.GITHUB_TOKEN
if (!token) {
  try {
    token = execFileSync('gh', ['auth', 'token'], { encoding: 'utf8' }).trim()
  } catch {
    console.error('需要 GITHUB_TOKEN，或先登录 gh')
    process.exit(1)
  }
}

async function query(batch) {
  const fields = batch
    .map(([owner, name], i) => `r${i}: repository(owner: ${JSON.stringify(owner)}, name: ${JSON.stringify(name)}) { nameWithOwner stargazerCount pushedAt isArchived url }`)
    .join('\n')
  const res = await fetch('https://api.github.com/graphql', {
    method: 'POST',
    headers: { Authorization: `Bearer ${token}`, 'Content-Type': 'application/json', 'User-Agent': 'iqf-registry' },
    body: JSON.stringify({ query: `query {\n${fields}\n}` }),
  })
  if (!res.ok) throw new Error(`GitHub GraphQL ${res.status}: ${await res.text()}`)
  // Missing repos come back as null data plus an error entry; both are fine.
  return (await res.json()).data ?? {}
}

const out = { generated_at: new Date().toISOString(), repos: {} }
const missing = []
const renamed = []
for (let i = 0; i < repos.length; i += 100) {
  const batch = repos.slice(i, i + 100).map((r) => r.split('/'))
  const data = await query(batch)
  batch.forEach(([owner, name], k) => {
    const key = `${owner}/${name}`
    const r = data[`r${k}`]
    if (!r) { missing.push(key); return }
    if (r.nameWithOwner.toLowerCase() !== key.toLowerCase()) renamed.push(`${key} -> ${r.nameWithOwner}`)
    out.repos[key] = { stars: r.stargazerCount, pushed_at: r.pushedAt, archived: r.isArchived, url: r.url, name_with_owner: r.nameWithOwner }
  })
}

writeFileSync(join(dir, 'stats.json'), JSON.stringify(out, null, 2) + '\n')
console.log(`stats: ${Object.keys(out.repos).length}/${repos.length} repos updated`)
if (renamed.length) console.log(`renamed (update the registry):\n  ${renamed.join('\n  ')}`)
if (missing.length) {
  console.log(`not found (deleted or private):\n  ${missing.join('\n  ')}`)
  process.exitCode = 2
}
