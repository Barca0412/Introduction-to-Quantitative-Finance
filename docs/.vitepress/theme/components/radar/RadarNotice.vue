<script setup>
// arXiv 自己停发（假期名单、临时停发）时说明原因，告诉读者不是本站坏了。
// 文案由 scripts/arxiv_radar/arxiv_calendar.py 写进 manifest.json 的 arxiv_schedule；
// 周末只在 RadarNav 的"数据截至"旁轻提示，这里只处理 level === 'holiday'。
import { computed, onMounted, ref } from 'vue'
import { loadManifest } from '../../radarData.js'
const props = defineProps({ variant: { type: String, default: 'banner' } })
const schedule = ref(null)
onMounted(async () => { try { schedule.value = (await loadManifest()).arxiv_schedule || null } catch { schedule.value = null } })
const parts = computed(() => {
  const s = schedule.value
  if (s?.level !== 'holiday' || !s.notice_zh) return null
  const link = s.link_text_zh
  const at = link ? s.notice_zh.indexOf(link) : -1
  return at < 0 ? { before: s.notice_zh, link: '', after: '' } : { before: s.notice_zh.slice(0, at), link, after: s.notice_zh.slice(at + link.length) }
})
</script>

<template>
  <div v-if="parts" :class="variant === 'note' ? 'index-note radar-notice-note' : 'radar-notice page'" role="status">
    <p><i v-if="variant !== 'note'" aria-hidden="true"></i><span>{{ parts.before }}<a v-if="parts.link" :href="schedule.source_url" target="_blank" rel="noopener">{{ parts.link }}</a>{{ parts.after }}</span></p>
  </div>
</template>

<style scoped>
.radar-notice { margin-block-start: 16px; }
.radar-notice p { display: flex; align-items: baseline; gap: 10px; padding: 12px 16px; border-radius: var(--fig-radius); background: var(--surface); color: var(--ink); font-size: 0.9375rem; line-height: 1.7; }
.radar-notice i { inline-size: 9px; block-size: 9px; border-radius: 50%; background: var(--accent); border: 1.5px solid var(--ink); flex: none; transform: translateY(-1px); }
a { text-decoration: underline; text-decoration-thickness: 2px; text-underline-offset: 4px; text-decoration-color: var(--accent); }
a:hover { text-decoration-color: var(--ink); }
@media (max-width: 860px) { .radar-notice p { padding: 10px 14px; font-size: 0.875rem; } }
</style>
