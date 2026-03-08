<template>
  <div class="papers-list">
    <div class="papers-layout">
      <section class="papers-main">
        <div class="list-intro">
          <div>
            <p class="eyebrow">Focused Radar</p>
            <h2 class="list-title">AI + Finance, agent planning, and deep research first</h2>
            <p class="list-description">
              The default view prioritizes papers that match your target themes, while still keeping
              the full 10-category arXiv recall layer available.
            </p>
          </div>
          <div class="list-stats">
            <div class="stat-pill">
              <strong>{{ visiblePapers.length }}</strong>
              <span>visible now</span>
            </div>
            <div class="stat-pill secondary">
              <strong>{{ allPapers.length }}</strong>
              <span>total indexed</span>
            </div>
          </div>
        </div>

        <div class="results-meta">
          <span>
            Showing <strong>{{ visiblePapers.length }}</strong> of <strong>{{ filteredPapers.length }}</strong> papers
            <template v-if="selectedQuickFilter !== 'all'">for {{ quickFilterLabel }}</template>
          </span>
          <span v-if="selectedTags.length || selectedAffiliation">
            <template v-if="selectedTags.length">Active tags: {{ selectedTags.join(', ') }}</template>
            <template v-if="selectedTags.length && selectedAffiliation"> · </template>
            <template v-if="selectedAffiliation">Affiliation: {{ selectedAffiliation }}</template>
          </span>
          <span v-if="semanticModeLabel">{{ semanticModeLabel }}</span>
        </div>

        <div v-if="loading" class="loading-indicator">
          Loading papers...
        </div>

        <div v-else-if="filteredPapers.length === 0" class="no-results">
          <div class="no-results-icon">📭</div>
          <p>No papers found matching your current focus and filters.</p>
        </div>

        <div v-else class="papers-feed">
          <PaperCard
            v-for="row in visiblePaperRows"
            :key="row.paper.id"
            :paper="row.paper"
            :semantic-active="semanticSearchActive"
            :semantic-rank="row.rank"
            :semantic-score="row.score"
            :highlight-level="row.highlightLevel"
            @filter-tag="toggleTag"
            @filter-affiliation="applyAffiliationFilter"
            @find-similar="activateSimilarPapers"
          />
        </div>

        <div v-if="canLoadMore" class="load-more-wrap">
          <button type="button" class="load-more-btn" @click="loadMore">
            Show more papers
          </button>
        </div>
      </section>

      <aside class="papers-sidebar">
        <div class="sidebar-panel sticky-panel">
          <div class="sidebar-block">
            <div class="sidebar-heading">
              <h3>Focus Tracks</h3>
              <p>Use the right-side controls to keep the cards on the left focused on your workflow.</p>
            </div>

            <div class="quick-filters">
              <button
                v-for="filter in quickFilters"
                :key="filter.id"
                type="button"
                class="quick-filter-btn"
                :class="{ active: selectedQuickFilter === filter.id }"
                @click="selectedQuickFilter = filter.id"
              >
                <span>{{ filter.label }}</span>
                <small>{{ filter.description }}</small>
              </button>
            </div>
          </div>

          <div class="sidebar-block">
            <div class="sidebar-heading compact">
              <h3>Refine Results</h3>
            </div>

            <div class="search-stack">
              <input
                v-model="searchQuery"
                type="text"
                class="search-input"
                placeholder="Search title, abstract, keywords..."
              >

              <select v-model="selectedCategory" class="filter-select">
                <option value="">All Categories</option>
                <option v-for="cat in categories" :key="cat" :value="cat">
                  {{ getCategoryName(cat) }}
                </option>
              </select>

              <select v-model="sortMode" class="filter-select">
                <option value="focus">Sort by Focus</option>
                <option value="latest">Sort by Latest</option>
              </select>

              <div class="affiliation-filter-wrap">
                <input
                  v-model="selectedAffiliation"
                  list="affiliation-options"
                  type="text"
                  class="search-input"
                  placeholder="Filter by affiliation..."
                >
                <datalist id="affiliation-options">
                  <option v-for="affiliation in allAffiliations" :key="affiliation" :value="affiliation" />
                </datalist>
              </div>

              <DateFilter
                :papers="allPapers"
                :model-value="selectedDate"
                @filter="onDateFilter"
              />

              <button
                v-if="selectedTags.length || selectedCategory || searchQuery || selectedDate || selectedAffiliation || selectedQuickFilter !== 'focused'"
                type="button"
                class="reset-btn"
                @click="resetFilters"
              >
                Reset filters
              </button>
            </div>
          </div>

          <div class="sidebar-block">
            <div class="sidebar-heading compact">
              <h3>Embedding Search</h3>
              <p>Search by meaning and rank papers by semantic similarity, not just exact keywords.</p>
            </div>

            <div class="search-stack">
              <input
                v-model="semanticQuery"
                type="text"
                class="search-input"
                placeholder="Search by idea with embeddings..."
                @keyup.enter="runSemanticSearch"
              >

              <div class="semantic-actions">
                <button type="button" class="semantic-btn primary" @click="runSemanticSearch">
                  Run semantic search
                </button>
                <button
                  v-if="semanticSearchActive"
                  type="button"
                  class="semantic-btn"
                  @click="clearSemanticSearch"
                >
                  Clear
                </button>
              </div>

              <div class="semantic-status" :class="semanticStatusClass">
                {{ semanticStatusMessage }}
              </div>

              <div class="semantic-theme-grid">
                <button
                  v-for="theme in embeddingThemeOptions"
                  :key="theme.id"
                  type="button"
                  class="semantic-theme-btn"
                  :class="{ active: selectedEmbeddingTheme === theme.id }"
                  @click="activateEmbeddingTheme(theme.id)"
                >
                  <span>{{ theme.label }}</span>
                  <small>{{ theme.description }}</small>
                </button>
              </div>
            </div>
          </div>

          <div v-if="allTags.length > 0" class="sidebar-block">
            <div class="sidebar-heading compact">
              <h3>Tag Filters</h3>
            </div>

            <div class="tags-filter">
              <button
                v-for="tag in allTags"
                :key="tag"
                type="button"
                class="tag-filter-btn"
                :class="{ active: selectedTags.includes(tag) }"
                @click="toggleTag(tag)"
              >
                {{ formatTag(tag) }}
              </button>
            </div>
          </div>
        </div>
      </aside>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { withBase } from 'vitepress'

