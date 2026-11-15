<script setup>
import { computed } from 'vue'
const props = defineProps({ columns: { type: Array, default: () => [] }, daily: Boolean })
const maximum = computed(() => Math.max(1, ...props.columns.map((column) => column.n)))
</script>
<template>
  <div v-if="columns.length" class="time-bars" :class="{daily}">
    <div class="plot">
      <a v-for="column in columns" :key="column.key" :href="column.href" :aria-label="`${column.accessibleLabel || column.label}：${column.n} 篇，核心 ${column.core} 篇`">
        <span class="number" :style="{top:`${160-column.n/maximum*160}px`}">{{ column.n }}</span>
        <svg viewBox="0 0 100 160" preserveAspectRatio="none" aria-hidden="true"><rect x="0" :y="160-column.n/maximum*160" width="100" :height="column.n/maximum*160" class="other"/><rect x="0" :y="160-column.core/maximum*160" width="100" :height="column.core/maximum*160" class="core"/></svg>
      </a>
    </div>
    <div class="axis"><span v-for="column in columns" :key="column.key">{{ column.label }}</span></div>
  </div>
  <p v-else>暂无可统计的论文。</p>
</template>
<style scoped>
.plot,.axis {display:grid;grid-auto-flow:column;grid-auto-columns:minmax(0,1fr);column-gap:10px;text-align:center}.plot{height:180px;align-items:end;border-bottom:1px solid var(--ink)}.plot a{height:100%;position:relative;display:flex;flex-direction:column;justify-content:end}.number{position:absolute;inset:0 0 auto;font-size:12.5px;font-variant-numeric:tabular-nums}.plot svg{height:160px;width:100%;overflow:visible}.other{fill:var(--control)}.core{fill:var(--ink)}.plot a:hover .other{fill:var(--muted)}.axis{padding-top:6px;font-size:12px;line-height:16px;color:var(--muted);font-variant-numeric:tabular-nums}.daily .plot,.daily .axis{column-gap:6px}@media(max-width:700px){.daily .axis span:nth-child(even){visibility:hidden}.time-bars{min-width:0}}
</style>
