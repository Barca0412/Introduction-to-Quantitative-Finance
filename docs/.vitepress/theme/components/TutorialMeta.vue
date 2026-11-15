<script setup>
// Lecture header card, shown above any page whose frontmatter has `tutorial:`.
// Keeps every lecture's "level / duration / prerequisites / data / code" block identical.
import { computed } from 'vue'
import { useData, withBase } from 'vitepress'
import { normalizePath } from '../paths.js'
import { METHOD_NAV } from '../../../../scripts/site/routes.mjs'

const REPO = 'https://github.com/Barca0412/Introduction-to-Quantitative-Finance'
const { frontmatter, page } = useData()

const asList = (value) => (Array.isArray(value) ? value : value ? [value] : [])
const meta = computed(() => frontmatter.value.tutorial || null)
const concepts = computed(() => asList(meta.value?.wiki).map(normalizePath).map(link => ({ link, text: METHOD_NAV.find(item => item.link === link)?.text || link })))

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
    ['先修', asList(t.prerequisites).join('、')],
    ['数据', asList(t.data).join('、')],
    ['整理', t.author],
    ['授权', t.license],
  ].filter(([, value]) => value)
})
</script>

<template>
  <div v-if="meta" class="tutorial-meta">
    <dl>
      <div v-for="[label, value] in rows" :key="label">
        <dt>{{ label }}</dt>
        <dd>{{ value }}</dd>
      </div>
      <div v-if="concepts.length"><dt>用到的概念</dt><dd><template v-for="(concept, index) in concepts" :key="concept.link"><span v-if="index">、</span><a :href="withBase(concept.link)">{{ concept.text }}</a></template></dd></div>
    </dl>
    <p v-if="codeUrl" class="tutorial-meta-links">
      <a v-if="codeUrl" :href="codeUrl" target="_blank" rel="noopener">查看本讲代码</a>
    </p>
  </div>
</template>

<style scoped>
.tutorial-meta {
  margin: 0 0 24px;
  padding: 0 0 24px;
  min-width: 0;
  border: 0;
  border-radius: 0;
  background: none;
  font-size: 14px;
}
.tutorial-meta dl {
  display: block;
  margin: 0;
  border-top: 1px solid var(--rule);
}
.tutorial-meta dl > div {
  display: grid;
  grid-template-columns: 5.5em minmax(0, 1fr);
  min-width: 0;
  gap: 12px;
  padding: 10px 0;
  border-bottom: 1px solid var(--rule);
}
.tutorial-meta dt {
  color: var(--vp-c-text-2);
  margin: 0;
  padding-top: 2px;
  line-height: 1.55;
}
.tutorial-meta dd {
  margin: 0;
  min-width: 0;
  font-size: 15px;
  line-height: 1.55;
  overflow-wrap: anywhere;
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
