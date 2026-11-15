<script setup>
import { computed, nextTick, onBeforeUnmount, onMounted, reactive, ref, shallowRef, watch } from 'vue'
import { withBase } from 'vitepress'
import { loadManifest, loadTaxonomy, loadGroupPapers, loadPapersByIds, loadPaperDetail,
  loadGroupVectors, scoreAgainst, vectorFor } from '../../radarData.js'
import { FACETS, PUBLICATION, DISCIPLINE, SHORT, publication, entityPath, values, initialState, stateQuery,
  dateSpan, utc, iso, matches, orderPapers, matrixCounts } from './paperFilters.mjs'
import { createSemanticClient, SEARCH_MODEL, SEARCH_DIMENSION } from './semanticClient.js'
import './papers.css'

const manifest = shallowRef(null)
const taxonomy = shallowRef(null)
const papers = shallowRef([])
const state = reactive(initialState())
const ready = ref(false)
const mounted = ref(false)
const loading = ref(true)
const loadError = ref('')
const shown = ref(60)
const filtersOpen = ref(false)
const filterPanel = ref(null)
const filterTrigger = ref(null)
const drawer = ref(null)
const closeButton = ref(null)
const selected = shallowRef(null)
const detailLoading = ref(false)
const detailError = ref('')
const similarPapers = shallowRef([])
const similarLoading = ref(false)
const similarError = ref('')
const semanticStatus = ref('idle')
const semanticError = ref('')
const semanticScores = shallowRef(null)
const semanticQuery = ref('')
const client = createSemanticClient()
const groups = new Map()
let rangeRequest = 0, searchRequest = 0, detailRequest = 0, locationRequest = 0, searchTimer
let applyingLocation = false
let previousFocus, filterFocus, savedOverflow = '', disposed = false

const latest = computed(() => manifest.value?.latest_published_date || '')
const span = computed(() => dateSpan(state.range, state.anchor, latest.value))
const scores = computed(() => state.mode === 'sem' && state.query.trim() === semanticQuery.value ? semanticScores.value : null)
const filtered = computed(() => orderPapers(papers.value.filter((paper) => matches(paper, state, span.value, { scores: scores.value })), state.sort, scores.value))
const visible = computed(() => filtered.value.slice(0, shown.value))
const coreCount = computed(() => filtered.value.filter((paper) => paper.relevance === 3).length)
const activeCount = computed(() => Object.values(state.facets).reduce((total, ids) => total + ids.length, 0) + Number(state.core) + Number(state.code))
const chips = computed(() => Object.entries(state.facets).flatMap(([group, ids]) => ids.map((id) => ({ group, id, label: label(group, id, true) }))))
const rangePapers = computed(() => papers.value.filter((paper) => paper.published_date >= span.value[0] && paper.published_date <= span.value[1]))
const matrix = computed(() => matrixCounts(rangePapers.value))
const domains = computed(() => vocabulary('domain'))
const tasks = computed(() => vocabulary('task'))
const drawerAuthors = computed(() => selected.value?.detail?.authors || selected.value?.authors || [])
const drawerInstitutions = computed(() => selected.value?.detail?.institutions || [])
const pointFields = [['problem', '问题'], ['method', '方法'], ['result', '结果'], ['limitation', '局限']]
const ranges = [['day', '今天'], ['week', '本周'], ['month', '本月'], ['all', '全部']]
const sideGroups = ['pub', 'discipline', 'method', 'type', 'market']
const pointData = computed(() => selected.value?.detail?.points || {})
const currentIndex = computed(() => selected.value ? filtered.value.findIndex((paper) => paper.id === selected.value.id) : -1)
const rangeName = computed(() => {
  if (state.range === 'all') return '全部论文'
  if (state.range === 'day') return dateZh(state.anchor)
  if (state.range === '30d' || state.range === '90d') return `最近 ${Number.parseInt(state.range)} 天`
  if (state.range === 'year') return `${latest.value.slice(0, 4)} 年`
  if (state.range === 'month') return `${Number(state.anchor.slice(5, 7))} 月以来`
  return dateSpan('week', latest.value, latest.value)[0] === span.value[0] ? '本周' : `${shortDate(span.value[0])} 那周`
})
const title = computed(() => loading.value && !papers.value.length ? '论文' : `${rangeName.value}${activeCount.value || state.query.trim() ? '里筛出 ' : '，'}${filtered.value.length} 篇，其中 ${coreCount.value} 篇核心`)
const rangeLabel = computed(() => state.range === 'day' ? dateZh(state.anchor) : `${shortDate(span.value[0])} 至 ${shortDate(span.value[1])}`)
const canNext = computed(() => state.range === 'day' ? state.anchor < latest.value : span.value[1] < latest.value)
const codeCount = computed(() => papers.value.filter((paper) => matches(paper, state, span.value, { skip: 'code', scores: scores.value }) && paper.has_code).length)

