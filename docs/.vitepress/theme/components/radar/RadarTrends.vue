<script setup>
import { computed, onMounted, ref } from 'vue'
import { loadManifest, loadStats, loadTaxonomy, loadAggregate } from '../../radarData.js'
import RadarLoadState from './RadarLoadState.vue'
import RadarTimeBars from './RadarTimeBars.vue'
import { REPOSITORY, COLLECTION_START, DAY, atUTC, isoDate, monthDay, zhDate, dateRange, weekStart, label, shortLabel, listUrl } from './sectionData.js'
const loading=ref(true), error=ref(''), manifest=ref(null), stats=ref(null), taxonomy=ref(null), keywords=ref(null), rising=ref(null), range=ref('month')
const latest=computed(()=>manifest.value?.latest_published_date || '')
const collectionStart=computed(()=>manifest.value?.collection_since || COLLECTION_START)
const monthStart=computed(()=>latest.value ? `${latest.value.slice(0,7)}-01` : '')
const facets=computed(()=>stats.value?.facets || {})
const observed=computed(()=>(facets.value.dates || []).map((date,index)=>({date,n:facets.value.total?.daily[index] || 0,core:facets.value.core?.daily[index] || 0})).filter((row)=>row.date>=collectionStart.value && row.date<=latest.value))
const weeks=computed(()=>{
  if(!latest.value || collectionStart.value>latest.value)return []
  const grouped=new Map()
  // Keep zero-paper weeks on the calendar instead of silently closing the gap.
  const start=Math.max(atUTC(weekStart(collectionStart.value)),atUTC(weekStart(latest.value))-11*7*DAY)
  for(let time=start;time<=atUTC(latest.value);time+=7*DAY){const key=isoDate(time);grouped.set(key,{key,n:0,core:0})}
  for(const row of observed.value){const item=grouped.get(weekStart(row.date));if(item){item.n+=row.n;item.core+=row.core}}
  const withYear=isoDate(start).slice(0,4)!==latest.value.slice(0,4)
  return [...grouped.values()].map((row)=>{const from=row.key<collectionStart.value?collectionStart.value:row.key;const end=isoDate(Math.min(atUTC(row.key)+6*DAY,atUTC(latest.value)));return {...row,label:from===end?monthDay(from,withYear):`${monthDay(from,withYear)} 至 ${monthDay(end,withYear)}`,accessibleLabel:from===end?from:`${from} 至 ${end}`,href:listUrl({range:from===end?'day':'week',d:from})}})
})
const days=computed(()=>{
  if(!latest.value)return []
  const start=Math.max(atUTC(collectionStart.value),atUTC(latest.value)-27*DAY), counts=new Map(observed.value.map((row)=>[row.date,row])), out=[]
  for(let t=start;t<=atUTC(latest.value);t+=DAY){const key=isoDate(t), row=counts.get(key)||{n:0,core:0};out.push({...row,key,label:String(Number(key.slice(8))),accessibleLabel:key,href:listUrl({range:'day',d:key})})}
  return out
})
const dimensions=[{group:'finance_domains',param:'domain',name:'金融领域'},{group:'task_types',param:'task',name:'任务'},{group:'methods',param:'method',name:'方法'}]
const distributions=computed(()=>dimensions.map((dim)=>{
  const data=facets.value.dims?.[dim.group] || {}, ids=taxonomy.value?.order?.[dim.group] || Object.keys(data.total||{})
  const rows=ids.map((id)=>({id,name:shortLabel(taxonomy.value,dim.group,id),full:label(taxonomy.value,dim.group,id),n:range.value==='all'?(data.total?.[id]||0):(facets.value.dates||[]).reduce((sum,date,index)=>sum+(date>=monthStart.value?(data.daily?.[id]?.[index]||0):0),0)})).sort((a,b)=>b.n-a.n)
  return {...dim,rows,max:Math.max(1,...rows.map((row)=>row.n))}
}))
const rangeCount=computed(()=>range.value==='all'?(stats.value?.summary?.total_papers||0):(facets.value.dates||[]).reduce((sum,date,index)=>sum+(date>=monthStart.value?(facets.value.total?.daily[index]||0):0),0))
const keywordWeeks=computed(()=>(keywords.value?.weeks||[]).slice(-4))
const keywordRows=computed(()=>{
  const allWeeks=keywords.value?.weeks||[], last=allWeeks.length-1
  return Object.entries(keywords.value?.keywords||{}).map(([id,row])=>({id,name:row.name,counts:row.counts})).sort((a,b)=>(b.counts[last]||0)-(a.counts[last]||0)||(b.counts[last-1]||0)-(a.counts[last-1]||0)||a.name.localeCompare(b.name,'zh-CN')).slice(0,10).map((row)=>({...row,counts:row.counts.slice(-4)}))
})
const keywordMax=computed(()=>Math.max(1,...keywordRows.value.flatMap((row)=>row.counts)))
const risingKinds=[['domain','金融领域'],['method','方法'],['keyword','关键词'],['institution','机构']]
const risingName=(kind,item)=>kind==='domain'?label(taxonomy.value,'finance_domains',item.id):kind==='method'?label(taxonomy.value,'methods',item.id):item.name
async function load(){loading.value=true;error.value='';try{const [m,s,t,k,r]=await Promise.all([loadManifest(),loadStats(),loadTaxonomy(),loadAggregate('weekly_keywords'),loadAggregate('rising')]);manifest.value=m;stats.value=s;taxonomy.value=t;keywords.value=k;rising.value=r}catch(e){error.value=e.message||'请稍后重试。'}finally{loading.value=false}}
onMounted(load)
</script>
<template>
  <div class="page screen radar-trends">
    <div class="title-row"><div><h1>趋势</h1><p class="title-sub">arXiv 每日收录从 {{ collectionStart.slice(0,4) }} 年 {{ zhDate(collectionStart) }}开始，之前的论文来自顶会中稿名单。</p></div></div>
    <p class="wip">这一页是对雷达里论文的数据可视化和挖掘。看哪些维度、怎么画，都还在边做边改。如果你想看一个新的维度，或者有更好的办法把趋势和洞察画出来，非常欢迎来提：<a class="text-link" :href="`${REPOSITORY}/issues`" target="_blank" rel="noopener">在 GitHub 开一个 issue</a>，或者直接看<a class="text-link" :href="REPOSITORY" target="_blank" rel="noopener">仓库</a>。</p>
    <RadarLoadState :loading="loading" :error="error" @retry="load"/>
    <template v-if="!loading && !error">
      <div class="grid g-time"><section class="block" aria-labelledby="weeks-title"><div class="block-head"><h2 id="weeks-title">每周论文</h2><p class="legend"><span><i class="k-core"/>核心</span><span><i class="k-rest"/>主要应用</span></p></div><RadarTimeBars :columns="weeks"/><p class="block-note">按已收录论文的发表日期统计，显示最近最多 12 周；最后一周可能尚未结束。</p></section><section class="block" aria-labelledby="days-title"><div class="block-head"><h2 id="days-title">每天论文</h2><p class="block-note">{{ dateRange(days[0]?.key, latest) }}</p></div><RadarTimeBars :columns="days" daily/></section></div>
      <div class="dist-head"><h2>论文都在研究什么</h2><span class="seg" role="group" aria-label="统计范围"><button type="button" :aria-pressed="range==='month'" @click="range='month'">{{ Number(latest.slice(5,7)) }} 月起</button><button type="button" :aria-pressed="range==='all'" @click="range='all'">全部</button></span><p class="block-note">{{ range==='all'?'全部':`${zhDate(monthStart)}起` }} {{ rangeCount }} 篇{{ range==='all'?'，包括较早的顶会论文':'' }}。一篇论文可以有几个标签，所以各项加起来比总数多。</p></div>
      <div class="grid g-dist"><section v-for="dim in distributions" :key="dim.group" class="block" :aria-labelledby="`dist-${dim.group}`"><div class="block-head"><h2 :id="`dist-${dim.group}`">{{ dim.name }}</h2></div><div class="blist" style="--label:6.5em"><a v-for="row in dim.rows" :key="row.id" :href="listUrl({range,[dim.param]:row.id})" :aria-label="`${row.full}：${row.n} 篇`"><span>{{ row.name }}</span><span class="bl-track"><span class="bl-fill" :style="{'--w':row.n/dim.max}"/></span><span class="bl-n num">{{ row.n }}</span></a></div></section></div>
      <div class="grid g-kw"><section class="block" aria-labelledby="keywords-title"><div class="block-head"><h2 id="keywords-title">每周关键词</h2><p class="block-note">按这周的篇数排，前 {{ keywordRows.length }} 个</p></div><div class="kw-scroll"><table v-if="keywordRows.length" class="kw-table"><thead><tr><th scope="col">关键词</th><th v-for="(week,index) in keywordWeeks" :key="week" class="n" scope="col">{{ monthDay(week) }} {{ index===keywordWeeks.length-1?'这周':'那周' }}</th></tr></thead><tbody><tr v-for="row in keywordRows" :key="row.id"><th scope="row"><a :href="listUrl({range:'all',q:row.name,mode:'kw'})">{{ row.name }}</a></th><td v-for="(count,index) in row.counts" :key="index" class="n"><span class="kw-bar" :class="{'is-now':index===row.counts.length-1}" :style="{'--w':count/keywordMax}"/><span class="num">{{ count }}</span></td></tr></tbody></table><p v-else class="block-note">每周关键词数据尚未生成。</p></div></section><section class="block" aria-labelledby="rising-title"><div class="block-head"><h2 id="rising-title">升温最快</h2></div><template v-if="!rising?.enough_history"><p class="plain">还没有完整的 4 周历史，暂不比较涨跌。</p><p class="block-note">这周之前有 {{ rising?.weeks_compared?.length || 0 }} 周可以比较。攒够 4 周以后，这里会列出比前几周明显变多的领域、方法、关键词和机构。</p></template><template v-else><div v-for="[key,name] in risingKinds" :key="key"><h3 class="rise-h">{{ name }}</h3><ul v-if="rising.lists?.[key]?.length" class="rise"><li v-for="item in rising.lists[key].slice(0,5)" :key="item.id"><span>{{ risingName(key,item) }}</span><span class="num">{{ item.n }} 篇，{{ item.new?'新出现':`前几周平均 ${item.mean_before}` }}</span></li></ul><p v-else class="block-note">没有明显升温的。</p></div></template></section></div>
    </template>
  </div>
</template>
<style scoped src="./visuals.css"></style>
<style scoped src="./trends.css"></style>
<style scoped>.kw-scroll{overflow-x:auto}.kw-table{border-collapse:collapse}.radar-trends{--hover:color-mix(in srgb,var(--surface) 70%,var(--bg))}.rise{list-style:none;padding:0}.title-row h1{margin:0}.kw-table th a:hover{text-decoration:underline;text-underline-offset:3px}@media(prefers-reduced-motion:reduce){*{transition:none!important}}</style>
