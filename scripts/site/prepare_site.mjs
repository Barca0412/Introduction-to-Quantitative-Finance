// Public GitHub metadata only; no credential is required or written.
import { mkdirSync, readFileSync, writeFileSync } from 'node:fs'
import { fileURLToPath } from 'node:url'
const dir = fileURLToPath(new URL('../../.site-build/', import.meta.url))
const file = `${dir}github.json`
let previous
try { previous = JSON.parse(readFileSync(file, 'utf8')) } catch {}
if (previous && previous.stars !== null && Date.now() - previous.fetched_at < 600000) process.exit(0)
let stars = null
// Anonymous GitHub API calls share a small per-IP limit with everyone on the same CI runner,
// so some builds were refused and the badge went blank. In CI the workflow's own read-only
// token is passed in (GITHUB_TOKEN); it is only sent to api.github.com and never written out.
const headers = { Accept: 'application/vnd.github+json' }
if (process.env.GITHUB_TOKEN) headers.Authorization = `Bearer ${process.env.GITHUB_TOKEN}`
for (let attempt = 1; attempt <= 3 && stars === null; attempt++) {
  try {
    const response = await fetch('https://api.github.com/repos/Barca0412/Introduction-to-Quantitative-Finance', { signal: AbortSignal.timeout(8000), headers })
    if (response.ok) { const data = await response.json(); if (Number.isInteger(data.stargazers_count)) stars = data.stargazers_count }
    else {
      console.log(`GitHub Star lookup attempt ${attempt}: HTTP ${response.status}`)
      if (response.status === 401) delete headers.Authorization
    }
  } catch (error) { console.log(`GitHub Star lookup attempt ${attempt}: ${error.name}`) }
  if (stars === null && attempt < 3) await new Promise(resolve => setTimeout(resolve, 2000 * attempt))
}
mkdirSync(dir, { recursive: true })
writeFileSync(file, JSON.stringify({ stars, fetched_at: Date.now() }))
console.log(stars === null ? 'GitHub Star count unavailable; hiding the count.' : `GitHub Star count: ${stars}`)