function dateZh(date) { return date ? `${date.slice(0, 4) === latest.value.slice(0, 4) ? '' : date.slice(0, 4) + ' 年 '}${Number(date.slice(5, 7))} 月 ${Number(date.slice(8, 10))} 日` : '' }
function shortDate(date) { return date ? date.slice(0, 4) === latest.value.slice(0, 4) ? date.slice(5, 10) : date.slice(0, 4) : '' }
function label(group, id, short = false) {
  if (short && SHORT[id]) return SHORT[id]
  if (group === 'pub') return PUBLICATION[id] || id
  if (group === 'discipline') return DISCIPLINE[id] || id
  return taxonomy.value?.[FACETS[group].taxonomy]?.get(id) || id
}
function vocabulary(group) {
  const map = group === 'pub' ? new Map(Object.entries(PUBLICATION)) : group === 'discipline' ? new Map(Object.entries(DISCIPLINE)) : taxonomy.value?.[FACETS[group].taxonomy]
  return [...(map || [])].filter(([id]) => id !== 'none').map(([id, name]) => ({ id, name, short: SHORT[id] || name }))
}
function facetItems(group) {
  const base = papers.value.filter((paper) => matches(paper, state, span.value, { skip: group, scores: scores.value }))
  return vocabulary(group).map((item) => ({ ...item, on: state.facets[group].includes(item.id), n: base.filter((paper) => values(paper, group).includes(item.id)).length }))
    .filter((item) => item.n || item.on)
}
function toggleFacet(group, id) {
  const ids = state.facets[group]
  state.facets[group] = ids.includes(id) ? ids.filter((value) => value !== id) : [...ids, id]
}
function clearFilters() { for (const key of Object.keys(FACETS)) state.facets[key] = []; state.core = false; state.code = false }
function chooseCell(domain, task) {
  const on = state.facets.domain.length === 1 && state.facets.domain[0] === domain && state.facets.task.length === 1 && state.facets.task[0] === task
  clearFilters()
  state.facets.domain = on ? [] : [domain]
  state.facets.task = on ? [] : [task]
  state.query = ''
}
function cellCount(domain, task) { return matrix.value.counts[`${domain}|${task}`] || 0 }
function cellLabel(domain, task) { return `${domain.name} × ${task.name}：${cellCount(domain.id, task.id)} 篇` }
function rowLabels(paper, group) { return values(paper, group).map((id) => label(group, id, true)).join(' · ') }
function rowHow(paper) { return [rowLabels(paper, 'method'), `${label('pub', publication(paper))}${paper.venue?.name ? ' ' + paper.venue.name : ''}`, paper.has_code ? '有代码' : ''].filter(Boolean).join(' · ') }
function entityLink(kind, entity) { const path = entityPath(kind, entity); return path ? withBase(path) : '' }
function setRange(range) { if (latest.value) { state.range = range; state.anchor = latest.value } }
function step(direction) {
  if (!latest.value || !state.anchor) return
  const min = manifest.value?.archive?.at(-1)?.month ? `${manifest.value.archive.at(-1).month}-01` : manifest.value?.recent?.since || latest.value
  state.anchor = iso(Math.min(utc(latest.value), Math.max(utc(min), utc(state.anchor) + direction * (state.range === 'week' ? 7 : 1) * 86400000)))
}
function syncUrl() {
  if (!ready.value || disposed || applyingLocation) return
  const query = stateQuery(state, latest.value)
  const hash = selected.value ? `#paper=${encodeURIComponent(selected.value.id)}` : ''
  history.replaceState(history.state, '', location.pathname + (query ? `?${query}` : '') + hash)
}
async function ensureRange() {
  if (!manifest.value) return
  const ticket = ++rangeRequest
  loading.value = true
  loadError.value = ''
  const [from, until] = span.value
  const needed = ['recent', ...manifest.value.archive.filter(({ month }) => month >= from.slice(0, 7) && month <= until.slice(0, 7)).map(({ month }) => `archive/${month}`)]
  try {
    await Promise.all(needed.map(async (key) => { if (!groups.has(key)) groups.set(key, await loadGroupPapers(key)) }))
    if (disposed || ticket !== rangeRequest) return
    papers.value = [...new Map([...groups.values()].flat().map((paper) => [paper.id, paper])).values()]
  } catch { if (ticket === rangeRequest) loadError.value = '论文数据暂时未能加载，请重试。' }
  finally { if (ticket === rangeRequest) loading.value = false }
}
async function vectorGroups(targetPapers = papers.value) {
  const keys = [...new Set(targetPapers.map((paper) => paper.group))]
  const result = await Promise.all(keys.map(loadGroupVectors))
  if (!result.some((group) => group.ids.length)) throw new Error('No vectors available')
  return result
}
async function runSemantic() {
  clearTimeout(searchTimer)
  const ticket = ++searchRequest
  const query = state.query.trim()
  semanticScores.value = null
  semanticQuery.value = ''
  if (state.mode !== 'sem' || !query) { semanticStatus.value = 'idle'; return }
  semanticStatus.value = 'loading'
  semanticError.value = ''
  let deadline
  try {
    const work = async () => {
      await ensureRange()
      if (disposed || ticket !== searchRequest) throw new Error('Search superseded')
      if (manifest.value?.embedding?.model !== SEARCH_MODEL || manifest.value?.embedding?.dimension !== SEARCH_DIMENSION) throw new Error('Incompatible search vectors')
      return Promise.all([client.embed(query), vectorGroups()])
    }
    const [vector, data] = await Promise.race([work(), new Promise((_, reject) => {
      deadline = setTimeout(() => {
        if (ticket === searchRequest) client.stop('Search timed out')
        reject(new Error('Search timed out'))
      }, 60_000)
    })])
    if (disposed || ticket !== searchRequest || state.mode !== 'sem' || state.query.trim() !== query) return
    semanticScores.value = scoreAgainst(vector, data)
    semanticQuery.value = query
    semanticStatus.value = 'ready'
  } catch {
    if (disposed || ticket !== searchRequest) return
    client.stop()
    semanticError.value = '按意思找暂时不可用，已切回关键词搜索。'
    state.mode = 'kw'
    semanticStatus.value = 'error'
  } finally { clearTimeout(deadline) }
}
function retrySemantic() { semanticError.value = ''; state.mode = 'sem' }
function retryLoad() { if (manifest.value) ensureRange(); else window.location.reload() }
function scheduleSearch() {
  ++searchRequest
  clearTimeout(searchTimer)
  semanticScores.value = null
  semanticQuery.value = ''
  semanticStatus.value = state.mode === 'sem' && state.query.trim() ? 'loading' : 'idle'
  if (state.mode === 'sem' && state.query.trim()) searchTimer = setTimeout(runSemantic, 450)
  else client.stop()
}
async function openPaper(paper, focus = true) {
  if (!selected.value) previousFocus = document.activeElement
  const ticket = ++detailRequest
  selected.value = paper
  detailLoading.value = true
  detailError.value = ''
  similarPapers.value = []
  similarError.value = ''
  syncUrl()
  await nextTick()
  if (focus) closeButton.value?.focus({ preventScroll: true })
  drawer.value?.scrollTo({ top: 0 })
  try {
    const result = await loadPaperDetail(paper)
    if (ticket === detailRequest && !disposed) selected.value = { ...result }
  } catch { if (ticket === detailRequest) detailError.value = '这篇论文的解读暂时未能加载。' }
  finally { if (ticket === detailRequest) detailLoading.value = false }
  if (ticket === detailRequest && !disposed) loadSimilar(paper, ticket)
}
async function loadSimilar(paper, ticket = detailRequest) {
  similarLoading.value = true
  try {
    const keys = ['recent', ...manifest.value.archive.map(({ month }) => `archive/${month}`)]
    const data = await Promise.all(keys.map(loadGroupVectors))
    const vector = vectorFor(paper.id, data)
    if (!vector) throw new Error('Paper has no vector')
    const ranked = Object.entries(scoreAgainst(vector, data)).filter(([id, score]) => id !== paper.id && Number.isFinite(score))
      .sort((a, b) => b[1] - a[1] || a[0].localeCompare(b[0])).slice(0, 5).map(([id]) => id)
    const result = await loadPapersByIds(ranked)
    if (ticket !== detailRequest || disposed) return
    const byId = new Map(result.map((item) => [item.id, item]))
    similarPapers.value = ranked.map((id) => byId.get(id)).filter(Boolean)
  } catch { if (ticket === detailRequest) similarError.value = '这篇论文暂时没有可用的相似论文结果。' }
  finally { if (ticket === detailRequest) similarLoading.value = false }
}
function closePaper(restore = true) {
  ++detailRequest
  selected.value = null
  syncUrl()
  if (restore) nextTick(() => previousFocus?.isConnected && previousFocus.focus({ preventScroll: true }))
}
function navigatePaper(direction) {
  const index = currentIndex.value + direction
  if (currentIndex.value >= 0 && index >= 0 && index < filtered.value.length) openPaper(filtered.value[index])
}
async function fromLocation() {
  if (!manifest.value) return
  const ticket = ++locationRequest
  let id = new URLSearchParams(location.search).get('paper')
  try { if (location.hash.startsWith('#paper=')) id = decodeURIComponent(location.hash.slice(7)) } catch { id = '' }
  applyingLocation = true
  try {
    Object.assign(state, initialState(location.search, latest.value))
    await ensureRange()
    if (ticket !== locationRequest || disposed) return
    if (id) {
      const paper = papers.value.find((item) => item.id === id) || (await loadPapersByIds([id]))[0]
      if (ticket !== locationRequest || disposed) return
      if (paper) await openPaper(paper)
      else loadError.value = '这篇论文目前不在公开列表里。'
    } else if (selected.value) closePaper(false)
  } catch { if (ticket === locationRequest) loadError.value = '这篇论文暂时未能加载，请重试。' }
  finally { if (ticket === locationRequest) { applyingLocation = false; syncUrl() } }
}
async function toggleFilters(open) {
  if (open) filterFocus = document.activeElement
  filtersOpen.value = open
  await nextTick()
  if (open) filterPanel.value?.querySelector('button')?.focus()
  else filterFocus?.focus({ preventScroll: true })
}
function onKey(event) {
  const modal = selected.value ? drawer.value : filtersOpen.value ? filterPanel.value : null
  if (!modal) return
  if (event.key === 'Escape') { event.preventDefault(); selected.value ? closePaper() : toggleFilters(false); return }
  if (event.key === 'Tab') {
    const focusable = [...modal.querySelectorAll('a[href],button:not([disabled]),input,select,[tabindex="0"]')].filter((item) => item.getClientRects().length)
    const first = focusable[0], last = focusable.at(-1)
    if (event.shiftKey && (document.activeElement === first || !modal.contains(document.activeElement))) { event.preventDefault(); last?.focus() }
    else if (!event.shiftKey && (document.activeElement === last || !modal.contains(document.activeElement))) { event.preventDefault(); first?.focus() }
  }
  if (selected.value && !/INPUT|TEXTAREA|SELECT/.test(event.target.tagName)) {
    if (event.key === 'ArrowLeft') { event.preventDefault(); navigatePaper(-1) }
    if (event.key === 'ArrowRight') { event.preventDefault(); navigatePaper(1) }
  }
}
watch(state, () => { shown.value = 60; syncUrl() }, { deep: true })
watch(() => [state.range, state.anchor], async () => { if (ready.value && !applyingLocation) { await ensureRange(); if (state.mode === 'sem' && state.query.trim()) runSemantic() } })
watch(() => [state.query, state.mode], () => { if (ready.value) scheduleSearch() })
watch(() => Boolean(selected.value) || filtersOpen.value, (open) => {
  if (typeof document === 'undefined') return
  if (open) { savedOverflow = document.body.style.overflow; document.body.style.overflow = 'hidden' }
  else document.body.style.overflow = savedOverflow
})
watch(selected, (paper) => { if (typeof document !== 'undefined') document.getElementById('app')?.toggleAttribute('inert', Boolean(paper)) })
onMounted(async () => {
  mounted.value = true
  document.addEventListener('keydown', onKey)
  window.addEventListener('popstate', fromLocation)
  window.addEventListener('hashchange', fromLocation)
  try {
    [manifest.value, taxonomy.value] = await Promise.all([loadManifest(), loadTaxonomy()])
    await fromLocation()
    ready.value = true
    if (state.mode === 'sem' && state.query.trim()) runSemantic()
  } catch { loadError.value = '论文数据暂时未能加载，请重试。'; loading.value = false }
})
onBeforeUnmount(() => {
  disposed = true; ++searchRequest; ++detailRequest; ++rangeRequest
  clearTimeout(searchTimer); client.stop()
  document.removeEventListener('keydown', onKey)
  window.removeEventListener('popstate', fromLocation)
  window.removeEventListener('hashchange', fromLocation)
  document.body.style.overflow = savedOverflow
  document.getElementById('app')?.removeAttribute('inert')
})
</script>

