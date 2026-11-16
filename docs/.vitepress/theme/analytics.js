// Custom Umami events. The tracker itself is injected by config.ts only when a
// website ID is configured; without it window.umami never exists and every call
// here is a no-op (local dev, forks, ad-blocked visitors).
//
// Privacy rules: no search text, no free-form input, nothing about the visitor —
// only which site content or which external host was used.

const REPO = 'github.com/barca0412/introduction-to-quantitative-finance'
const MAX_VALUE = 120

function track(name, data) {
  try {
    if (typeof window !== 'undefined' && window.umami && typeof window.umami.track === 'function') {
      window.umami.track(name, data)
    }
  } catch {
    // Analytics must never break the page.
  }
}

const clip = (value) => String(value || '').slice(0, MAX_VALUE)

function fileName(url) {
  try {
    return clip(decodeURIComponent(url.pathname.split('/').pop() || ''))
  } catch {
    return clip(url.pathname.split('/').pop())
  }
}

// One event per click, picked by what the link points at.
export function classifyLink(href, origin) {
  let url
  try {
    url = new URL(href, origin)
  } catch {
    return null
  }
  if (!/^https?:$/.test(url.protocol)) return null
  const host = url.hostname.toLowerCase()
  const path = url.pathname.toLowerCase()
  const full = `${host}${path}`

  if (path.endsWith('.pdf')) return ['pdf-open', { file: fileName(url) }]
  if (host === 'huggingface.co' && path.startsWith('/datasets/')) return ['dataset-open', { target: 'huggingface' }]
  if (full.startsWith(`${REPO}/releases`)) return ['dataset-open', { target: 'github-release' }]
  if (full.startsWith(REPO)) {
    if (/\/tree\/[^/]+\/docs\/tutorials\/[^/]+\/code/.test(path)) return ['code-open', { lecture: clip(path.split('/docs/tutorials/')[1]?.split('/')[0]) }]
    // /owner/repo[/section/...] -> 'repo', 'blob', 'tree', 'stargazers', 'discussions', ...
    return ['github-click', { target: clip(path.split('/').filter(Boolean)[2] || 'repo') }]
  }
  if (url.origin !== origin) return ['outbound', { host: clip(host) }]
  return null
}

function onClick(event) {
  // Radar filters are toggle buttons (aria-pressed), not form fields.
  const toggle = event.target.closest?.('#radar-paper-filters button[aria-pressed]')
  if (toggle && !filteredThisPage) {
    filteredThisPage = true
    track('radar-filter')
    return
  }
  const link = event.target.closest?.('a[href]')
  if (!link) return
  const hit = classifyLink(link.getAttribute('href'), window.location.origin)
  if (hit) track(hit[0], hit[1])
}

// Radar: count that a search or filter happened, never what was typed.
let searchTimer
let searchedThisPage = false
function onInput(event) {
  const target = event.target
  if (!(target instanceof HTMLElement)) return
  if (target.id === 'radar-paper-query') {
    clearTimeout(searchTimer)
    searchTimer = setTimeout(() => {
      if (target.value.trim() && !searchedThisPage) {
        searchedThisPage = true
        track('radar-search')
      }
    }, 1500)
  }
}
let filteredThisPage = false

// Reading depth on lectures and knowledge-base pages, once per threshold per view.
const DEPTHS = [50, 90]
let reached = new Set()
let depthEnabled = false
let ticking = false
function measure() {
  ticking = false
  if (!depthEnabled) return
  const doc = document.documentElement
  const scrollable = doc.scrollHeight - window.innerHeight
  const ratio = scrollable <= 0 ? 1 : window.scrollY / scrollable
  for (const depth of DEPTHS) {
    if (ratio * 100 >= depth && !reached.has(depth)) {
      reached.add(depth)
      track(`read-${depth}`, { page: clip(window.location.pathname) })
    }
  }
}
function onScroll() {
  if (!ticking) {
    ticking = true
    window.requestAnimationFrame(measure)
  }
}

// Called on every route change (and once at start).
export function resetPage(path) {
  reached = new Set()
  searchedThisPage = false
  filteredThisPage = false
  depthEnabled = /\/(tutorials|wiki)\/./.test(path)
}

let installed = false
export function installAnalytics(router) {
  if (installed || typeof window === 'undefined') return
  installed = true
  document.addEventListener('click', onClick, { capture: true })
  document.addEventListener('input', onInput, { capture: true })
  window.addEventListener('scroll', onScroll, { passive: true })
  resetPage(window.location.pathname)
  const previous = router.onAfterRouteChanged
  router.onAfterRouteChanged = (to) => {
    resetPage(to)
    if (typeof previous === 'function') previous(to)
  }
}
