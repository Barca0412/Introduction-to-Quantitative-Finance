<script setup>
import { useData } from 'vitepress'
import TutorialMeta from './TutorialMeta.vue'
defineProps({ mobile: Boolean })
const {page,frontmatter}=useData()
</script>
<template><div v-if="frontmatter.tutorial" class="lecture-sidebar"><TutorialMeta/><details class="lecture-toc-fold" :open="!mobile"><summary class="side-h">本页目录</summary><nav class="lecture-toc" aria-label="本讲目录"><template v-for="h in page.headers" :key="h.slug"><a :href="'#'+h.slug">{{h.title}}</a><a v-for="c in h.children || []" :key="c.slug" class="sub" :href="'#'+c.slug">{{c.title}}</a></template></nav></details></div></template>
