<script setup>
// 首页的访问统计：此刻多少人在看、多少 agent 在读，以及累计访客和 agent 数。
// 数据由服务器每分钟生成一次（scripts/site/stats/site_stats.py），只有总数，没有任何访客信息。
// 读不到、或数据超过 10 分钟没更新时，整块隐藏，不显示 0。
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import { withBase } from 'vitepress'

const MAIN = 'https://quant.hfthnu.com/site-stats.json'
const STALE_MS = 10 * 60 * 1000
const stats = ref(null)
let timer = null

const fmt = (n) => Number(n).toLocaleString('zh-CN')
const online = computed(() => stats.value?.online || {})
const total = computed(() => stats.value?.total || {})

async function load() {
  try {
    // 主站读自己域名下的文件；GitHub Pages 镜像跨域读主站（服务器已允许）
    const url = location.hostname.endsWith('github.io') ? MAIN : withBase('/site-stats.json')
    const res = await fetch(url, { cache: 'no-store' })
    if (!res.ok) throw new Error(String(res.status))
    const data = await res.json()
    const age = Date.now() - Date.parse(data.updated_at)
    stats.value = Number.isFinite(age) && age < STALE_MS ? data : null
  } catch {
    stats.value = null
  }
}

onMounted(() => {
  load()
  timer = setInterval(load, 60 * 1000)
})
onBeforeUnmount(() => clearInterval(timer))
</script>

<template>
  <div v-if="stats" class="live-stats" aria-live="off">
    <p class="live-now">
      <i class="live-dot" aria-hidden="true"></i>
      <template v-if="online.humans != null">此刻 <span class="num">{{ fmt(online.humans) }}</span> 人在看 · </template>
      <span class="num">{{ fmt(online.agents || 0) }}</span> 个 agent 正在读
    </p>
    <p class="live-total">
      累计&nbsp;<template v-if="total.visitors != null"><span class="num">{{ fmt(total.visitors) }}</span> 位访客 · </template>
      <span class="num">{{ fmt(total.agent_requests || 0) }}</span> 个 agent
    </p>
  </div>
</template>

<style scoped>
.live-stats { margin-block-start: 20px; color: var(--muted); font-size: var(--step-small); line-height: 1.7; max-inline-size: 26em; }
.live-now { display: flex; align-items: center; flex-wrap: wrap; gap: 0 4px; color: var(--ink); }
.live-dot { inline-size: 8px; block-size: 8px; border-radius: 50%; background: var(--accent); border: 1.5px solid var(--ink); margin-inline-end: 4px; flex: none; }
.num { font-variant-numeric: tabular-nums; }
</style>
