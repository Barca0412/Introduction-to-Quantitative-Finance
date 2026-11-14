<script setup>
// Header card for knowledge-base concept pages whose frontmatter has a `wiki:` block:
//   wiki:
//     level: 入门 | 进阶 | 高级
//     prerequisites: [IC, 分层回测]
//     code: true            # the page contains runnable code
// Authorship and licence are the same for every concept page.
import { computed } from 'vue'
import { useData } from 'vitepress'

const { frontmatter, page } = useData()
const meta = computed(() => (page.value.relativePath.startsWith('wiki/') ? frontmatter.value.wiki || null : null))
const asList = (v) => (Array.isArray(v) ? v : v ? [v] : [])

const rows = computed(() => {
  const w = meta.value
  if (!w) return []
  return [
    ['难度', w.level],
    ['前置知识', asList(w.prerequisites).join('、')],
    ['可运行代码', w.code ? '有（免费数据可复现）' : ''],
    ['署名', '湖南大学金融科技协会 Quant Group'],
  ].filter(([, v]) => v)
})
</script>

<template>
  <div v-if="meta" class="wiki-meta">
    <dl>
      <template v-for="[label, value] in rows" :key="label">
        <dt>{{ label }}</dt>
        <dd>{{ value }}</dd>
      </template>
    </dl>
    <p class="wiki-meta-license">
      文字按 <a href="https://creativecommons.org/licenses/by/4.0/deed.zh-hans" target="_blank" rel="noopener">CC BY 4.0</a> 授权，代码按 MIT 授权。
    </p>
  </div>
</template>

<style scoped>
.wiki-meta {
  margin: 0 0 24px;
  padding: 12px 16px;
  border: 1px solid var(--vp-c-divider);
  border-radius: 8px;
  background: var(--vp-c-bg-soft);
  font-size: 14px;
}
.wiki-meta dl {
  display: grid;
  grid-template-columns: max-content 1fr;
  gap: 4px 16px;
  margin: 0;
}
.wiki-meta dt {
  color: var(--vp-c-text-2);
}
.wiki-meta dd {
  margin: 0;
}
.wiki-meta-license {
  margin: 8px 0 0;
  color: var(--vp-c-text-2);
  font-size: 13px;
}
</style>
