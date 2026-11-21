<script setup>
// 首页的访问统计：此刻多少人在看、多少 agent 在读，以及累计访客和 agent 读取次数。
// 数据由服务器每分钟生成一次（scripts/site/stats/site_stats.py），只有总数，没有任何访客信息。
// 读不到、或数据超过 10 分钟没更新时，整块隐藏，不显示 0。
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import { withBase } from 'vitepress'

const MAIN = 'https://quant.hfthnu.com/site-stats.json'
const STALE_MS = 10 * 60 * 1000
const stats = ref(null)
let timer = null

const fmt = (n) => Number(n).toLocaleString('zh-CN')
const day = (d) => (d ? `${Number(d.slice(5, 7))} 月 ${Number(d.slice(8, 10))} 日` : '')
const online = computed(() => stats.value?.online || {})
const total = computed(() => stats.value?.total || {})
const since = computed(() => stats.value?.since || {})
const agentsTop = computed(() => (stats.value?.agents_top || []).slice(0, 5))

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
      agent 读取 <span class="num">{{ fmt(total.agent_requests || 0) }}</span> 次
    </p>
    <details class="live-how">
      <summary>怎么数的</summary>
      <p>人数来自本站自己部署的统计工具 Umami，"此刻"指最近 5 分钟内有活动的访客；已识别出的 AI 爬虫不计入。agent 指 AI 爬虫和 AI 助手，数据来自网站服务器日志，只统计在请求里自报身份的，比如 GPTBot、ClaudeBot、ChatGPT-User；伪装成普通浏览器的 agent 识别不出来。访客从 {{ day(since.visitors) }}起算，agent 从 {{ day(since.agents) }}起算。每分钟更新一次，只公开总数。</p>
      <p v-if="agentsTop.length">来过的 agent：<template v-for="([name, n], i) in agentsTop" :key="name">{{ i ? '、' : '' }}{{ name }} <span class="num">{{ fmt(n) }}</span> 次</template>。<a :href="withBase('/about#访问统计')">详细说明</a></p>
    </details>
  </div>
</template>

<style scoped>
.live-stats { margin-block-start: 20px; color: var(--muted); font-size: var(--step-small); line-height: 1.7; max-inline-size: 26em; }
.live-now { display: flex; align-items: center; flex-wrap: wrap; gap: 0 4px; color: var(--ink); }
.live-dot { inline-size: 8px; block-size: 8px; border-radius: 50%; background: var(--accent); border: 1.5px solid var(--ink); margin-inline-end: 4px; flex: none; }
.live-how { margin-block-start: 2px; }
.live-how summary { display: inline-flex; min-block-size: 32px; align-items: center; cursor: pointer; text-decoration: underline; text-decoration-color: var(--control); text-underline-offset: 4px; list-style: none; }
.live-how summary::-webkit-details-marker { display: none; }
.live-how summary:hover { color: var(--ink); text-decoration-color: var(--ink); }
.live-how p { margin-block-start: 6px; }
.live-how a { color: var(--ink); text-decoration: underline; text-decoration-color: var(--control); text-underline-offset: 4px; }
.num { font-variant-numeric: tabular-nums; }
</style>
