<template>
  <div class="trends-chart">
    <div class="chart-toolbar">
      <div class="toolbar-block">
        <span class="toolbar-label">Metric</span>
        <div class="toolbar-buttons">
          <button
            v-for="option in metricOptions"
            :key="option.id"
            :class="['chart-toggle-btn', { active: chartType === option.id }]"
            @click="chartType = option.id"
          >
            {{ option.label }}
          </button>
        </div>
      </div>

      <div class="toolbar-block">
        <span class="toolbar-label">Window</span>
        <div class="toolbar-buttons">
          <button
            v-for="option in modeOptions"
            :key="option.id"
            :class="['chart-toggle-btn', { active: chartMode === option.id }]"
            @click="chartMode = option.id"
          >
            {{ option.label }}
          </button>
        </div>
      </div>

      <div v-if="chartType === 'tags'" class="toolbar-block">
        <span class="toolbar-label">Scope</span>
        <div class="toolbar-buttons">
          <button
            v-for="option in scopeOptions"
            :key="option.id"
            :class="['chart-toggle-btn', { active: chartScope === option.id }]"
            @click="chartScope = option.id"
          >
            {{ option.label }}
          </button>
        </div>
      </div>
    </div>

    <div class="chart-summary">
      <div>
        <strong>{{ selectedSeriesKeys.length }}</strong>
        <span>series visible</span>
      </div>
      <div v-if="stats.summary?.tag_days">
        <strong>{{ stats.summary.tag_days }}</strong>
        <span>tracked days</span>
      </div>
      <div v-if="stats.last_updated">
        <strong>{{ formatLastUpdated(stats.last_updated) }}</strong>
        <span>last updated</span>
      </div>
    </div>

    <div ref="chartContainer" class="chart-container"></div>
  </div>
</template>

<script setup>
import { computed, nextTick, onMounted, onUnmounted, ref, watch } from 'vue'
import * as echarts from 'echarts'

const props = defineProps({
  stats: {
    type: Object,
    required: true
  }
})

const focusTagOrder = [
  'ai-finance',
  'agent-planning',
  'deep-research',
  'multi-agent',
  'tool-use',
  'reasoning',
  'memory',
  'rag',
  'time-series'
]

const chartContainer = ref(null)
const chartType = ref('tags')
const chartMode = ref('daily')
const chartScope = ref('focus')
const metricOptions = [
  { id: 'tags', label: 'Tags' },
  { id: 'keywords', label: 'Keywords' }
]
const modeOptions = [
  { id: 'daily', label: 'Daily' },
  { id: 'cumulative', label: 'Cumulative' }
]
const scopeOptions = [
  { id: 'focus', label: 'Focus Topics' },
  { id: 'all', label: 'Top Overall' }
]

let chart = null
let resizeHandler = null

const colors = ['#2563eb', '#0891b2', '#0f766e', '#dc2626', '#7c3aed', '#ea580c', '#4f46e5', '#65a30d', '#db2777', '#475569']

const statsBucket = computed(() => {
  if (chartType.value === 'tags') {
    return props.stats?.tag_stats?._all || {}
  }
  return props.stats?.keyword_stats?._all || {}
})

const seriesEntries = computed(() => statsBucket.value?.[chartMode.value] || [])

const selectedSeriesKeys = computed(() => {
  const cumulative = statsBucket.value?.cumulative || []
  const latestCounts = cumulative[cumulative.length - 1]?.counts || {}

  if (chartType.value === 'tags' && chartScope.value === 'focus') {
    return focusTagOrder.filter((tag) => (latestCounts[tag] || 0) > 0)
  }

  return Object.entries(latestCounts)
    .sort((left, right) => right[1] - left[1])
    .slice(0, 10)
    .map(([key]) => key)
})

