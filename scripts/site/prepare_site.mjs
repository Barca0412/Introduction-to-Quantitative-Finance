// Public GitHub metadata only; no credential is required or written.
import { mkdirSync, readFileSync, writeFileSync } from 'node:fs'
import { fileURLToPath } from 'node:url'
const dir = fileURLToPath(new URL('../../.site-build/', import.meta.url))
const file = `${dir}github.json`
let previous
try { previous = JSON.parse(readFileSync(file, 'utf8')) } catch {}
if (previous && previous.stars !== null && Date.now() - previous.fetched_at < 600000) process.exit(0)
let stars = null
try {
  const response = await fetch('https://api.github.com/repos/Barca0412/Introduction-to-Quantitative-Finance', { signal: AbortSignal.timeout(8000), headers: { Accept: 'application/vnd.github+json' } })
  if (response.ok) { const data = await response.json(); if (Number.isInteger(data.stargazers_count)) stars = data.stargazers_count }
} catch { /* Optional badge: a failed lookup hides the number. */ }
mkdirSync(dir, { recursive: true })
writeFileSync(file, JSON.stringify({ stars, fetched_at: Date.now() }))
console.log(stars === null ? 'GitHub Star count unavailable; hiding the count.' : `GitHub Star count: ${stars}`)
