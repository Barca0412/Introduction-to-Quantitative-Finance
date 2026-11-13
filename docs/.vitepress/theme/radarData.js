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
      if (!response.ok) throw new Error(`Failed to load ${file} (${response.status})`)
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
    abstract: record.s || '',
    abstract_truncated: record.ac !== undefined,
    abstract_chunk: record.ac,
    group: groupKey,
    abs_link: `https://arxiv.org/abs/${record.id}`,
    pdf_link: `https://arxiv.org/pdf/${record.id}`,
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

export async function loadAbstractChunk(groupKey, chunkIndex) {
  const manifest = await loadManifest()
  const info = groupInfo(manifest, groupKey)
  const part = info.abstracts[chunkIndex]
  if (!part) return {}
  return fetchJson(part.file, manifest.generated_at)
}

/** Replace snippets with full abstracts for the given papers (mutates them). */
export async function fillFullAbstracts(papers) {
  const needed = new Map()
  for (const paper of papers) {
    if (!paper.abstract_truncated) continue
    const key = `${paper.group}#${paper.abstract_chunk}`
    if (!needed.has(key)) needed.set(key, { group: paper.group, chunk: paper.abstract_chunk, papers: [] })
    needed.get(key).papers.push(paper)
  }
  await Promise.all([...needed.values()].map(async ({ group, chunk, papers: targets }) => {
    const abstracts = await loadAbstractChunk(group, chunk)
    for (const paper of targets) {
      if (abstracts[paper.id]) {
        paper.abstract = abstracts[paper.id]
        paper.abstract_truncated = false
      }
    }
  }))
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
