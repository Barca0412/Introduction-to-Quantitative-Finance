<template>
  <div class="paper-card" :class="cardClasses">
    <div v-if="semanticActive && semanticScoreDisplay" class="semantic-row">
      <span class="semantic-chip rank">#{{ semanticRank }}</span>
      <span class="semantic-chip score">Semantic {{ semanticScoreDisplay }}</span>
      <span v-if="highlightLevel === 'strong'" class="semantic-chip accent">Top match</span>
      <span v-else-if="highlightLevel === 'medium'" class="semantic-chip accent soft">Strong match</span>
    </div>

    <div v-if="paper.focus?.is_focus" class="paper-focus-row">
      <span class="focus-badge primary">Focus {{ paper.focus?.score || 0 }}</span>
      <span v-for="label in focusLabels" :key="label" class="focus-badge">
        {{ label }}
      </span>
    </div>

    <h3 class="paper-title">
      <a :href="paper.abs_link" target="_blank" rel="noopener">{{ paper.title }}</a>
    </h3>

    <div class="paper-meta">
      <span class="paper-authors">{{ authorNames }}</span>
      <span class="paper-date">{{ paper.published_date }}</span>
      <div v-if="affiliations.length > 0" class="paper-affiliation">
        <button
          v-for="aff in affiliations"
          :key="aff"
          type="button"
          class="affiliation-tag"
          @click="$emit('filter-affiliation', aff)"
        >
          {{ aff }}
        </button>
      </div>
      <span v-if="paper.tags && paper.tags.length > 0" class="paper-tag-count">
        {{ paper.tags.length }} tags
      </span>
    </div>

    <p v-if="paper.focus?.reasons?.length" class="paper-focus-notes">
      {{ paper.focus.reasons.join(' • ') }}
    </p>

    <div class="paper-tags">
      <span v-for="cat in paper.categories" :key="cat" class="category-tag">
        {{ cat }}
      </span>
      <button
        v-for="tag in paper.tags"
        :key="tag"
        type="button"
        class="research-tag"
        @click="$emit('filter-tag', tag)"
      >
        {{ tag }}
      </button>
    </div>

    <p class="paper-abstract">{{ paper.abstract }}</p>

    <div v-if="paper.summary_zh" class="paper-summary-zh">
      <div class="summary-label">Chinese Summary</div>
      <div class="summary-text">{{ paper.summary_zh }}</div>
    </div>

    <div v-if="paper.keywords && paper.keywords.length" class="paper-keywords">
      <div class="keywords-label">Keywords</div>
      <div class="keywords-list">
        <span v-for="kw in paper.keywords" :key="kw" class="keyword">
          {{ kw }}
        </span>
      </div>
    </div>

    <div class="paper-links">
      <button type="button" class="paper-link similar" @click="$emit('find-similar', paper)">
        <IconWrapper name="sparkles" :size="16" />
        Similar papers
      </button>
      <a :href="paper.pdf_link" target="_blank" rel="noopener" class="paper-link primary">
        <IconWrapper name="file-text" :size="16" />
        PDF
      </a>
      <a :href="paper.abs_link" target="_blank" rel="noopener" class="paper-link secondary">
        <IconWrapper name="external-link" :size="16" />
        arXiv
      </a>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

import IconWrapper from './IconWrapper.vue'

const props = defineProps({
  paper: {
    type: Object,
    required: true
  },
  semanticActive: {
    type: Boolean,
    default: false
  },
  semanticRank: {
    type: Number,
    default: null
  },
  semanticScore: {
    type: Number,
    default: null
  },
  highlightLevel: {
    type: String,
    default: 'none'
  }
})

defineEmits(['filter-tag', 'filter-affiliation', 'find-similar'])

const authorNames = computed(() => {
  const authors = props.paper.authors || []
  if (authors.length === 0) return 'Unknown Authors'
  if (authors.length <= 3) {
    return authors.map((author) => author.name).join(', ')
  }
  return `${authors.slice(0, 3).map((author) => author.name).join(', ')} et al.`
})

const affiliations = computed(() => {
  const values = Array.isArray(props.paper.affiliations) && props.paper.affiliations.length > 0
    ? props.paper.affiliations
    : String(props.paper.affiliation || '')
        .split(/[;；]+/)
        .map((value) => value.trim())

  return values
    .filter((value) => value.length > 0 && value !== 'Unknown')
    .slice(0, 4)
})

const focusLabels = computed(() => props.paper.focus?.labels || [])

const semanticScoreDisplay = computed(() => {
  if (!props.semanticActive || typeof props.semanticScore !== 'number' || !Number.isFinite(props.semanticScore)) {
    return ''
  }
  return `${(props.semanticScore * 100).toFixed(1)}%`
})

const cardClasses = computed(() => {
  return {
    'semantic-active': props.semanticActive,
    'semantic-strong': props.semanticActive && props.highlightLevel === 'strong',
    'semantic-medium': props.semanticActive && props.highlightLevel === 'medium',
    'semantic-soft': props.semanticActive && props.highlightLevel === 'soft'
  }
})
</script>

<style scoped>
.paper-card {
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 1rem;
  padding: 1.4rem;
  margin-bottom: 1rem;
  box-shadow: 0 8px 30px rgba(15, 23, 42, 0.04);
  transition: border-color 0.2s ease, box-shadow 0.2s ease, transform 0.2s ease;
}

.paper-card.semantic-active {
  border-color: #bfdbfe;
}

