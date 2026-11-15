<script setup>
import { computed } from 'vue'
import RadarEntityLink from './RadarEntityLink.vue'
import { rankNumbers } from './sectionData.js'
const props = defineProps({ items: { type: Array, default: () => [] }, kind: String, numbered: Boolean, compact: Boolean, plain: Boolean, showCore: Boolean })
const max = computed(() => Math.max(1, ...props.items.map((item) => item.n || 0)))
const ranks = computed(() => rankNumbers(props.items))
</script>
<template>
  <ol v-if="items.length" class="rank" :class="{compact,plain}">
    <li v-for="(item,index) in items" :key="item.id || item.code || item.name">
      <span v-if="numbered" class="no">{{ ranks[index] }}</span>
      <span class="name"><RadarEntityLink v-if="kind" :kind="kind" :item="item" /><span v-else>{{ item.name }}</span><small v-if="item.description">{{ item.description }}</small><small v-else-if="item.institution"><RadarEntityLink kind="institution" :item="{name:item.institution,page:item.institution_page}" /></small></span>
      <svg v-if="!plain" class="bar" viewBox="0 0 100 10" preserveAspectRatio="none" role="img" :aria-label="`${item.n} 篇${item.core == null ? '' : `，其中核心 ${item.core} 篇`}`"><rect x="0" y="0" :width="item.n / max * 100" height="10" rx="2" class="other"/><rect x="0" y="0" :width="(item.core ?? item.n) / max * 100" height="10" rx="2" class="core"/></svg>
      <span class="num">{{ item.n }} 篇<small v-if="showCore">核心 {{ item.core || 0 }}</small></span>
    </li>
  </ol>
  <p v-else class="empty">这段时间暂无数据。</p>
</template>
<style scoped>
.rank { list-style:none; padding:0; margin:0; }
.rank li { display:grid; grid-template-columns:26px minmax(0,1fr) minmax(80px,30%) 96px; gap:14px; align-items:center; padding:9px 8px; margin-inline:-8px; border-bottom:1px solid var(--rule); transition:background-color 120ms ease-out; }
.rank li:hover { background:var(--surface); }
.rank .no { color:var(--muted); font-size:var(--step-small); text-align:right; }
.name { min-width:0; font-weight:600; }
.name small { display:block; color:var(--muted); font-size:.8125rem; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; font-weight:400; }
.name :deep(a:hover) { text-decoration:underline; text-underline-offset:4px; }
.bar { height:10px; width:100%; display:block; }
.other { fill:var(--control); }.core{fill:var(--ink)}
.num { text-align:right; font-size:.9375rem; white-space:nowrap; font-variant-numeric:tabular-nums; }
.num small { color:var(--muted); font-size:.8125rem; margin-left:6px; }
.rank.compact li { grid-template-columns:minmax(0,1fr) minmax(60px,34%) 64px; padding-block:7px; }
.rank.plain li { grid-template-columns:26px minmax(0,1fr) 96px; }
.empty { color:var(--muted); padding:14px 0; border-bottom:1px solid var(--rule); }
@media(max-width:900px){.rank li{grid-template-columns:22px minmax(0,1fr) 84px;row-gap:6px}.bar{grid-column:2/4;grid-row:2}.rank.compact li{grid-template-columns:minmax(0,1fr) 64px}.rank.compact .bar{grid-column:1/3}.rank.plain li{grid-template-columns:22px minmax(0,1fr) 84px}}
</style>