import DateFilter from './DateFilter.vue'
import PaperCard from './PaperCard.vue'

const quickFilters = [
  { id: 'focused', label: 'Focused Radar', description: 'AI+Finance + agentic themes' },
  { id: 'ai-finance', label: 'AI + Finance', description: 'Market, trading, risk, portfolio' },
  { id: 'agent-planning', label: 'Agent Planning', description: 'ReAct, workflows, planning' },
  { id: 'deep-research', label: 'Deep Research', description: 'Research agents, surveys, synthesis' },
  { id: 'multi-agent', label: 'Multi-Agent', description: 'Coordination and agent teams' },
  { id: 'tool-use', label: 'Tool Use', description: 'Function calling and tools' },
  { id: 'reasoning', label: 'Reasoning', description: 'Inference and multi-step thought' },
  { id: 'all', label: 'All Papers', description: 'Everything from the 10 categories' }
]

const embeddingThemeOptions = [
  { id: 'ai-finance', label: 'Semantic AI + Finance', description: 'Finance workflows, trading, risk, research' },
  { id: 'agent-planning', label: 'Semantic Planning', description: 'Autonomous planning and decomposition' },
  { id: 'deep-research', label: 'Semantic Research', description: 'Research agents and evidence synthesis' },
  { id: 'multi-agent', label: 'Semantic Multi-Agent', description: 'Coordination, debate, teams' },
  { id: 'tool-use', label: 'Semantic Tool Use', description: 'Function calling, browser, computer use' },
  { id: 'reasoning', label: 'Semantic Reasoning', description: 'Inference and multi-step reasoning' }
]

const categoryNames = {
  'cs.AI': 'Artificial Intelligence',
  'cs.CL': 'Computation and Language',
  'cs.MA': 'Multiagent Systems',
  'cs.IR': 'Information Retrieval',
  'cs.SE': 'Software Engineering',
  'cs.CE': 'Computational Engineering, Finance, and Science',
  'q-fin.ST': 'Statistical Finance',
  'q-fin.CP': 'Computational Finance',
  'q-fin.PM': 'Portfolio Management',
  'q-fin.TR': 'Trading and Market Microstructure'
}

