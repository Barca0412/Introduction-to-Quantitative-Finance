<script setup>
import { computed, onMounted, ref } from 'vue'
import { useData } from 'vitepress'
import { data as siteMeta } from '../siteMeta.data.js'
defineProps({ inline: Boolean })
const expanded = ref(false)
onMounted(() => { expanded.value = !matchMedia('(max-width: 860px)').matches })
const { page } = useData()
const isIndex = computed(() => page.value.relativePath === 'resources/index.md')
const entries = computed(() => (page.value.headers || []).flatMap(h => [h, ...(isIndex.value ? [] : h.children || [])]))
</script>

<template>
  <component :is="inline ? 'details' : 'nav'" v-if="entries.length" :class="['resource-outline', inline ? 'resource-outline-inline' : 'resource-outline-side']" :open="inline ? expanded : undefined" :aria-label="inline ? undefined : '本页目录'" @toggle="expanded = $event.target.open">
    <component :is="inline ? 'summary' : 'p'" class="outline-title">本页目录</component>
    <ol><li v-for="entry in entries" :key="entry.slug" :class="{ sub: entry.level > 2 }"><a :href="'#' + entry.slug"><span>{{ entry.title }}</span><span v-if="isIndex && siteMeta.resourceCategories[entry.title]" class="num">{{ siteMeta.resourceCategories[entry.title] }}</span></a></li></ol>
  </component>
</template>

<style scoped>
.outline-title { margin:0 0 12px; font-weight:600; font-size:15px; }
.resource-outline ol { list-style:none; padding:0; margin:0; }
.resource-outline a { display:flex; justify-content:space-between; gap:12px; padding:5px 0 5px 12px; border-left:2px solid var(--rule); color:var(--muted); font-size:14px; line-height:1.45; text-decoration:none; }
.resource-outline .sub a { padding-left:24px; }
.resource-outline a:hover,.resource-outline a:focus-visible { color:var(--ink); border-color:var(--ink); }
.resource-outline .num { flex:none; }
.resource-outline-inline { display:none; }
@media(max-width:1240px){ .resource-outline-inline { display:block; margin-top:24px; }.resource-outline-inline summary { cursor:pointer; } }
@media(max-width:860px){
 .resource-outline-inline summary { display:flex; justify-content:space-between; padding:12px 0; margin:0; border-block:1px solid var(--rule); list-style:none; }
 .resource-outline-inline summary::-webkit-details-marker { display:none; }
 .resource-outline-inline summary::after { content:'+'; color:var(--muted); }
 .resource-outline-inline[open] summary::after { content:'−'; }
 .resource-outline-inline ol { margin-top:12px; }
}
</style>
