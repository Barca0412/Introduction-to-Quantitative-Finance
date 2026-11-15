<script setup>
import { computed, ref, watch } from 'vue'
import { useData, useRoute, withBase } from 'vitepress'
import GitHubStar from './GitHubStar.vue'
import RadarNav from './RadarNav.vue'
const route = useRoute()
const { isDark } = useData()
const open = ref(false)
const path = computed(() => route.path.replace(withBase('/'), '/'))
const radar = computed(() => path.value.startsWith('/arxiv'))
const nav = [['首页', '/'], ['教程', '/tutorials/'], ['开源资源清单', '/resources/'], ['研报与论文', '/library/'], ['AI × 金融论文雷达', '/arxiv/'], ['投稿与联系', '/contact']]
const current = p => p === '/' ? path.value === '/' : path.value.startsWith(p.replace(/\/$/, ''))
watch(() => route.path, () => { open.value = false })
function search() { window.dispatchEvent(new KeyboardEvent('keydown', { key: 'k', ctrlKey: true, bubbles: true })); open.value = false }
</script>
<template>
<header id="site-header" :class="{ 'has-radar-nav': radar }">
  <div class="site-nav" :class="{open}">
    <a class="site-name" :href="withBase('/')"><i aria-hidden="true"></i>量化研究入门与AI+金融</a>
    <nav class="site-links" id="site-links" aria-label="站点导航"><a v-for="[name,url] in nav" :key="url" :href="withBase(url)" :aria-current="current(url)?'page':undefined">{{ name }}<span v-if="url === '/arxiv/'" class="sub">FinPaperRadar</span></a></nav>
    <GitHubStar />
    <button type="button" class="site-menu" :aria-expanded="open" aria-controls="site-links" @click="open = !open">{{ open ? '收起' : '菜单' }}</button>
    <details class="site-tools"><summary aria-label="站内搜索与显示设置">···</summary><div><button type="button" @click="search">搜索站内内容 <kbd>⌘ K</kbd></button><button type="button" @click="isDark = !isDark">切换深浅色</button></div></details>
  </div>
  <RadarNav v-if="radar" />
</header>
</template>
