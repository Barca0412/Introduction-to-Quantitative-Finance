<script setup>
import { withBase } from 'vitepress'
import { data as tutorials } from '../tutorials.data.js'
import { lectureImages } from '../lectureImages.js'
</script>
<template><section aria-labelledby="h-list"><h2 id="h-list" class="index-h">讲义列表</h2><ol class="ledger lecture-ledger"><li v-for="t in tutorials" :key="t.slug"><a class="ledger-row lecture-row" :href="withBase(t.url)"><span class="lec-fig"><img v-if="lectureImages[t.slug]" :src="lectureImages[t.slug]" :alt="t.title+'图表'" width="1600" height="1024" loading="lazy"></span><span class="lec-text"><span class="lec-n">{{ t.title.split(/[：:]/)[0] }} · {{ t.level }}<span v-if="t.slug===tutorials.at(-1)?.slug" class="latest">最新</span></span><span class="lec-t">{{ t.title.replace(/^实战[一二三四五六七八九十]+[：:]/, '') }}</span><span class="lec-d">{{ t.description }}</span><span class="lec-m">先修：{{ t.prerequisites }}　数据：{{ t.data }}</span></span></a></li></ol></section></template>
