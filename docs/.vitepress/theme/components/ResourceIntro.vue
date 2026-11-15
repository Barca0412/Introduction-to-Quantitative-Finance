<script setup>
import { computed } from 'vue'
import { useData, withBase } from 'vitepress'
import ResourceOutline from './ResourceOutline.vue'
const { frontmatter, page } = useData()
const isIndex = computed(() => page.value.relativePath === 'resources/index.md')
</script>

<template>
  <header class="resource-intro">
    <nav class="resource-crumbs" aria-label="位置"><a :href="withBase(isIndex ? '/' : '/resources/')">{{ isIndex ? '首页' : '开源资源清单' }}</a></nav>
    <h1>{{ frontmatter.title }}</h1>
    <p v-if="frontmatter.description" class="read-lead">{{ frontmatter.description }}</p>
    <ResourceOutline inline />
  </header>
</template>

<style scoped>
.resource-intro { margin-bottom:40px; }
.resource-crumbs { font-size:14px; color:var(--muted); }
.resource-crumbs a:hover { text-decoration:underline; text-underline-offset:4px; }
h1 { margin-top:16px; font-size:clamp(1.75rem,1.3rem + 1vw,2.25rem); line-height:1.25; font-weight:600; letter-spacing:-.02em; }
.read-lead { margin-top:20px; font-size:17px; line-height:1.75; color:var(--muted); }
</style>