const preferredTagOrder = [
  'ai-finance',
  'agent-planning',
  'deep-research',
  'multi-agent',
  'tool-use',
  'reasoning',
  'memory',
  'rag',
  'time-series',
  'benchmark',
  'training-efficiency',
  'multimodal',
  'prompt-engineering',
  'rlhf-alignment',
  'code-generation'
]

const searchQuery = ref('')
const semanticQuery = ref('')
const selectedCategory = ref('')
const selectedTags = ref([])
const selectedAffiliation = ref('')
const selectedDate = ref('')
const selectedQuickFilter = ref('focused')
const selectedEmbeddingTheme = ref('')
const selectedSimilarPaperId = ref('')
const selectedSimilarPaperTitle = ref('')
const sortMode = ref('focus')
const visibleCount = ref(24)
const loading = ref(false)
const allPapers = ref([])
const categories = ref([])
const allTags = ref([])
const allAffiliations = ref([])
const semanticScores = ref({})
const semanticStatus = ref('idle')
const semanticError = ref('')

let embeddingsIndex = null
let semanticExtractorPromise = null

const getCategoryName = (cat) => categoryNames[cat] || cat

const formatTag = (tag) => {
  return tag
    .split('-')
    .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
    .join(' ')
}

const quickFilterLabel = computed(() => {
  return quickFilters.find((filter) => filter.id === selectedQuickFilter.value)?.label || 'Focused Radar'
})

const semanticSearchActive = computed(() => {
  return Boolean(
    selectedEmbeddingTheme.value
      || selectedSimilarPaperId.value
      || (semanticQuery.value.trim() && Object.keys(semanticScores.value).length > 0)
  )
})

const semanticModeLabel = computed(() => {
  if (selectedSimilarPaperId.value) {
    return `Similar to: ${selectedSimilarPaperTitle.value}`
  }
  if (selectedEmbeddingTheme.value) {
    const theme = embeddingThemeOptions.find((item) => item.id === selectedEmbeddingTheme.value)
    return theme ? `Embedding theme: ${theme.label}` : 'Embedding theme active'
  }
  if (semanticQuery.value.trim() && Object.keys(semanticScores.value).length > 0) {
    return `Semantic query: ${semanticQuery.value.trim()}`
  }
  return ''
})

const semanticStatusClass = computed(() => {
  if (semanticStatus.value === 'error') return 'error'
  if (semanticStatus.value === 'ready') return 'ready'
  if (semanticStatus.value === 'loading-model' || semanticStatus.value === 'loading-index' || semanticStatus.value === 'searching') return 'loading'
  return 'idle'
})

const semanticStatusMessage = computed(() => {
  if (semanticStatus.value === 'loading-index') return 'Loading embedding index...'
  if (semanticStatus.value === 'loading-model') return 'Loading local embedding model for browser search...'
  if (semanticStatus.value === 'searching') return 'Ranking papers by semantic similarity...'
  if (semanticStatus.value === 'ready' && semanticModeLabel.value) return `${semanticModeLabel.value} - top semantic matches are highlighted in the list.`
  if (semanticStatus.value === 'error') return semanticError.value || 'Semantic search failed'
  return 'Use semantic search for idea-based retrieval or click a semantic theme to rank papers by embeddings.'
})

const paperAffiliations = (paper) => {
  const values = Array.isArray(paper.affiliations) && paper.affiliations.length > 0
    ? paper.affiliations
    : String(paper.affiliation || '')
        .split(/[;；]+/)
        .map((value) => value.trim())

  return values.filter((value) => value && value !== 'Unknown')
}

const paperMatchesQuickFilter = (paper) => {
  const filter = selectedQuickFilter.value
  const focus = paper.focus || {}
  const tags = paper.tags || []
  const topics = focus.topics || []

  if (filter === 'all') return true
  if (filter === 'focused') return Boolean(focus.is_focus || focus.score >= 10)
  return tags.includes(filter) || topics.includes(filter) || focus.primary_topic === filter
}

const paperSearchText = (paper) => {
  const focusLabels = paper.focus?.labels || []
  const reasons = paper.focus?.reasons || []
  return [
    paper.title,
    paper.abstract,
    ...(paper.keywords || []),
    ...(paper.tags || []),
    ...focusLabels,
    ...reasons
  ]
    .join(' ')
    .toLowerCase()
}

