<script setup>
// Bottom of every /wiki/ page: the lectures whose frontmatter lists this page
// under `tutorial.wiki`. Renders nothing until such a lecture exists.
import { computed } from 'vue'
import { useRoute, withBase } from 'vitepress'
import { data as tutorials } from '../tutorials.data.js'
import { normalizePath } from '../paths.js'

const route = useRoute()

const current = computed(() => {
  const base = withBase('/').replace(/\/$/, '')
  return normalizePath(route.path.startsWith(base) ? route.path.slice(base.length) : route.path)
})

const linked = computed(() =>
  current.value.startsWith('/wiki') ? tutorials.filter((t) => t.wiki.includes(current.value)) : [],
)
</script>

<template>
  <div v-if="linked.length" class="wiki-backlinks">
    <h2>在这些讲义里实践过</h2>
    <ul>
      <li v-for="t in linked" :key="t.slug">
        <a :href="withBase(t.url)">{{ t.title }}</a>
        <span v-if="t.description"> — {{ t.description }}</span>
      </li>
    </ul>
  </div>
</template>

<style scoped>
.wiki-backlinks {
  margin-top: 48px;
  padding-top: 16px;
  border-top: 1px solid var(--vp-c-divider);
}
.wiki-backlinks h2 {
  margin: 0 0 8px;
  border-top: none;
  padding-top: 0;
  font-size: 18px;
}
</style>
