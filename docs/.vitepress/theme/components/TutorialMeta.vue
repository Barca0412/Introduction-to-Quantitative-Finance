<script setup>
// Lecture header card, shown above any page whose frontmatter has `tutorial:`.
// Keeps every lecture's "level / duration / prerequisites / data / code" block identical.
import { computed } from 'vue'
import { useData } from 'vitepress'

const REPO = 'https://github.com/Barca0412/Introduction-to-Quantitative-Finance'
const { frontmatter, page } = useData()

const asList = (value) => (Array.isArray(value) ? value : value ? [value] : [])
const meta = computed(() => frontmatter.value.tutorial || null)

// docs/tutorials/01-factor-ic-test/index.md -> .../tree/main/docs/tutorials/01-factor-ic-test/code
const codeUrl = computed(() => {
  if (!meta.value || meta.value.code === false) return ''
  const dir = page.value.relativePath.replace(/\/index\.md$/, '')
  const sub = typeof meta.value.code === 'string' ? meta.value.code : 'code'
  return `${REPO}/tree/main/docs/${dir}/${sub}`
})

const rows = computed(() => {
  const t = meta.value
  if (!t) return []
  return [
    ['难度', t.level],
    ['预计时长', t.duration],
    ['前置知识', asList(t.prerequisites).join('、')],
    ['数据', asList(t.data).join('、')],
    ['署名', t.author],
  ].filter(([, value]) => value)
})
</script>

<template>
  <div v-if="meta" class="tutorial-meta">
    <dl>
      <template v-for="[label, value] in rows" :key="label">
        <dt>{{ label }}</dt>
        <dd>{{ value }}</dd>
      </template>
    </dl>
    <p class="tutorial-meta-links">
      <a v-if="codeUrl" :href="codeUrl" target="_blank" rel="noopener">查看本讲代码</a>
      <span v-if="meta.license" class="tutorial-meta-license">{{ meta.license }}</span>
    </p>
  </div>
</template>

<style scoped>
.tutorial-meta {
  margin: 0 0 24px;
  padding: 12px 16px;
  border: 1px solid var(--vp-c-divider);
  border-radius: 8px;
  background: var(--vp-c-bg-soft);
  font-size: 14px;
}
.tutorial-meta dl {
  display: grid;
  grid-template-columns: max-content 1fr;
  gap: 4px 16px;
  margin: 0;
}
.tutorial-meta dt {
  color: var(--vp-c-text-2);
}
.tutorial-meta dd {
  margin: 0;
}
.tutorial-meta-links {
  display: flex;
  gap: 16px;
  align-items: baseline;
  margin: 8px 0 0;
}
.tutorial-meta-license {
  color: var(--vp-c-text-2);
  font-size: 13px;
}
</style>
