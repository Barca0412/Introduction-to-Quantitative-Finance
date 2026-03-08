# Research Trends

<script setup>
import { onMounted, ref } from 'vue'
import { withBase } from 'vitepress'

const stats = ref(null)
const loading = ref(true)

const loadStats = async () => {
  try {
    loading.value = true
    const response = await fetch(withBase('/arxiv-data/stats.json'))
    stats.value = await response.json()
  } catch (error) {
    console.error('Failed to load stats:', error)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadStats()
})
</script>

<div v-if="loading" class="loading-indicator">
  Loading trends...
</div>

<div v-else-if="stats">
  <p class="page-lead">
    Start with <strong>Focus Topics</strong> to track the tags most aligned with AI + Finance,
    agent planning, and deep research. Switch to <strong>Top Overall</strong> when you want the
    broader signal from all monitored tags or keywords.
  </p>

  <TrendsChart :stats="stats" />

  <div class="trends-info">
    <h2>How to read this chart</h2>
    <ul>
      <li><strong>Tags:</strong> LLM-assigned research categories such as <code>ai-finance</code>, <code>agent-planning</code>, and <code>deep-research</code>.</li>
      <li><strong>Keywords:</strong> High-signal technical phrases extracted per paper.</li>
      <li><strong>Daily:</strong> How many papers matched the topic on each publication date.</li>
      <li><strong>Cumulative:</strong> Running total to show whether a topic is compounding over time.</li>
    </ul>
  </div>
</div>

<style scoped>
.page-lead {
  margin: 0 0 1rem;
  color: #475569;
  line-height: 1.8;
}

.loading-indicator {
  text-align: center;
  padding: 3rem;
  color: #6b7280;
  font-size: 1rem;
}

.trends-info {
  margin-top: 1.5rem;
  padding: 1.2rem 1.3rem;
  background: #ffffff;
  border-radius: 1rem;
  border: 1px solid #e2e8f0;
}

.trends-info h2 {
  margin-top: 0;
  font-size: 1.2rem;
}

.trends-info ul {
  margin: 0;
  padding-left: 1.1rem;
  color: #475569;
  line-height: 1.75;
}
</style>
