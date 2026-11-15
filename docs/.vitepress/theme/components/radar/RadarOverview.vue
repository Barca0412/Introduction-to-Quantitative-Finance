<script setup>
import { computed, nextTick, onMounted, ref } from 'vue'
import { withBase } from 'vitepress'
import { loadManifest, loadStats, loadTaxonomy, loadAggregate, loadGroupPapers, loadPaperDetail, loadGroupVectors, scoreAgainst, vectorFor } from '../../radarData.js'
import RadarLoadState from './RadarLoadState.vue'
import RadarEntityLink from './RadarEntityLink.vue'
import { label, shortLabel, listUrl, monthDay, dateRange, weekStart, weekday } from './sectionData.js'

const manifest = ref(null), stats = ref(null), taxonomy = ref(null), leaders = ref(null), papers = ref([])
const loading = ref(true), error = ref(''), selectedDay = ref(''), featured = ref(null), similar = ref([]), extraError = ref('')
const carousel = ref(null), mode = ref('sem'), query = ref('')
const latest = computed(() => manifest.value?.latest_published_date || '')
const cores = computed(() => papers.value.filter((p) => p.relevance === 3 && p.published_date >= weekStart(latest.value)))
const days = computed(() => [...new Set(cores.value.map((p) => p.published_date))].sort().reverse())
const dayPapers = computed(() => cores.value.filter((p) => p.published_date === selectedDay.value))
const grid = computed(() => stats.value?.facets?.grid || { rows: [], cols: [], cells: [] })
const gridMax = computed(() => Math.max(1, ...grid.value.cells.flat()))
const overview = computed(() => leaders.value?.overview || null)
const instDomains = computed(() => (overview.value?.domains || []).filter((_,index) => overview.value.institutions.some((row) => (row.cells || row.domain_counts || [])[index] > 0)))
const instCount = (row, domain) => (row.cells || [])[overview.value?.domains?.indexOf(domain)] || row.domain_counts?.[domain] || 0
const instMax = computed(() => Math.max(1, ...(overview.value?.institutions || []).flatMap((row) => instDomains.value.map((domain) => instCount(row,domain)))))
const uniqueInstMaximum = computed(() => (overview.value?.institutions || []).flatMap((row) => instDomains.value.map((domain) => instCount(row,domain))).filter((n) => n === instMax.value).length === 1)
const pointLabels = [['problem','问题'],['method','方法'],['result','结果'],['limitation','局限']]
const ideas = ['订单簿上的高频预测','大模型读财报','强化学习做组合配置','信用违约预测']

async function load() {
  loading.value=true; error.value=''; extraError.value=''; similar.value=[]
  try {
    const [m,s,t,l,p] = await Promise.all([loadManifest(),loadStats(),loadTaxonomy(),loadAggregate('leaders'),loadGroupPapers('recent')])
    manifest.value=m;stats.value=s;taxonomy.value=t;leaders.value=l;papers.value=p
    selectedDay.value=days.value[0] || ''
    featured.value=cores.value[0] || p.find((paper) => paper.relevance === 3) || p[0] || null
    if(featured.value) {
      try {
        await loadPaperDetail(featured.value)
        featured.value={...featured.value}
        const vectors=await loadGroupVectors('recent'), vector=vectorFor(featured.value.id,[vectors])
        if(vector){const scores=scoreAgainst(vector,[vectors]);similar.value=p.filter((paper)=>paper.id!==featured.value.id && Number.isFinite(scores[paper.id])).sort((a,b)=>scores[b.id]-scores[a.id]).slice(0,5)}
      } catch { extraError.value='论文详情暂时未能加载，可到论文列表重试。' }
    }
  } catch(e) { error.value=e.message || '请稍后重试。' }
  finally { loading.value=false }
}
async function moveDay(event) {
  const direction=['ArrowRight','ArrowDown'].includes(event.key)?1:['ArrowLeft','ArrowUp'].includes(event.key)?-1:0
  if(!direction || !days.value.length)return
  const tablist=event.currentTarget
  event.preventDefault();const index=(days.value.indexOf(selectedDay.value)+direction+days.value.length)%days.value.length
  selectedDay.value=days.value[index];await nextTick();tablist.querySelector('[aria-selected="true"]')?.focus()
}
function slide(direction) {
  const row=carousel.value;if(!row)return
  const items=[...row.children], first=items[0]?.offsetLeft || 0, lefts=items.map((item)=>item.offsetLeft-first)
  const next=direction>0?lefts.find((left)=>left>row.scrollLeft+4):lefts.filter((left)=>left<row.scrollLeft-4).at(-1)
  row.scrollTo({left:next ?? (direction>0?row.scrollWidth:0),behavior:matchMedia('(prefers-reduced-motion: reduce)').matches?'auto':'smooth'})
}
onMounted(load)
</script>

