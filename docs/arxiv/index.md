---
layout: home
---

<script setup>
import { computed, onMounted, ref } from 'vue'
import { withBase } from 'vitepress'

const stats = ref({
  last_updated: null,
  summary: {
    total_papers: 0,
    focus_papers: 0,
    monitored_categories: 10,
    tracked_tags: 15,
    focus_tag_counts: {}
  }
})

const summary = computed(() => stats.value.summary || {})

const lanes = computed(() => {
  const counts = summary.value.focus_tag_counts || {}
  return [
    {
      title: 'AI + Finance',
      copy: 'Trading, portfolio, risk, financial NLP, and market intelligence.',
      count: counts['ai-finance'] || 0
    },
    {
      title: 'Agent Planning',
      copy: 'ReAct, workflow decomposition, tool orchestration, and long-horizon execution.',
      count: counts['agent-planning'] || 0
    },
    {
      title: 'Deep Research',
      copy: 'Research agents, literature synthesis, evidence gathering, and survey automation.',
      count: counts['deep-research'] || 0
    },
    {
      title: 'Agentic Building Blocks',
      copy: 'Multi-agent, tool-use, reasoning, memory, and RAG patterns that support robust agents.',
      count: (counts['multi-agent'] || 0) + (counts['tool-use'] || 0) + (counts['reasoning'] || 0) + (counts['memory'] || 0)
    }
  ]
})

const loadStats = async () => {
  try {
    const response = await fetch(withBase('/arxiv-data/stats.json'))
    stats.value = await response.json()
  } catch (error) {
    console.error('Failed to load stats:', error)
  }
}

const formatDate = (dateStr) => {
  if (!dateStr) return 'Unknown'
  return new Date(dateStr).toLocaleString('en-US', {
    month: 'short',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

onMounted(() => {
  loadStats()
})
</script>

<style scoped>
.hero-shell {
  position: relative;
  overflow: hidden;
  margin-top: 1.35rem;
  padding: 4rem 1.25rem 3rem;
  border-radius: 1.5rem;
  background:
    radial-gradient(circle at top right, rgba(14, 165, 233, 0.22), transparent 30%),
    radial-gradient(circle at bottom left, rgba(37, 99, 235, 0.18), transparent 32%),
    linear-gradient(135deg, #ffffff 0%, #f8fbff 45%, #eef5ff 100%);
  border: 1px solid rgba(148, 163, 184, 0.25);
}

.hero-kicker {
  display: inline-flex;
  padding: 0.35rem 0.75rem;
  border-radius: 999px;
  background: rgba(37, 99, 235, 0.1);
  color: #1d4ed8;
  font-size: 0.8rem;
  font-weight: 700;
  letter-spacing: 0.04em;
  margin-bottom: 1rem;
}

.hero-title {
  font-size: clamp(2.4rem, 6vw, 4.4rem);
  line-height: 1.02;
  margin: 0;
  color: #0f172a;
}

.hero-lead {
  max-width: 56rem;
  margin: 1rem 0 0;
  font-size: 1.15rem;
  line-height: 1.8;
  color: #475569;
}

.hero-buttons {
  display: flex;
  gap: 0.9rem;
  flex-wrap: wrap;
  margin-top: 1.75rem;
}

.hero-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  padding: 0.85rem 1.4rem;
  border-radius: 0.85rem;
  font-weight: 700;
  text-decoration: none;
  transition: transform 0.2s ease, box-shadow 0.2s ease, background-color 0.2s ease;
}

.hero-btn.primary {
  background: #2563eb;
  color: white;
  box-shadow: 0 16px 30px rgba(37, 99, 235, 0.18);
}

.hero-btn.primary:hover {
  transform: translateY(-1px);
  background: #1d4ed8;
}

.hero-btn.secondary {
  background: white;
  color: #334155;
  border: 1px solid #cbd5e1;
}

.hero-btn.secondary:hover {
  transform: translateY(-1px);
  border-color: #93c5fd;
}

.stats-grid,
.lane-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 1rem;
  margin-top: 2rem;
}

.stat-card,
.lane-card {
  border-radius: 1rem;
  padding: 1rem 1.1rem;
  background: rgba(255, 255, 255, 0.9);
  border: 1px solid rgba(203, 213, 225, 0.8);
  backdrop-filter: blur(6px);
}

.stat-value {
  font-size: 2rem;
  line-height: 1;
  font-weight: 800;
  color: #0f172a;
}

.stat-label {
  margin-top: 0.45rem;
  color: #64748b;
  font-size: 0.85rem;
}

.lane-card h3 {
  margin: 0;
  font-size: 1rem;
  color: #0f172a;
}

.lane-count {
  display: inline-flex;
  margin-top: 0.65rem;
  padding: 0.2rem 0.55rem;
  border-radius: 999px;
  background: #dbeafe;
  color: #1d4ed8;
  font-size: 0.78rem;
  font-weight: 700;
}

.lane-card p {
  margin: 0.7rem 0 0;
  color: #475569;
  line-height: 1.7;
}

.last-updated {
  margin-top: 1.5rem;
  color: #64748b;
  font-size: 0.9rem;
}
</style>

<div class="hero-shell">
  <div class="hero-kicker">Focused AI/LLM/Agent Finance Radar</div>
  <h1 class="hero-title">Track the papers that matter to your research workflow</h1>
  <p class="hero-lead">
    The arXiv radar continuously monitors 10 arXiv categories, enriches papers with tags,
    keywords, Chinese summaries, affiliations, and semantic embeddings, then publishes a static
    browsing experience under this VitePress site.
  </p>

  <div class="hero-buttons">
    <a :href="withBase('/arxiv/papers')" class="hero-btn primary">Open Focused Papers</a>
    <a :href="withBase('/arxiv/trends')" class="hero-btn secondary">Explore Trends</a>
  </div>

  <div class="stats-grid">
    <div class="stat-card">
      <div class="stat-value">{{ summary.total_papers || 0 }}</div>
      <div class="stat-label">Indexed papers</div>
    </div>
    <div class="stat-card">
      <div class="stat-value">{{ summary.focus_papers || 0 }}</div>
      <div class="stat-label">Focus-matched papers</div>
    </div>
    <div class="stat-card">
      <div class="stat-value">{{ summary.monitored_categories || 10 }}</div>
      <div class="stat-label">Monitored categories</div>
    </div>
    <div class="stat-card">
      <div class="stat-value">{{ summary.tracked_tags || 15 }}</div>
      <div class="stat-label">Tracked research tags</div>
    </div>
  </div>

  <div class="lane-grid">
    <div v-for="lane in lanes" :key="lane.title" class="lane-card">
      <h3>{{ lane.title }}</h3>
      <span class="lane-count">{{ lane.count }} tagged papers</span>
      <p>{{ lane.copy }}</p>
    </div>
  </div>

  <div v-if="stats.last_updated" class="last-updated">
    Last updated: {{ formatDate(stats.last_updated) }}
  </div>
</div>

## What This Section Optimizes For

- A broad recall layer from 10 AI and quantitative finance arXiv categories.
- A tighter focus layer that prioritizes AI + Finance, agent planning, and deep research themes.
- Fast browsing with tags, keywords, affiliations, Chinese summaries, and semantic search.

## Workflow

- Fetch recent arXiv papers from monitored categories.
- Enrich with LLM tags, keywords, Chinese summaries, and normalized affiliations.
- Compute stats, generate charts, build embeddings, and copy public JSON into `docs/public/arxiv-data`.
- Update the README status block from the generated dataset.
