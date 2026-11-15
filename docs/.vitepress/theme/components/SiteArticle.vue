<script setup>
import { computed, onMounted, ref } from 'vue'
import { useData, withBase } from 'vitepress'
const { frontmatter, page } = useData()
const open = ref(true)
const headers = computed(()=>page.value.headers || [])
onMounted(()=>{open.value=!matchMedia('(max-width: 860px)').matches})
</script>
<template><div class="content-view"><main id="main" class="page read"><nav class="crumbs" aria-label="位置"><a :href="withBase('/')">首页</a></nav><header class="read-head"><h1>{{ frontmatter.title }}</h1><p class="read-lead">{{ frontmatter.description }}</p></header><div class="read-grid"><aside class="read-side"><details class="toc" :open="open" @toggle="open=$event.target.open"><summary>本页目录</summary><ol><li v-for="h in headers" :key="h.slug" class="l2"><a :href="'#'+h.slug">{{ h.title }}</a></li></ol></details></aside><article class="prose"><slot /></article></div></main></div></template>
