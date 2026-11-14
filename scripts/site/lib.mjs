// Shared helpers for the site generators (gen_library.mjs, gen_resources.mjs).
import { readdirSync, statSync, existsSync, readFileSync } from 'node:fs'
import { join, relative, sep } from 'node:path'
import { fileURLToPath } from 'node:url'
import { parse as parseYaml } from 'yaml'

export const ROOT = join(fileURLToPath(new URL('.', import.meta.url)), '..', '..')
export const REPO = process.env.GITHUB_REPOSITORY || 'Barca0412/Introduction-to-Quantitative-Finance'
export const BRANCH = process.env.LIBRARY_BRANCH || 'main'

export const collator = new Intl.Collator('zh-CN', { numeric: true })

export function walk(dir) {
  if (!existsSync(dir)) return []
  return readdirSync(dir).flatMap((name) => {
    if (name.startsWith('.')) return []
    const full = join(dir, name)
    return statSync(full).isDirectory() ? walk(full) : [full]
  })
}

export const repoPath = (full) => relative(ROOT, full).split(sep)

export const githubUrl = (kind, parts) =>
  `https://github.com/${REPO}/${kind}/${BRANCH}/${parts.map(encodeURIComponent).join('/')}`

// Markdown text must not break table/list/link syntax.
export const escapeText = (text) => String(text ?? '').replace(/([\\[\]|*_`<>])/g, '\\$1')

// Same slug rule as VitePress' default markdown-it anchor for CJK headings.
export function anchor(text) {
  return String(text)
    .normalize('NFKD')
    .replace(/[̀-ͯ]/g, '')
    .replace(/[\u0000-\u001f]/g, '')
    .replace(/[\s~`!@#$%^&*()\-_+=[\]{}|\\;:"'“”‘’<>,.?/]+/g, '-')
    .replace(/-{2,}/g, '-')
    .replace(/^-+|-+$/g, '')
    .replace(/^(\d)/, '_$1')
    .toLowerCase()
}

export function readYaml(file) {
  return parseYaml(readFileSync(file, 'utf8')) ?? {}
}

// Replace the text between `<!-- NAME:START -->` and `<!-- NAME:END -->`.
// Returns null when the markers are missing, so callers can decide what to do.
export function replaceBlock(text, name, inner) {
  const start = `<!-- ${name}:START -->`
  const end = `<!-- ${name}:END -->`
  const i = text.indexOf(start)
  const j = text.indexOf(end)
  if (i === -1 || j === -1 || j < i) return null
  return `${text.slice(0, i + start.length)}\n${inner.trim()}\n${text.slice(j)}`
}