<template>
  <div class="radar-overview">
    <section class="page hero" aria-labelledby="radar-hero">
      <div class="hero-text"><h1 id="radar-hero"><span>AI × 金融</span><span>论文雷达</span></h1><p class="hero-name">FinPaperRadar</p><p class="hero-lead">从 arXiv、NBER 工作论文和顶会中稿名单里挑出 AI × 金融的论文，按金融领域和任务分好类，每篇配一句中文。</p><a class="btn btn-accent" :href="withBase('/arxiv/papers')">打开论文列表</a></div>
      <section class="dash" aria-labelledby="inst-grid-title"><h2 id="inst-grid-title">最近两周发文最多的 5 个机构</h2><RadarLoadState :loading="loading" :error="error" @retry="load" />
        <template v-if="overview && !loading && !error"><div class="dash-grid"><table class="mx mx-inst"><thead><tr><th scope="col"><span class="sr-only">机构</span></th><th v-for="domain in instDomains" :key="domain" class="mx-task" scope="col"><span>{{ shortLabel(taxonomy,'finance_domains',domain) }}</span></th><th class="mx-total" scope="col">篇数</th></tr></thead><tbody><tr v-for="row in overview.institutions" :key="row.id"><th class="mx-domain" scope="row"><RadarEntityLink :item="row" /></th><td v-for="domain in instDomains" :key="domain" class="mx-cell" :data-top="uniqueInstMaximum && instCount(row,domain) === instMax ? 'true' : null"><span v-if="instCount(row,domain)" class="mx-dot" :style="{'--r':instCount(row,domain)/instMax}" :title="`${row.name} × ${label(taxonomy,'finance_domains',domain)}：${instCount(row,domain)} 篇`">{{ instCount(row,domain) }}</span><span v-else class="mx-zero" aria-label="0 篇" /></td><td class="mx-total num">{{ row.n }}</td></tr></tbody></table></div><p class="dash-note">{{ dateRange(overview.since, overview.until || latest) }}的 {{ overview.papers ?? overview.n ?? '已收录' }} 篇论文，按作者所属机构计数：一篇论文有几个机构，就给每个机构各算一篇；一篇也可能横跨几个领域，所以一行的格子加起来可以比篇数多。 <a class="text-link" :href="withBase('/arxiv/people')">看全部机构与作者</a></p></template>
        <p v-else-if="!loading && !error" class="dash-note">机构统计尚未生成。</p>
      </section>
    </section>
    <template v-if="!loading && !error">
      <section class="page agenda" aria-labelledby="agenda-title"><div class="sec-head"><h2 id="agenda-title">本周的核心论文</h2><a class="text-link" :href="listUrl({range:'week'})">本周全部论文</a></div><div class="agenda-body"><div class="day-tabs" role="tablist" aria-label="按天看" @keydown="moveDay"><button v-for="day in days" :id="`day-${day}`" :key="day" type="button" role="tab" class="day-tab" :aria-selected="selectedDay===day" :tabindex="selectedDay===day?0:-1" aria-controls="core-paper-list" @click="selectedDay=day"><span class="day-tab-name">{{ weekday(day) }}</span><span class="day-tab-date num">{{ monthDay(day) }} · {{ cores.filter((p)=>p.published_date===day).length }} 篇</span></button></div><ul id="core-paper-list" class="bands" role="tabpanel" :aria-labelledby="selectedDay?`day-${selectedDay}`:undefined" aria-live="polite"><li v-for="paper in dayPapers" :key="paper.id" class="band"><a :href="listUrl({range:'week'},paper.id)"><span class="band-lead">{{ shortLabel(taxonomy,'finance_domains',paper.finance_domains[0]) }}</span><span class="band-main"><span class="band-title" lang="en">{{ paper.title }}</span><span class="band-note">{{ paper.tldr_zh }}</span></span><span class="band-end">{{ paper.task_types.map((id)=>shortLabel(taxonomy,'task_types',id)).join(' · ') }}<template v-if="paper.venue"> · {{ paper.venue.name }}</template><template v-if="paper.has_code"> · 有代码</template></span></a></li><li v-if="!dayPapers.length" class="empty">本周暂无核心论文。</li></ul></div></section>
      <section class="lit" aria-labelledby="grid-title"><div class="page sec-head"><h2 id="grid-title">每篇论文落在哪一格</h2><span class="lit-nav"><button type="button" data-lit="-1" aria-label="上一块" @click="slide(-1)"/><button type="button" data-lit="1" aria-label="下一块" @click="slide(1)"/></span></div><div ref="carousel" class="lit-row" tabindex="0" aria-label="左右滑动，看雷达界面的几个部分">
        <figure class="lit-item lit-grid"><div class="lit-panel"><table class="mx"><thead><tr><th class="mx-corner" scope="col">领域 ＼ 任务</th><th v-for="task in grid.cols" :key="task" class="mx-task" scope="col"><span>{{ label(taxonomy,'task_types',task) }}</span></th><th class="mx-total" scope="col">合计</th></tr></thead><tbody><tr v-for="(domain,i) in grid.rows" :key="domain"><th class="mx-domain" scope="row">{{ label(taxonomy,'finance_domains',domain) }}</th><td v-for="(task,j) in grid.cols" :key="task" class="mx-cell" :data-top="grid.cells[i][j]===gridMax?'true':null"><a v-if="grid.cells[i][j]" :href="listUrl({range:'all',domain,task})" :style="{'--r':grid.cells[i][j]/gridMax}" :aria-label="`${label(taxonomy,'finance_domains',domain)} × ${label(taxonomy,'task_types',task)}：${grid.cells[i][j]} 篇`">{{ grid.cells[i][j] }}</a><span v-else class="mx-zero" aria-label="0 篇"/></td><td class="mx-total num">{{ stats.facets.dims.finance_domains.total[domain] || 0 }}</td></tr><tr class="mx-foot"><th scope="row" class="mx-domain">合计</th><td v-for="task in grid.cols" :key="task" class="mx-total num">{{ stats.facets.dims.task_types.total[task] || 0 }}</td><td class="mx-total num">{{ stats.summary.total_papers }}</td></tr></tbody></table></div><figcaption><b>金融领域 × 任务。</b>格子里是全部 <span class="num">{{ stats.summary.total_papers }}</span> 篇论文的篇数，包括较早的顶会论文；一篇论文可以落在几格里。点一格，直接看那几篇。</figcaption></figure>
        <figure class="lit-item"><div class="lit-panel"><template v-if="featured"><a class="frag-title" :href="listUrl({range:'all'},featured.id)" lang="en">{{ featured.title }}</a><dl class="points"><div v-for="[key,name] in pointLabels" :key="key" class="point"><dt>{{ name }}</dt><dd>{{ featured.detail?.points?.[key] || '这条要点尚未生成。' }}</dd></div></dl></template><p v-else>暂无论文。</p><p v-if="extraError">{{ extraError }}</p></div><figcaption><b>四句话读完。</b>问题、方法、结果、局限，各一句中文，再决定要不要读原文。</figcaption></figure>
        <figure class="lit-item"><div class="lit-panel"><ul class="similar"><li v-for="paper in similar" :key="paper.id"><a :href="listUrl({range:'all'},paper.id)"><span class="sim-title" lang="en">{{ paper.title }}</span><span class="sim-tldr">{{ paper.tldr_zh }}</span></a></li></ul><p v-if="!similar.length">相近论文暂时没有可用数据。</p></div><figcaption><b>相近的 5 篇。</b>从已载入的论文中，按向量相似度找出最接近的另外 5 篇。</figcaption></figure>
      </div></section>
      <section class="page find" aria-labelledby="find-title"><h2 id="find-title"><label for="radar-find">想找哪方面的论文？</label></h2><form class="find-ui" :action="withBase('/arxiv/papers')" method="get"><input type="hidden" name="range" value="all"><input type="hidden" name="mode" :value="mode"><div class="find-row"><input id="radar-find" v-model="query" class="find-q" type="text" name="q" :placeholder="mode==='sem'?'用一句话说，比如：订单簿上的高频预测':'标题、作者、中文概括里的词，比如：limit order book'" autocomplete="off"><button class="btn btn-ink" type="submit">找论文</button></div><div class="find-opts"><span class="seg" role="group" aria-label="搜索方式"><button type="button" :aria-pressed="mode==='sem'" @click="mode='sem'">按意思找</button><button type="button" :aria-pressed="mode==='kw'" @click="mode='kw'">关键词</button></span><span class="find-try"><a v-for="idea in ideas" :key="idea" class="try" :href="listUrl({range:'all',mode,q:idea})">{{ idea }}</a></span></div></form></section>
    </template>
  </div>
</template>
<style scoped src="./visuals.css"></style>
<style scoped src="./overview.css"></style>
<style scoped>
.bands {list-style:none;padding:0;margin:0}.hero h1 {margin:0}.hero p{margin-bottom:0}.empty{padding:20px;color:var(--muted)}.sr-only{position:absolute;width:1px;height:1px;padding:0;overflow:hidden;clip:rect(0,0,0,0);white-space:nowrap}.radar-overview{--hover:color-mix(in srgb,var(--surface) 70%,var(--bg));--press:color-mix(in srgb,var(--surface) 88%,var(--ink))}.mx-inst .mx-cell[data-top="true"] .mx-dot{background:var(--accent);color:var(--accent-ink)}.mx-inst .mx-cell:not([data-top="true"]) .mx-dot{background:var(--ink);color:var(--bg)}.mx-inst :deep(a){text-decoration:underline;text-decoration-color:var(--control);text-underline-offset:4px}@media(prefers-reduced-motion:reduce){*{animation:none!important;transition:none!important;scroll-behavior:auto!important}}
</style>