<template>
  <div class="radar-papers" :data-range="state.range" :data-ready="ready ? '1' : '0'">
    <div class="rp-title-row">
      <h1>{{ title }}</h1>
      <div class="rp-seg rp-sort" role="group" aria-label="排序">
        <button type="button" :aria-pressed="state.sort === 'new'" @click="state.sort = 'new'">最新</button>
        <button type="button" :aria-pressed="state.sort === 'rel'" @click="state.sort = 'rel'">相关度</button>
      </div>
    </div>
    <div class="rp-toolbar">
      <form class="rp-search" role="search" @submit.prevent="state.mode === 'sem' && runSemantic()">
        <label class="rp-vh" for="radar-paper-query">搜索论文</label>
        <input id="radar-paper-query" v-model="state.query" type="search" autocomplete="off" :placeholder="state.mode === 'sem' ? '用一句话描述你想找的研究' : '搜标题、作者、机构'">
        <div class="rp-seg" role="group" aria-label="搜索方式">
          <button type="button" :aria-pressed="state.mode === 'kw'" @click="state.mode = 'kw'; semanticError = ''">关键词</button>
          <button type="button" :aria-pressed="state.mode === 'sem'" @click="state.mode = 'sem'">按意思找</button>
        </div>
      </form>
      <div class="rp-seg" role="group" aria-label="日期范围"><button v-for="[id, name] in ranges" :key="id" type="button" :aria-pressed="state.range === id" @click="setRange(id)">{{ name }}</button></div>
      <div v-if="['day', 'week'].includes(state.range)" class="rp-stepper">
        <button type="button" aria-label="往前" @click="step(-1)">‹</button><span>{{ rangeLabel }}</span>
        <button type="button" aria-label="往后" :disabled="!canNext" @click="step(1)">›</button>
      </div>
      <button type="button" class="rp-toggle rp-core-toggle" :aria-pressed="state.core" @click="state.core = !state.core">只看核心</button>
      <button ref="filterTrigger" type="button" class="rp-filter-open" :aria-expanded="filtersOpen" aria-controls="radar-paper-filters" @click="toggleFilters(true)">筛选<span v-if="activeCount">{{ activeCount }}</span></button>
      <p class="rp-count" aria-live="polite">{{ filtered.length }} 篇<span v-if="!state.core">，其中核心 {{ coreCount }} 篇</span></p>
    </div>
    <p v-if="semanticStatus === 'loading'" class="rp-search-status" role="status">正在准备按意思找，首次使用需加载约 23 MB 的搜索模型…</p>
    <p v-else-if="semanticStatus === 'ready' && scores" class="rp-search-status" role="status">已按语义相近程度排序。英文描述通常更准确。</p>
    <p v-if="semanticError" class="rp-search-status" role="status">{{ semanticError }} <button type="button" @click="retrySemantic">重试按意思找</button></p>
    <p v-if="loadError" class="rp-search-status" role="alert">{{ loadError }} <button type="button" @click="retryLoad">重试</button></p>
    <div v-if="chips.length || state.code || state.core" class="rp-chips">
      <button v-for="chip in chips" :key="chip.group + chip.id" type="button" class="rp-chip" :aria-label="`去掉筛选：${chip.label}`" @click="toggleFacet(chip.group, chip.id)">{{ chip.label }} <span aria-hidden="true">×</span></button>
      <button v-if="state.core" class="rp-chip" type="button" @click="state.core = false">只看核心 ×</button>
      <button v-if="state.code" class="rp-chip" type="button" @click="state.code = false">有代码 ×</button>
      <button type="button" class="rp-chip rp-clear" @click="clearFilters">清空</button>
    </div>
    <div class="rp-work">
      <section class="rp-list rp-panel" aria-label="论文列表" :aria-busy="loading">
        <ul class="rp-rows">
          <li v-if="loading && !papers.length" class="rp-empty" role="status">正在加载论文…</li>
          <li v-else-if="!filtered.length" class="rp-empty">这个范围里没有符合条件的论文。去掉一个筛选条件，或者把日期换成“全部”。</li>
          <li v-for="paper in visible" :key="paper.id" class="rp-row" :class="{ 'is-core': paper.relevance === 3 }">
            <a class="rp-row-link" :href="`#paper=${encodeURIComponent(paper.id)}`" :aria-current="selected?.id === paper.id ? 'true' : undefined" @click.prevent="openPaper(paper)">
              <span class="rp-row-date">{{ shortDate(paper.published_date) }}</span>
              <span class="rp-row-core"><span v-if="paper.relevance === 3" class="rp-core-mark">核心</span></span>
              <span class="rp-row-main"><span class="rp-row-title" lang="en" :title="paper.title">{{ paper.title }}</span><span class="rp-row-tldr">{{ paper.tldr_zh || paper.summary_zh }}</span></span>
              <span class="rp-row-meta"><span class="rp-row-what">{{ [rowLabels(paper, 'domain'), rowLabels(paper, 'task')].filter(Boolean).join(' · ') }}</span><span class="rp-row-how">{{ rowHow(paper) }}</span></span>
            </a>
          </li>
        </ul>
        <button v-if="shown < filtered.length" type="button" class="rp-more" @click="shown += 60">再看 {{ Math.min(60, filtered.length - shown) }} 篇</button>
      </section>
      <aside id="radar-paper-filters" ref="filterPanel" class="rp-filters" :class="{ 'is-open': filtersOpen }" :role="filtersOpen ? 'dialog' : undefined" :aria-modal="filtersOpen ? 'true' : undefined" aria-label="筛选">
        <div class="rp-filters-head"><p>筛选</p><button type="button" @click="toggleFilters(false)">完成</button></div>
        <div class="rp-mobile-controls rp-panel">
          <button type="button" class="rp-toggle" :aria-pressed="state.core" @click="state.core = !state.core">只看核心</button>
          <div class="rp-seg" role="group" aria-label="排序"><button type="button" :aria-pressed="state.sort === 'new'" @click="state.sort = 'new'">最新</button><button type="button" :aria-pressed="state.sort === 'rel'" @click="state.sort = 'rel'">相关度</button></div>
          <div v-if="['day', 'week'].includes(state.range)" class="rp-stepper"><button type="button" aria-label="往前" @click="step(-1)">‹</button><span>{{ rangeLabel }}</span><button type="button" aria-label="往后" :disabled="!canNext" @click="step(1)">›</button></div>
        </div>
        <section class="rp-panel rp-rail-grid" aria-labelledby="rp-grid-title">
          <h2 id="rp-grid-title" class="rp-facet-title">金融领域 × 任务</h2>
          <table class="rp-matrix"><caption>点越大，论文越多。点一下只看那一格。</caption>
            <thead><tr><th scope="col"><span class="rp-vh">金融领域</span></th><th v-for="task in tasks" :key="task.id" scope="col" class="rp-matrix-task"><button type="button" :aria-pressed="state.facets.task.includes(task.id)" :title="task.name" @click="toggleFacet('task', task.id)"><span>{{ task.short }}</span></button></th></tr></thead>
            <tbody><tr v-for="domain in domains" :key="domain.id"><th scope="row" class="rp-matrix-domain"><button type="button" :title="domain.name" :aria-pressed="state.facets.domain.includes(domain.id)" @click="toggleFacet('domain', domain.id)">{{ domain.short }}</button></th>
              <td v-for="task in tasks" :key="task.id" class="rp-matrix-cell" :data-n="cellCount(domain.id, task.id)">
                <button v-if="cellCount(domain.id, task.id)" type="button" :class="{ peak: cellCount(domain.id, task.id) > matrix.max * .75, chosen: state.facets.domain.includes(domain.id) && state.facets.task.includes(task.id) }" :style="{ '--r': cellCount(domain.id, task.id) / matrix.max }" :aria-label="cellLabel(domain, task)" :title="cellLabel(domain, task)" @click="chooseCell(domain.id, task.id)"><span class="rp-vh">{{ cellCount(domain.id, task.id) }}</span></button>
                <span v-else class="rp-matrix-zero" :aria-label="cellLabel(domain, task)"></span>
              </td>
            </tr></tbody>
          </table>
        </section>
        <div class="rp-panel rp-rail-facets">
          <template v-for="(group, index) in sideGroups" :key="group">
            <section class="rp-facet"><h2 class="rp-facet-title">{{ FACETS[group].title }}</h2><ul class="rp-facet-list"><li v-for="item in facetItems(group)" :key="item.id"><button type="button" :aria-pressed="item.on" :title="item.name" @click="toggleFacet(group, item.id)"><span>{{ item.short }}</span><span class="rp-facet-count">{{ item.n }}</span></button></li></ul></section>
            <section v-if="index === 1" class="rp-facet"><h2 class="rp-facet-title">可复现</h2><ul class="rp-facet-list"><li><button type="button" :aria-pressed="state.code" @click="state.code = !state.code"><span>有代码</span><span class="rp-facet-count">{{ codeCount }}</span></button></li></ul></section>
          </template>
        </div>
      </aside>
    </div>
  </div>
  <Teleport v-if="mounted" to="body">
    <div v-if="selected" class="radar-paper-overlay">
      <div class="rp-scrim" aria-hidden="true" @click="closePaper()"></div>
      <aside ref="drawer" class="rp-drawer" role="dialog" aria-modal="true" aria-labelledby="radar-paper-title">
        <header class="rp-drawer-head"><p>{{ dateZh(selected.published_date) }}<template v-if="selected.is_arxiv"> · arXiv {{ selected.id }}</template><template v-else-if="selected.venue"> · {{ selected.venue.name }}</template></p><button ref="closeButton" type="button" @click="closePaper()">关闭</button></header>
        <div class="rp-drawer-body">
          <h2 id="radar-paper-title" class="rp-drawer-title" lang="en">{{ selected.title }}</h2>
          <div class="rp-drawer-authors"><p><template v-for="(author, index) in drawerAuthors" :key="author.id || index"><span v-if="index">，</span><a v-if="author.page" :href="entityLink('author', author)">{{ author.name }}</a><span v-else>{{ author.name }}</span><sup v-if="selected.detail?.author_institutions?.[index]?.length">{{ selected.detail.author_institutions[index].map((i) => i + 1).join(',') }}</sup></template><span v-if="selected.author_count > drawerAuthors.length"> 等 {{ selected.author_count }} 人</span></p>
            <p class="rp-drawer-institutions"><template v-for="(institution, index) in drawerInstitutions" :key="institution.id || index"><span v-if="index"> · </span><sup>{{ index + 1 }}</sup><a v-if="institution.page" :href="entityLink('institution', institution)">{{ institution.name }}</a><span v-else>{{ institution.name }}</span></template><template v-if="!drawerInstitutions.length">{{ (selected.affiliations || []).join(' · ') }}</template></p>
          </div>
          <p class="rp-drawer-tldr"><span v-if="selected.relevance === 3" class="rp-core-mark">核心</span>{{ selected.tldr_zh || selected.summary_zh }}</p>
          <p v-if="detailLoading" class="rp-status" role="status">正在加载解读…</p>
          <p v-if="detailError" class="rp-status" role="status">{{ detailError }} <button type="button" @click="openPaper(selected)">重试</button></p>
          <dl class="rp-points"><div v-for="[key, name] in pointFields" :key="key"><dt>{{ name }}</dt><dd>{{ pointData[key] || (detailLoading ? '加载中…' : '暂无解读') }}</dd></div></dl>
          <p class="rp-drawer-actions"><a v-if="selected.pdf_link" class="rp-action-primary" :href="selected.pdf_link" target="_blank" rel="noopener noreferrer">打开 PDF</a><a v-if="selected.abs_link" :class="{ 'rp-action-primary': !selected.pdf_link }" :href="selected.abs_link" target="_blank" rel="noopener noreferrer">{{ selected.is_arxiv ? 'arXiv 页面' : '论文页面' }}</a></p>
          <section class="rp-drawer-section"><h3>分类</h3><dl class="rp-kvs">
            <div><dt>相关度</dt><dd><b>{{ selected.relevance === 3 ? '核心' : '主要应用' }}</b>　{{ selected.detail?.reason }}</dd></div>
            <div v-for="group in ['type', 'domain', 'task', 'method', 'market']" v-show="values(selected, group).length" :key="group"><dt>{{ FACETS[group].title }}</dt><dd>{{ values(selected, group).map((id) => label(group, id)).join(' · ') }}</dd></div>
            <div><dt>发表状态</dt><dd>{{ label('pub', publication(selected)) }}<template v-if="selected.venue">　{{ selected.venue.name }}<span v-if="selected.venue.official">（官方录用名单）</span><template v-if="selected.venue.note"> · {{ selected.venue.note }}</template></template></dd></div>
            <div v-if="selected.discipline"><dt>学科</dt><dd>{{ label('discipline', selected.discipline) }}</dd></div>
            <div v-if="selected.has_code"><dt>可复现</dt><dd>有代码</dd></div>
            <div v-if="selected.keywords_std?.length || selected.keywords?.length"><dt>关键词</dt><dd>{{ selected.keywords_std?.length ? selected.keywords_std.map((k) => k.label).join(' · ') : selected.keywords.join(' · ') }}</dd></div>
          </dl></section>
          <section class="rp-drawer-section"><h3>相近的 5 篇</h3><p v-if="similarLoading" class="rp-status" role="status">正在查找相近论文…</p><p v-else-if="similarError" class="rp-status">{{ similarError }}</p><ul v-else class="rp-similar"><li v-for="paper in similarPapers" :key="paper.id"><a :href="`#paper=${encodeURIComponent(paper.id)}`" @click.prevent="openPaper(paper)"><span lang="en">{{ paper.title }}</span><small>{{ paper.tldr_zh || paper.summary_zh }}</small></a></li></ul></section>
          <nav class="rp-drawer-pager" aria-label="切换论文"><button type="button" :disabled="currentIndex <= 0" @click="navigatePaper(-1)">← 上一篇</button><span>键盘 ← → 切换</span><button type="button" :disabled="currentIndex < 0 || currentIndex >= filtered.length - 1" @click="navigatePaper(1)">下一篇 →</button></nav>
        </div>
      </aside>
    </div>
  </Teleport>
</template>
