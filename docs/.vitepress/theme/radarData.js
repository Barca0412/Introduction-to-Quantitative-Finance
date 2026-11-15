// Client-side loader for the light-weight Radar data in /arxiv-data/.
// Layout and record schema are produced by scripts/arxiv_radar/build_site_data.py.
import { withBase } from 'vitepress'

const FOCUS_LABELS = {
  'ai-finance': 'AI + Finance',
  'agent-planning': 'Agent Planning',
  'deep-research': 'Deep Research',
}

let manifestPromise = null
const jsonCache = new Map()
const groupPapersCache = new Map()
const vectorCache = new Map()

const dataUrl = (file, version) => {
  const url = withBase(`/arxiv-data/${file}`)
  return version ? `${url}?v=${encodeURIComponent(version)}` : url
}

async function fetchJson(file, version) {
  const key = `${file}?${version || ''}`
  if (!jsonCache.has(key)) {
    jsonCache.set(key, fetch(dataUrl(file, version)).then((response) => {
      if (!response.ok) {
        const error = new Error(`Failed to load ${file} (${response.status})`)
        error.status = response.status
        throw error
      }
      return response.json()
    }).catch((error) => {
      jsonCache.delete(key)
      throw error
    }))
  }
  return jsonCache.get(key)
}

export function loadManifest() {
  if (!manifestPromise) {
    // The manifest itself is tiny; a timestamp keeps it fresh behind the Pages CDN cache.
    manifestPromise = fetch(`${dataUrl('manifest.json')}?t=${Math.floor(Date.now() / 600000)}`)
      .then((response) => {
        if (!response.ok) throw new Error(`Radar manifest is not available (${response.status})`)
        return response.json()
      })
      .catch((error) => {
        manifestPromise = null
        throw error
      })
  }
  return manifestPromise
}

export async function loadStats() {
  const manifest = await loadManifest()
  return fetchJson('stats.json', manifest.generated_at)
}