const fallbackSort = (left, right) => {
  if (sortMode.value === 'focus') {
    const focusDelta = (right.focus?.score || 0) - (left.focus?.score || 0)
    if (focusDelta !== 0) return focusDelta
  }

  const dateDelta = String(right.published_date || '').localeCompare(String(left.published_date || ''))
  if (dateDelta !== 0) return dateDelta

  return String(right.id || '').localeCompare(String(left.id || ''))
}

const sortPapers = (papers) => {
  return [...papers].sort((left, right) => {
    return fallbackSort(left, right)
  })
}

const scoreForPaper = (paperId) => {
  const score = semanticScores.value[paperId]
  return typeof score === 'number' ? score : Number.NEGATIVE_INFINITY
}

const dotProduct = (left, right) => {
  let total = 0
  for (let index = 0; index < left.length; index += 1) {
    total += left[index] * right[index]
  }
  return total
}

const ensureEmbeddingsIndex = async () => {
  if (embeddingsIndex) return embeddingsIndex

  semanticStatus.value = 'loading-index'
    const response = await fetch(withBase('/arxiv-data/embeddings_index.json'))
  if (!response.ok) {
    throw new Error('Embedding index is not available yet')
  }

  embeddingsIndex = await response.json()
  return embeddingsIndex
}

const ensureSemanticExtractor = async () => {
  if (semanticExtractorPromise) return semanticExtractorPromise

  semanticStatus.value = 'loading-model'
  semanticExtractorPromise = (async () => {
    const { env, pipeline } = await import('@xenova/transformers')
    env.allowLocalModels = false
    env.useBrowserCache = true
    return pipeline('feature-extraction', 'Xenova/all-MiniLM-L6-v2')
  })()

  return semanticExtractorPromise
}

const clearSemanticSearch = () => {
  semanticQuery.value = ''
  selectedEmbeddingTheme.value = ''
  selectedSimilarPaperId.value = ''
  selectedSimilarPaperTitle.value = ''
  semanticScores.value = {}
  semanticError.value = ''
  semanticStatus.value = 'idle'
}

const activateEmbeddingTheme = async (themeId) => {
  try {
    const index = await ensureEmbeddingsIndex()
    selectedEmbeddingTheme.value = themeId
    semanticQuery.value = ''
    semanticError.value = ''
    semanticScores.value = Object.fromEntries(
      (index.papers || []).map((paper) => [paper.id, Number(paper.theme_scores?.[themeId] ?? Number.NEGATIVE_INFINITY)])
    )
    semanticStatus.value = 'ready'
  } catch (error) {
    console.error('Failed to activate embedding theme:', error)
    semanticError.value = error.message || 'Embedding theme ranking failed'
    semanticStatus.value = 'error'
  }
}

const activateSimilarPapers = async (paper) => {
  try {
    const index = await ensureEmbeddingsIndex()
    const sourcePaper = (index.papers || []).find((item) => item.id === paper.id)
    if (!sourcePaper?.vector) {
      throw new Error('Embedding vector is missing for this paper')
    }

    semanticQuery.value = ''
    selectedEmbeddingTheme.value = ''
    selectedSimilarPaperId.value = paper.id
    selectedSimilarPaperTitle.value = paper.title
    semanticError.value = ''

    semanticScores.value = Object.fromEntries(
      (index.papers || []).map((item) => [
        item.id,
        item.id === paper.id ? Number.NEGATIVE_INFINITY : dotProduct(sourcePaper.vector, item.vector || []),
      ])
    )
    semanticStatus.value = 'ready'
  } catch (error) {
    console.error('Similar paper ranking failed:', error)
    semanticError.value = error.message || 'Similar paper ranking failed'
    semanticStatus.value = 'error'
  }
}

const runSemanticSearch = async () => {
  const query = semanticQuery.value.trim()
  if (!query) {
    clearSemanticSearch()
    return
  }

  try {
    const [index, extractor] = await Promise.all([
      ensureEmbeddingsIndex(),
      ensureSemanticExtractor(),
    ])

    semanticStatus.value = 'searching'
    semanticError.value = ''
    selectedEmbeddingTheme.value = ''

    const output = await extractor(query, { pooling: 'mean', normalize: true })
    const queryVector = output.tolist()[0]
    semanticScores.value = Object.fromEntries(
      (index.papers || []).map((paper) => [paper.id, dotProduct(queryVector, paper.vector || [])])
    )
    semanticStatus.value = 'ready'
  } catch (error) {
    console.error('Semantic search failed:', error)
    semanticError.value = error.message || 'Semantic search failed'
    semanticStatus.value = 'error'
  }
}

