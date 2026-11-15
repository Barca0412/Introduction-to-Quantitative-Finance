<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRoute, withBase } from 'vitepress'
import { loadManifest } from '../radarData.js'
const route = useRoute()
const date = ref('')
const tabs = [['总览', '/arxiv/'], ['论文', '/arxiv/papers'], ['趋势', '/arxiv/trends'], ['机构与作者', '/arxiv/people'], ['说明', '/arxiv/about']]
const active = computed(() => route.path.replace(withBase('/'), '/').replace(/\.html$/, ''))
const current = p => p === '/arxiv/people' ? /\/arxiv\/(people|institution|author)/.test(active.value) : active.value === p
onMounted(async () => { try { const m = await loadManifest(); const d = m.latest_published_date; date.value = d ? `${Number(d.slice(5,7))} 月 ${Number(d.slice(8,10))} 日` : '' } catch { date.value = '' } })
</script>
<template><nav class="radar-tabs" aria-label="论文雷达的页面"><a v-for="[text,path] in tabs" :key="path" class="tab" :href="withBase(path)" :aria-current="current(path) ? 'page' : undefined">{{ text }}</a><span v-if="date" class="radar-fresh">数据截至 {{ date }}</span></nav></template>