.paper-card.semantic-strong {
  border-color: #2563eb;
  box-shadow: 0 16px 34px rgba(37, 99, 235, 0.16);
  background: linear-gradient(180deg, #ffffff 0%, #f8fbff 100%);
}

.paper-card.semantic-medium {
  border-color: #93c5fd;
  box-shadow: 0 12px 28px rgba(59, 130, 246, 0.1);
}

.paper-card.semantic-soft {
  border-color: #dbeafe;
}

.semantic-row {
  display: flex;
  gap: 0.45rem;
  flex-wrap: wrap;
  margin-bottom: 0.75rem;
}

.semantic-chip {
  display: inline-flex;
  align-items: center;
  padding: 0.22rem 0.6rem;
  border-radius: 999px;
  font-size: 0.72rem;
  font-weight: 700;
  background: #eff6ff;
  color: #1d4ed8;
}

.semantic-chip.rank {
  background: #dbeafe;
}

.semantic-chip.score {
  background: #ecfeff;
  color: #155e75;
}

.semantic-chip.accent {
  background: #d1fae5;
  color: #065f46;
}

.semantic-chip.accent.soft {
  background: #fef3c7;
  color: #92400e;
}

.paper-focus-row {
  display: flex;
  flex-wrap: wrap;
  gap: 0.45rem;
  margin-bottom: 0.75rem;
}

.focus-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.25rem;
  padding: 0.22rem 0.6rem;
  border-radius: 999px;
  background: #f3f4f6;
  color: #374151;
  font-size: 0.72rem;
  font-weight: 700;
}

.focus-badge.primary {
  background: #dbeafe;
  color: #1d4ed8;
}

.paper-title {
  font-size: 1.2rem;
  font-weight: 700;
  margin: 0 0 0.75rem;
  line-height: 1.45;
}

.paper-title a {
  color: #111827;
  text-decoration: none;
}

.paper-title a:hover {
  color: var(--vp-c-brand-1);
}

.paper-meta {
  display: flex;
  gap: 0.8rem;
  align-items: center;
  margin-bottom: 0.75rem;
  font-size: 0.875rem;
  color: #6b7280;
  flex-wrap: wrap;
}

.paper-authors {
  font-weight: 600;
  color: #374151;
}

.paper-date {
  color: #9ca3af;
}

.paper-affiliation {
  display: flex;
  gap: 0.45rem;
  flex-wrap: wrap;
}

.affiliation-tag {
  border: none;
  background: #eef2ff;
  color: #4338ca;
  padding: 0.18rem 0.55rem;
  border-radius: 0.45rem;
  font-size: 0.72rem;
  font-weight: 600;
  cursor: pointer;
  transition: background-color 0.2s ease;
}

.affiliation-tag:hover {
  background: #dbeafe;
}

.paper-tag-count {
  background: #eff6ff;
  color: #1d4ed8;
  padding: 0.18rem 0.55rem;
  border-radius: 0.45rem;
  font-size: 0.72rem;
  font-weight: 700;
}

.paper-focus-notes {
  margin: 0 0 0.8rem;
  color: #4b5563;
  font-size: 0.84rem;
}

.paper-tags {
  display: flex;
  gap: 0.45rem;
  flex-wrap: wrap;
  margin-bottom: 0.85rem;
}

.category-tag {
  background: #fef3c7;
  color: #92400e;
  padding: 0.22rem 0.6rem;
  border-radius: 999px;
  font-size: 0.72rem;
  font-weight: 700;
}

.research-tag {
  background: #dbeafe;
  color: #1e3a8a;
  padding: 0.22rem 0.6rem;
  border: none;
  border-radius: 999px;
  font-size: 0.72rem;
  font-weight: 700;
  cursor: pointer;
  transition: background-color 0.2s ease;
}

.research-tag:hover {
  background: #bfdbfe;
}

.paper-abstract {
  color: #4b5563;
  line-height: 1.7;
  margin: 0 0 1rem;
  display: -webkit-box;
  -webkit-line-clamp: 4;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.paper-summary-zh {
  background: #f9fafb;
  border-left: 3px solid #3b82f6;
  padding: 0.85rem 1rem;
  margin-bottom: 1rem;
  border-radius: 0 0.5rem 0.5rem 0;
}

.summary-label,
.keywords-label {
  font-size: 0.75rem;
  font-weight: 700;
  color: #6b7280;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin-bottom: 0.35rem;
}

.summary-text {
  color: #374151;
  font-size: 0.92rem;
  line-height: 1.7;
}

.paper-keywords {
  margin-bottom: 1rem;
}

.keywords-list {
  display: flex;
  gap: 0.4rem;
  flex-wrap: wrap;
}

.keyword {
  background: #f3f4f6;
  color: #4b5563;
  padding: 0.18rem 0.5rem;
  border-radius: 0.35rem;
  font-size: 0.74rem;
}

.paper-links {
  display: flex;
  gap: 0.75rem;
}

.paper-link {
  border: none;
  display: inline-flex;
  align-items: center;
  gap: 0.375rem;
  padding: 0.55rem 0.95rem;
  border-radius: 0.65rem;
  font-size: 0.875rem;
  font-weight: 600;
  text-decoration: none;
  transition: all 0.2s ease;
  cursor: pointer;
}

.paper-link.similar {
  background: #eef2ff;
  color: #4338ca;
}

.paper-link.similar:hover {
  background: #e0e7ff;
}

.paper-link.primary {
  background-color: #2563eb;
  color: white;
}

.paper-link.primary:hover {
  background-color: #1d4ed8;
}

.paper-link.secondary {
  background-color: white;
  border: 1px solid #d1d5db;
  color: #374151;
}

.paper-link.secondary:hover {
  border-color: #60a5fa;
  color: #2563eb;
}
</style>