function groupInfo(manifest, groupKey) {
  if (groupKey === 'recent') return manifest.recent
  const month = groupKey.replace(/^archive\//, '')
  const info = manifest.archive.find((item) => item.month === month)
  if (!info) throw new Error(`Unknown Radar month: ${month}`)
  return info
}

export function hydratePaper(record, groupKey) {
  const focus = record.fo || {}
  const topics = focus.t || []
  const affiliations = record.f || []
  return {
    id: record.id,
    title: record.t || '',
    authors: (record.a || []).map((name) => ({ name })),
    author_count: record.an || (record.a || []).length,
    categories: record.c || [],
    published_date: record.d || '',
    tags: record.g || [],
    keywords: record.k || [],
    summary_zh: record.z || '',
    affiliations,
    affiliation: affiliations.join('; '),
    group: groupKey,
    // S3 v2 enrichment and P2 fields (ids are named in taxonomy.json, see loadTaxonomy).
    relevance: record.r ?? null,
    is_core: record.r === 3,
    paper_type: record.pt || '',
    task_types: record.tt || [],
    finance_domains: record.fd || [],
    methods: record.m || [],
    data_market: record.dm || [],
    tldr_zh: record.tl || '',
    keywords_std: (record.kn || []).map(([id, label, kind]) => ({ id, label, kind: kind === 'f' ? 'finance' : 'tech' })),
    // official: confirmed by the venue's accepted-paper list; note: its track or decision.
    venue: record.v
      ? { name: record.v.n, kind: record.v.k || '', status: record.v.s || '', year: record.v.y || null,
          official: record.v.o === 1, note: record.v.t || '' }
      : null,
    venue_mention: record.vm || '',
    discipline: record.ds || '',
    has_code: record.cd === 1,
    detail_chunk: record.dc,
    detail: null,
    is_arxiv: record.ar === 1,
    abs_link: record.u || '',
    pdf_link: record.p || '',
    focus: {
      score: focus.s || 0,
      is_focus: Boolean(focus.f),
      primary_topic: focus.p || null,
      topics,
      labels: topics.map((topic) => FOCUS_LABELS[topic]).filter(Boolean),
      reasons: focus.r || [],
    },
  }
}

export async function loadGroupPapers(groupKey) {
  if (!groupPapersCache.has(groupKey)) {
    groupPapersCache.set(groupKey, (async () => {
      const manifest = await loadManifest()
      const info = groupInfo(manifest, groupKey)
      const parts = await Promise.all(info.papers.map((part) => fetchJson(part.file, manifest.generated_at)))
      return parts.flatMap((part) => part.papers.map((record) => hydratePaper(record, groupKey)))
    })().catch((error) => {
      groupPapersCache.delete(groupKey)
      throw error
    }))
  }
  return groupPapersCache.get(groupKey)
}

/** Load history only when the selected range needs it. */
export async function loadAllPapers() {
  const manifest = await loadManifest()
  const groups = ['recent', ...manifest.archive.map((item) => `archive/${item.month}`)]
  return (await Promise.all(groups.map(loadGroupPapers))).flat()
    .sort((a, b) => b.published_date.localeCompare(a.published_date) || b.id.localeCompare(a.id))
}

/** Resolve explicit paper IDs without guessing their date from their identifier. */
export async function loadPapersByIds(ids) {
  const manifest = await loadManifest()
  const index = manifest.paper_index
    ? await fetchJson(manifest.paper_index.file, manifest.generated_at) : null
  const papers = index
    ? (await Promise.all([...new Set(ids.map((id) => index[id]).filter(Boolean))].map(loadGroupPapers))).flat()
    : await loadAllPapers()
  const byId = new Map(papers.map((paper) => [paper.id, paper]))
  return ids.map((id) => byId.get(id)).filter(Boolean)
}

/**
 * S8 trend aggregates written by scripts/arxiv_radar/trends.py into /arxiv-data/agg/:
 * 'weekly_keywords', 'weekly_institutions', 'rising', `topic/<domain or method id>`,
 * `keyword/<id>`. Returns null when the site data has no aggregates or the file is missing.
 * rising.enough_history is false until four earlier weeks exist: say so on the page.
 */
export async function loadAggregate(name) {
  if (!/^[a-zA-Z0-9_-]+(?:\/[a-zA-Z0-9_-]+)?$/.test(name)) throw new Error('Invalid aggregate name')
  const manifest = await loadManifest()
  if (!manifest.agg) return null
  try {
    return await fetchJson(`agg/${name}.json`, manifest.generated_at)
  } catch (error) {
    if (error.status === 404) return null
    throw error
  }
}

/** Chinese names of the classification ids: { paper_types: Map(id -> zh), ..., relevance }. */
export async function loadTaxonomy() {
  const manifest = await loadManifest()
  if (!manifest.taxonomy) return null
  const raw = await fetchJson(manifest.taxonomy.file, manifest.generated_at)
  const out = { relevance: raw.relevance || {}, order: {} }
  for (const key of ['paper_types', 'task_types', 'finance_domains', 'methods', 'data_markets']) {
    out[key] = new Map((raw[key] || []).map((item) => [item.id, item.zh]))
    out.order[key] = (raw[key] || []).map((item) => item.id)
  }
  return out
}

/**
 * Key points, relevance reason and institutions for one paper (mutates and returns it).
 * paper.detail = { points: {problem, method, result, limitation}, reason,
 *                  institutions: [{name, country, type}], author_institutions: [[index]] }
 */
export async function loadPaperDetail(paper) {
  if (paper.detail || paper.detail_chunk === undefined) return paper
  const manifest = await loadManifest()
  const part = (groupInfo(manifest, paper.group).details || [])[paper.detail_chunk]
  if (!part) return paper
  const raw = (await fetchJson(part.file, manifest.generated_at))[paper.id] || {}
  paper.detail = {
    points: raw.pz || null,
    reason: raw.rr || '',
    institutions: (raw.ins || []).map((item) => ({ id: item.id || '', name: item.n, page: item.page || '', country: item.c || '', type: item.t || '' })),
    authors: (raw.au || []).map((item) => ({ id: item.id, name: item.n, page: item.page || '' })),
    author_institutions: raw.aa || [],
  }
  return paper
}

/**
 * Int8 vectors for one group: { dim, ids, scales: Float32Array, data: Int8Array }.
 * Row i of `data` (length dim) belongs to ids[i]; value ≈ data * scales[i].
 */
export async function loadGroupVectors(groupKey) {
  if (!vectorCache.has(groupKey)) {
    vectorCache.set(groupKey, (async () => {
      const manifest = await loadManifest()
      const info = groupInfo(manifest, groupKey)
      const dim = manifest.embedding.dimension
      const parts = await Promise.all(info.vectors.map(async (part) => {
        const [index, buffer] = await Promise.all([
          fetchJson(part.index.file, manifest.generated_at),
          fetch(dataUrl(part.bin.file, manifest.generated_at)).then((response) => {
            if (!response.ok) throw new Error(`Failed to load ${part.bin.file}`)
            return response.arrayBuffer()
          }),
        ])
        return { index, data: new Int8Array(buffer) }
      }))
      const ids = parts.flatMap((part) => part.index.ids)
      const scales = Float32Array.from(parts.flatMap((part) => part.index.scales))
      const data = new Int8Array(ids.length * dim)
      let offset = 0
      for (const part of parts) {
        data.set(part.data, offset)
        offset += part.data.length
      }
      return { dim, ids, scales, data }
    })().catch((error) => {
      vectorCache.delete(groupKey)
      throw error
    }))
  }
  return vectorCache.get(groupKey)
}

/** Dot product of a float query with every row of the given vector groups. */
export function scoreAgainst(query, groups) {
  const scores = {}
  for (const group of groups) {
    const { dim, ids, scales, data } = group
    for (let row = 0; row < ids.length; row += 1) {
      let total = 0
      const base = row * dim
      for (let k = 0; k < dim; k += 1) total += query[k] * data[base + k]
      scores[ids[row]] = total * scales[row]
    }
  }
  return scores
}

/** Dequantized float vector for one paper id, or null. */
export function vectorFor(paperId, groups) {
  for (const group of groups) {
    const row = group.ids.indexOf(paperId)
    if (row === -1) continue
    const vector = new Float32Array(group.dim)
    for (let k = 0; k < group.dim; k += 1) vector[k] = group.data[row * group.dim + k] * group.scales[row]
    return vector
  }
  return null
}