const formatLastUpdated = (value) => {
  return new Date(value).toLocaleString('en-US', {
    month: 'short',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const titleForChart = () => {
  const metricLabel = chartType.value === 'tags' ? 'Research Tags' : 'Keywords'
  const modeLabel = chartMode.value === 'daily' ? 'Daily Count' : 'Cumulative Count'
  const scopeLabel = chartType.value === 'tags' && chartScope.value === 'focus' ? 'Focused Topics' : 'Top Trends'
  return `${metricLabel} - ${modeLabel} (${scopeLabel})`
}

const buildSeries = () => {
  const keys = selectedSeriesKeys.value
  return keys.map((key, index) => ({
    name: key,
    type: 'line',
    smooth: true,
    showSymbol: false,
    emphasis: { focus: 'series' },
    lineStyle: {
      width: 2,
      color: colors[index % colors.length]
    },
    itemStyle: {
      color: colors[index % colors.length]
    },
    data: seriesEntries.value.map((entry) => entry.counts?.[key] || 0)
  }))
}

const updateChart = () => {
  if (!chart || !chartContainer.value) return

  const dates = seriesEntries.value.map((entry) => entry.date)
  const series = buildSeries()

  if (dates.length === 0 || series.length === 0) {
    chart.setOption({
      title: {
        text: 'No trend data available yet',
        left: 'center',
        top: 'middle',
        textStyle: { color: '#6b7280', fontSize: 16 }
      },
      xAxis: { show: false },
      yAxis: { show: false },
      series: []
    }, true)
    return
  }

  chart.setOption({
    color: colors,
    title: {
      text: titleForChart(),
      left: 'center',
      textStyle: {
        fontSize: 16,
        fontWeight: 700,
        color: '#0f172a'
      }
    },
    tooltip: {
      trigger: 'axis',
      backgroundColor: 'rgba(15, 23, 42, 0.92)',
      borderWidth: 0,
      textStyle: { color: '#f8fafc' },
      formatter: (params) => {
        const rows = params
          .map((item) => `${item.marker} ${item.seriesName}: ${item.value}`)
          .join('<br/>')
        return `<strong>${params[0]?.axisValue || ''}</strong><br/>${rows}`
      }
    },
    legend: {
      type: 'scroll',
      top: 36,
      left: 20,
      right: 20
    },
    grid: {
      left: 48,
      right: 24,
      top: 96,
      bottom: 72
    },
    xAxis: {
      type: 'category',
      data: dates,
      axisLabel: {
        color: '#64748b',
        rotate: dates.length > 6 ? 35 : 0
      },
      axisLine: {
        lineStyle: { color: '#cbd5e1' }
      }
    },
    yAxis: {
      type: 'value',
      minInterval: 1,
      axisLabel: {
        color: '#64748b'
      },
      splitLine: {
        lineStyle: {
          color: '#e2e8f0'
        }
      }
    },
    dataZoom: [
      { type: 'inside', start: 0, end: 100 },
      { type: 'slider', start: dates.length > 10 ? 35 : 0, end: 100, bottom: 20 }
    ],
    series
  }, true)
}

watch(
  [chartType, chartMode, chartScope, () => props.stats],
  async () => {
    await nextTick()
    updateChart()
  },
  { deep: true }
)

onMounted(async () => {
  await nextTick()
  if (!chartContainer.value) return
  chart = echarts.init(chartContainer.value)
  resizeHandler = () => chart?.resize()
  window.addEventListener('resize', resizeHandler)
  updateChart()
})

onUnmounted(() => {
  if (resizeHandler) {
    window.removeEventListener('resize', resizeHandler)
  }
  chart?.dispose()
  chart = null
})
</script>

<style scoped>
.trends-chart {
  padding: 1rem 0;
}

.chart-toolbar {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 0.9rem;
  margin-bottom: 1rem;
}

.toolbar-block {
  padding: 0.9rem 1rem;
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 0.9rem;
}

.toolbar-label {
  display: block;
  margin-bottom: 0.55rem;
  font-size: 0.75rem;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: #64748b;
  font-weight: 700;
}

.toolbar-buttons {
  display: flex;
  gap: 0.45rem;
  flex-wrap: wrap;
}

.chart-toggle-btn {
  padding: 0.5rem 0.85rem;
  border: 1px solid #d1d5db;
  border-radius: 999px;
  background: white;
  cursor: pointer;
  font-size: 0.82rem;
  font-weight: 600;
  transition: all 0.2s ease;
}

.chart-toggle-btn:hover {
  border-color: #60a5fa;
}

.chart-toggle-btn.active {
  background-color: #2563eb;
  color: white;
  border-color: #2563eb;
}

.chart-summary {
  display: flex;
  gap: 0.75rem;
  flex-wrap: wrap;
  margin-bottom: 1rem;
}

.chart-summary div {
  min-width: 120px;
  padding: 0.75rem 0.9rem;
  border-radius: 0.8rem;
  border: 1px solid #e2e8f0;
  background: white;
}

.chart-summary strong {
  display: block;
  color: #0f172a;
  font-size: 1rem;
}

.chart-summary span {
  color: #64748b;
  font-size: 0.75rem;
}

.chart-container {
  width: 100%;
  min-height: 540px;
  border: 1px solid #e5e7eb;
  border-radius: 1rem;
  background: linear-gradient(180deg, #ffffff 0%, #fbfdff 100%);
  padding: 0.5rem;
}

@media (max-width: 768px) {
  .chart-container {
    min-height: 420px;
  }
}
</style>
