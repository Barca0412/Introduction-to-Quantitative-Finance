<script setup>
// Lecture index for /tutorials/ (mode="list") and the
// "reproduced reports" index on /library/ (mode="reports").
import { computed } from 'vue'
import { withBase } from 'vitepress'
import { data as tutorials } from '../tutorials.data.js'

const props = defineProps({
  mode: { type: String, default: 'list' },
})

const showLevel = computed(() => tutorials.some((t) => t.level))
const showDuration = computed(() => tutorials.some((t) => t.duration))

const reproductions = computed(() =>
  tutorials.flatMap((t) =>
    t.reports.map((report) => ({
      tutorial: t,
      title: typeof report === 'string' ? report : report.title,
      link: typeof report === 'string' ? '' : report.link || '',
    })),
  ),
)
</script>

<template>
  <div class="tutorial-list">
    <template v-if="props.mode === 'reports'">
      <table v-if="reproductions.length">
        <thead><tr><th>研报</th><th>复现它的讲义</th></tr></thead>
        <tbody>
          <tr v-for="item in reproductions" :key="item.tutorial.slug + item.title">
            <td>
              <a v-if="item.link" :href="item.link" target="_blank" rel="noopener">{{ item.title }}</a>
              <span v-else>{{ item.title }}</span>
            </td>
            <td><a :href="withBase(item.tutorial.url)">{{ item.tutorial.title }}</a></td>
          </tr>
        </tbody>
      </table>
      <p v-else class="tutorial-list-empty">还没有讲义复现研报。讲义上线后，复现过的研报会自动列在这里。</p>
    </template>

    <template v-else>
      <table v-if="tutorials.length">
        <thead>
          <tr>
            <th class="tutorial-list-title">讲义</th>
            <th v-if="showLevel">难度</th>
            <th v-if="showDuration">时长</th>
            <th>你会做出什么</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="t in tutorials" :key="t.slug">
            <td class="tutorial-list-title"><a :href="withBase(t.url)">{{ t.title }}</a></td>
            <td v-if="showLevel" class="tutorial-list-nowrap">{{ t.level }}</td>
            <td v-if="showDuration" class="tutorial-list-nowrap">{{ t.duration }}</td>
            <td>{{ t.description }}</td>
          </tr>
        </tbody>
      </table>
      <p v-else class="tutorial-list-empty">首批因子投资讲义正在整理，上线后会自动出现在这里。</p>
    </template>
  </div>
</template>

<style scoped>
.tutorial-list-empty {
  color: var(--vp-c-text-2);
}
.tutorial-list-title {
  min-width: 11em;
}
.tutorial-list-nowrap {
  white-space: nowrap;
}
</style>