const filteredPapers = computed(() => {
  const query = searchQuery.value.trim().toLowerCase()

  const papers = allPapers.value.filter((paper) => {
    if (!paperMatchesQuickFilter(paper)) return false
    if (selectedSimilarPaperId.value && paper.id === selectedSimilarPaperId.value) return false
    if (query && !paperSearchText(paper).includes(query)) return false
    if (selectedCategory.value && !paper.categories?.includes(selectedCategory.value)) return false

    if (selectedAffiliation.value) {
      const affiliationQuery = selectedAffiliation.value.trim().toLowerCase()
      const affiliations = paperAffiliations(paper)
      if (!affiliations.some((affiliation) => affiliation.toLowerCase().includes(affiliationQuery))) {
        return false
      }
    }

    if (selectedTags.value.length > 0 && !selectedTags.value.every((tag) => paper.tags?.includes(tag))) {
      return false
    }

    if (selectedDate.value && String(paper.published_date || '').slice(0, 10) !== selectedDate.value) {
      return false
    }

    return true
  })

  if (!semanticSearchActive.value) {
    return sortPapers(papers)
  }

  const ranked = [...papers]
    .map((paper) => ({ paper, score: scoreForPaper(paper.id) }))
    .filter((entry) => Number.isFinite(entry.score))
    .sort((left, right) => {
      if (right.score !== left.score) return right.score - left.score
      return fallbackSort(left.paper, right.paper)
    })
    .map((entry) => entry.paper)

  if (semanticQuery.value.trim()) {
    return ranked.slice(0, 120)
  }

  return ranked
})

const visiblePapers = computed(() => filteredPapers.value.slice(0, visibleCount.value))
const canLoadMore = computed(() => visibleCount.value < filteredPapers.value.length)
const visiblePaperRows = computed(() => {
  return visiblePapers.value.map((paper, index) => ({
    paper,
    rank: semanticSearchActive.value ? index + 1 : null,
    score: semanticSearchActive.value ? scoreForPaper(paper.id) : null,
    highlightLevel: !semanticSearchActive.value
      ? 'none'
      : index < 3
        ? 'strong'
        : index < 10
          ? 'medium'
          : 'soft',
  }))
})

const loadPapers = async () => {
  try {
    loading.value = true
    const response = await fetch(withBase('/arxiv-data/papers.json'))
    const data = await response.json()

    allPapers.value = data.papers || []

    const categorySet = new Set()
    const tagSet = new Set()
    const affiliationCounts = new Map()

    allPapers.value.forEach((paper) => {
      ;(paper.categories || []).forEach((category) => categorySet.add(category))
      ;(paper.tags || []).forEach((tag) => tagSet.add(tag))
      paperAffiliations(paper).forEach((affiliation) => {
        affiliationCounts.set(affiliation, (affiliationCounts.get(affiliation) || 0) + 1)
      })
    })

    categories.value = Array.from(categorySet).sort((left, right) => {
      const leftLabel = getCategoryName(left)
      const rightLabel = getCategoryName(right)
      return leftLabel.localeCompare(rightLabel)
    })

    allTags.value = Array.from(tagSet).sort((left, right) => {
      const leftIndex = preferredTagOrder.indexOf(left)
      const rightIndex = preferredTagOrder.indexOf(right)

      if (leftIndex !== -1 || rightIndex !== -1) {
        return (leftIndex === -1 ? preferredTagOrder.length : leftIndex) - (rightIndex === -1 ? preferredTagOrder.length : rightIndex)
      }

      return left.localeCompare(right)
    })

    allAffiliations.value = Array.from(affiliationCounts.entries())
      .sort((left, right) => {
        if (right[1] !== left[1]) return right[1] - left[1]
        return left[0].localeCompare(right[0])
      })
      .map(([affiliation]) => affiliation)
  } catch (error) {
    console.error('Failed to load papers:', error)
  } finally {
    loading.value = false
  }
}

const toggleTag = (tag) => {
  const index = selectedTags.value.indexOf(tag)
  if (index === -1) {
    selectedTags.value.push(tag)
  } else {
    selectedTags.value.splice(index, 1)
  }
}

const onDateFilter = (date) => {
  selectedDate.value = date
}

const applyAffiliationFilter = (affiliation) => {
  selectedAffiliation.value = affiliation
}

const resetFilters = () => {
  searchQuery.value = ''
  selectedCategory.value = ''
  selectedTags.value = []
  selectedAffiliation.value = ''
  selectedDate.value = ''
  selectedQuickFilter.value = 'focused'
  sortMode.value = 'focus'
  clearSemanticSearch()
}

const loadMore = () => {
  visibleCount.value += 24
}

watch(filteredPapers, () => {
  visibleCount.value = 24
})

onMounted(() => {
  loadPapers()
})
</script>

<style scoped>
:global(.VPDoc.has-sidebar .content-container) {
  max-width: 1500px;
}

.papers-list {
  padding: 1rem 0 2rem;
}

.papers-layout {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 430px;
  gap: 1.5rem;
  align-items: start;
}

.papers-main {
  min-width: 0;
}

.papers-sidebar {
  min-width: 0;
}

.sticky-panel {
  position: sticky;
  top: calc(var(--vp-nav-height, 64px) + 24px);
}

.sidebar-panel {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.sidebar-block,
.list-intro {
  padding: 1.25rem;
  border: 1px solid #dbe3f0;
  border-radius: 1rem;
  background:
    radial-gradient(circle at top right, rgba(59, 130, 246, 0.1), transparent 35%),
    linear-gradient(135deg, #ffffff 0%, #f8fbff 100%);
}

.sidebar-heading h3,
.list-title {
  margin: 0;
  color: #111827;
}

.sidebar-heading p {
  margin: 0.45rem 0 0;
  color: #6b7280;
  line-height: 1.6;
  font-size: 0.9rem;
}

.sidebar-heading.compact p {
  display: none;
}

.eyebrow {
  margin: 0 0 0.35rem;
  font-size: 0.75rem;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: #2563eb;
  font-weight: 700;
}

.list-intro {
  display: flex;
  justify-content: space-between;
  gap: 1.5rem;
  align-items: flex-start;
  margin-bottom: 1rem;
}

.list-title {
  font-size: 1.6rem;
  line-height: 1.2;
}

.list-description {
  margin: 0.6rem 0 0;
  max-width: 56rem;
  color: #4b5563;
  line-height: 1.7;
}

.list-stats {
  display: flex;
  gap: 0.75rem;
  flex-wrap: wrap;
  justify-content: flex-end;
}

.stat-pill {
  min-width: 120px;
  padding: 0.85rem 1rem;
  border-radius: 0.9rem;
  background: #eff6ff;
  border: 1px solid #bfdbfe;
  display: flex;
  flex-direction: column;
  align-items: flex-start;
}

.stat-pill.secondary {
  background: #f9fafb;
  border-color: #e5e7eb;
}

.stat-pill strong {
  font-size: 1.2rem;
  color: #1d4ed8;
}

.stat-pill.secondary strong {
  color: #111827;
}

.stat-pill span {
  font-size: 0.75rem;
  color: #6b7280;
}

.results-meta {
  display: flex;
  justify-content: space-between;
  gap: 0.75rem;
  flex-wrap: wrap;
  margin-bottom: 1rem;
  color: #6b7280;
  font-size: 0.9rem;
}

.quick-filters {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 0.65rem;
  margin-top: 0.95rem;
}

.quick-filter-btn {
  min-height: 96px;
  padding: 0.75rem 0.85rem;
  border-radius: 0.85rem;
  border: 1px solid #d1d5db;
  background: white;
  text-align: left;
  cursor: pointer;
  transition: all 0.2s ease;
}

.quick-filter-btn span {
  display: block;
  font-weight: 700;
  color: #111827;
}

.quick-filter-btn small {
  display: block;
  margin-top: 0.25rem;
  color: #6b7280;
  line-height: 1.4;
}

.quick-filter-btn:hover {
  border-color: #93c5fd;
  transform: translateY(-1px);
  box-shadow: 0 8px 20px rgba(15, 23, 42, 0.06);
}

.quick-filter-btn.active {
  border-color: #2563eb;
  background: linear-gradient(135deg, #eff6ff 0%, #dbeafe 100%);
}

.search-stack {
  display: flex;
  flex-direction: column;
  gap: 0.8rem;
  margin-top: 0.85rem;
}

.semantic-actions {
  display: flex;
  gap: 0.6rem;
}

.semantic-btn {
  flex: 1;
  padding: 0.72rem 0.9rem;
  border-radius: 0.75rem;
  border: 1px solid #d1d5db;
  background: white;
  color: #374151;
  cursor: pointer;
  font-weight: 700;
  transition: all 0.2s ease;
}

.semantic-btn.primary {
  background: #2563eb;
  border-color: #2563eb;
  color: white;
}

.semantic-btn:hover {
  border-color: #60a5fa;
}

.semantic-btn.primary:hover {
  background: #1d4ed8;
}

.semantic-status {
  border-radius: 0.75rem;
  padding: 0.75rem 0.9rem;
  font-size: 0.85rem;
  line-height: 1.5;
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  color: #475569;
}

.semantic-status.loading {
  background: #eff6ff;
  border-color: #bfdbfe;
  color: #1d4ed8;
}

.semantic-status.ready {
  background: #ecfeff;
  border-color: #a5f3fc;
  color: #155e75;
}

.semantic-status.error {
  background: #fef2f2;
  border-color: #fecaca;
  color: #b91c1c;
}

.semantic-theme-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 0.65rem;
}

.semantic-theme-btn {
  min-height: 86px;
  padding: 0.75rem 0.8rem;
  border-radius: 0.85rem;
  border: 1px solid #d1d5db;
  background: white;
  text-align: left;
  cursor: pointer;
  transition: all 0.2s ease;
}

.semantic-theme-btn span {
  display: block;
  font-weight: 700;
  color: #111827;
}

.semantic-theme-btn small {
  display: block;
  margin-top: 0.3rem;
  color: #6b7280;
  line-height: 1.4;
}

.semantic-theme-btn.active,
.semantic-theme-btn:hover {
  border-color: #2563eb;
  background: linear-gradient(135deg, #eff6ff 0%, #dbeafe 100%);
}

.affiliation-filter-wrap {
  width: 100%;
}

.search-input {
  width: 100%;
  padding: 0.75rem 1rem;
  border: 1px solid #d1d5db;
  border-radius: 0.75rem;
  font-size: 0.95rem;
}

.search-input:focus,
.filter-select:focus {
  outline: none;
  border-color: var(--vp-c-brand-1);
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.12);
}

.filter-select {
  width: 100%;
  padding: 0.75rem 0.95rem;
  border: 1px solid #d1d5db;
  border-radius: 0.75rem;
  background: white;
  font-size: 0.9rem;
  cursor: pointer;
}

.tags-filter {
  display: flex;
  gap: 0.45rem;
  flex-wrap: wrap;
  margin-top: 0.85rem;
}

.tag-filter-btn,
.reset-btn {
  padding: 0.45rem 0.8rem;
  border-radius: 999px;
  border: 1px solid #d1d5db;
  background: white;
  color: #374151;
  cursor: pointer;
  transition: all 0.2s ease;
}

.tag-filter-btn:hover,
.reset-btn:hover {
  border-color: #93c5fd;
  background: #eff6ff;
}

.tag-filter-btn.active {
  background: #2563eb;
  color: white;
  border-color: #2563eb;
}

.reset-btn {
  width: 100%;
  background: #f9fafb;
  font-weight: 600;
}

.papers-feed {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.loading-indicator,
.no-results {
  text-align: center;
  padding: 3rem 1rem;
  color: #6b7280;
}

.load-more-wrap {
  display: flex;
  justify-content: center;
  margin-top: 1.5rem;
}

.load-more-btn {
  padding: 0.8rem 1.4rem;
  border: 1px solid #cbd5e1;
  border-radius: 999px;
  background: white;
  color: #1f2937;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.2s ease;
}

.load-more-btn:hover {
  border-color: #60a5fa;
  color: #1d4ed8;
}

.no-results-icon {
  font-size: 3rem;
  margin-bottom: 0.8rem;
}

@media (max-width: 1100px) {
  .papers-layout {
    grid-template-columns: 1fr;
  }

  .sticky-panel {
    position: static;
  }

  .quick-filters {
    grid-template-columns: 1fr;
  }

  .semantic-theme-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .list-intro {
    flex-direction: column;
  }

  .list-stats {
    width: 100%;
    justify-content: flex-start;
  }
}
</style>
