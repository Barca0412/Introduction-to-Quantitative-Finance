<script setup>
import { computed, onMounted, ref } from 'vue'
import { loadManifest, loadTaxonomy, loadAggregate } from '../../radarData.js'
import RadarLoadState from './RadarLoadState.vue'
import RadarRankList from './RadarRankList.vue'
import RadarEntityLink from './RadarEntityLink.vue'
import { COLLECTION_START, label, shortLabel, periodOptions, zhDate } from './sectionData.js'
const loading=ref(true),error=ref(''),manifest=ref(null),taxonomy=ref(null),leaders=ref(null),teams=ref([]),period=ref('30d'),showAll=ref(false)
const options=computed(()=>periodOptions(leaders.value))
const current=computed(()=>leaders.value?.periods?.[period.value] || null)
const periodName=computed(()=>options.value.find((item)=>item.key===period.value)?.name || '')
const totals=computed(()=>current.value?.totals || {})
const countries=computed(()=>Object.fromEntries((current.value?.countries||[]).map((item)=>[item.code,item.name])))
const institutions=computed(()=>(current.value?.institutions||[]).map((item)=>({...item,description:[item.name_en,item.type_zh||'类型未知',countries.value[item.country]||item.country||'国家未知'].filter(Boolean).join(' · ')})))
const shownInstitutions=computed(()=>showAll.value?institutions.value:institutions.value.slice(0,16))
const grid=computed(()=>current.value?.institution_domain||{domains:[],rows:[]})
const gridRows=computed(()=>grid.value.rows.map((row)=>({...row,cells:row.counts||row.cells||[],n:row.n ?? institutions.value.find((item)=>item.id===row.id)?.n ?? 0})))
const gridMax=computed(()=>Math.max(0,...gridRows.value.flatMap((row)=>row.cells)))
const finding=computed(()=>{
  if(!current.value)return ''
  const beginning=`${periodName.value}收录 ${current.value.papers} 篇，来自 ${totals.value.institutions || 0} 个机构。`, top=institutions.value[0]
  if(!top)return beginning
  const tied=institutions.value.filter((item)=>item.n===top.n)
  return beginning+(tied.length===1?`${top.name} ${top.n} 篇最多${top.core===top.n?'，而且全是核心论文':`，其中核心 ${top.core} 篇`}。`:`${tied.map((item)=>item.name).join('、')} 并列最多，各 ${top.n} 篇。`)
})
const collaboration=computed(()=>{
  const co=current.value?.collaboration||{}
  return [['只有高校和研究机构','education','sw-data'],['高校和企业合作','mixed','sw-muted'],['只有企业','company','sw-soft'],['有政府、非营利等其他机构','other','sw-pale'],['没有识别出机构','unknown','sw-none']].map(([name,key,cls])=>({name,key,cls,n:co[key]||0}))
})
const collaborationTotal=computed(()=>collaboration.value.reduce((sum,item)=>sum+item.n,0))
const crossPairs=computed(()=>(current.value?.cross_country?.pairs||[]).slice(0,5).map((item)=>({...item,id:item.pair,name:item.names.join(' 与 ')})))
const dotSize=(n)=>n===0?0:n===1?1:n<=3?2:n<=5?3:4
const domainSummary=(row)=>row.cells.map((n,index)=>({id:grid.value.domains[index],n})).filter((item)=>item.n).sort((a,b)=>b.n-a.n).slice(0,3).map((item)=>`${shortLabel(taxonomy.value,'finance_domains',item.id)} ${item.n}`).join(' · ')
function selectPeriod(key){period.value=key;showAll.value=false}
async function load(){loading.value=true;error.value='';try{const [m,t,l,te]=await Promise.all([loadManifest(),loadTaxonomy(),loadAggregate('leaders'),loadAggregate('teams')]);manifest.value=m;taxonomy.value=t;leaders.value=l;teams.value=te?.teams||[];if(!l?.periods?.[period.value])period.value=Object.keys(l?.periods||{})[0]||'30d'}catch(e){error.value=e.message||'请稍后重试。'}finally{loading.value=false}}
onMounted(load)
</script>
<template>
  <div class="page people">
    <div class="head"><div><h1>机构与作者</h1><p class="finding">{{ finding }}</p></div><div class="seg" role="group" aria-label="时间段"><button v-for="item in options" :key="item.key" type="button" :aria-pressed="period===item.key" @click="selectPeriod(item.key)">{{ item.name }}</button></div></div>
    <p class="note">arXiv 新论文从 {{ zhDate(manifest?.collection_since || COLLECTION_START, true) }}开始收录；更早的论文只来自各顶会的中稿名单，所以“{{ manifest?.latest_published_date?.slice(0,4) || '今年' }} 年”和“全部”偏向已经发表的论文，不能和“近 30 天”直接比多少。</p>
    <RadarLoadState :loading="loading" :error="error" @retry="load"/>
    <template v-if="current && !loading && !error">
      <section class="block"><header><h2>哪家机构在做哪一块</h2><span>{{ periodName }}发文最多的 {{ gridRows.length }} 个机构 × {{ grid.domains.length }} 个金融领域；圆越大篇数越多，一篇可以算在多个领域</span></header><table class="matrix"><thead><tr><th scope="col"><span class="sr-only">机构</span></th><th v-for="domain in grid.domains" :key="domain" scope="col" :title="label(taxonomy,'finance_domains',domain)">{{ shortLabel(taxonomy,'finance_domains',domain) }}</th></tr></thead><tbody><tr v-for="row in gridRows" :key="row.id"><th class="row" scope="row"><RadarEntityLink :item="row"/><small>{{ row.n }} 篇</small></th><td v-for="(count,index) in row.cells" :key="grid.domains[index]"><span class="dot" :class="[`s${dotSize(count)}`,{'top':count===gridMax && count>1}]" role="img" :aria-label="`${row.name} · ${label(taxonomy,'finance_domains',grid.domains[index])}：${count} 篇`" :title="`${row.name} · ${label(taxonomy,'finance_domains',grid.domains[index])}：${count} 篇`">{{ count>1?count:'' }}</span></td></tr></tbody></table><p v-if="!gridRows.length" class="empty">这段时间没有识别出机构。</p><p class="legend matrix-legend"><span><span class="dot s1"/>1 篇</span><span><span class="dot s2">3</span>2 到 3 篇</span><span><span class="dot s3">5</span>4 到 5 篇</span><span><span class="dot s0"/>没有</span><span v-if="gridMax>1"><span class="dot s2 top">{{ gridMax }}</span>这段时间最多的一格</span></p><ol class="rank plain matrix-list"><li v-for="(row,index) in gridRows" :key="row.id"><span class="no">{{ index+1 }}</span><span class="name"><RadarEntityLink :item="row"/><small>{{ domainSummary(row) }}</small></span><span class="num">{{ row.n }} 篇</span></li></ol></section>
      <div class="cols"><div class="stack"><section><header><h2>机构</h2><span>共 {{ totals.institutions }} 个；按论文篇数，深色部分是核心论文</span><button v-if="institutions.length>16" class="more" type="button" :aria-expanded="showAll" @click="showAll=!showAll">{{ showAll?'只看前 16 个':`显示前 ${institutions.length} 个` }}</button></header><RadarRankList :items="shownInstitutions" kind="institution" numbered show-core/><p class="legend"><span><i class="sw-data"/>核心论文</span><span><i class="sw-soft"/>其他相关论文</span><span>同样篇数的名次并列；并列时先比核心篇数，再按名称排</span></p></section></div>
        <div class="stack"><section><header><h2>企业</h2><span>共 {{ totals.companies }} 家，参与了 {{ (current.collaboration?.company||0)+(current.collaboration?.mixed||0) }} 篇</span></header><RadarRankList :items="(current.companies||[]).slice(0,5)" kind="institution" compact/></section><section><header><h2>国家和地区</h2><span>共 {{ totals.countries }} 个；一篇可以算在多个地方</span></header><RadarRankList :items="(current.countries||[]).slice(0,7)" compact/></section><section><header><h2>跨国合作</h2><span>{{ current.cross_country?.papers || 0 }} 篇论文的作者来自不止一个国家或地区</span></header><RadarRankList :items="crossPairs" compact/></section><section><header><h2>谁和谁合作</h2><span>按每篇论文里机构的类型分</span></header><div class="split" role="img" :aria-label="collaboration.map((item)=>`${item.name} ${item.n} 篇`).join('；')"><i v-for="part in collaboration.filter((item)=>item.n)" :key="part.key" :class="part.cls" :style="{width:`${100*part.n/(collaborationTotal||1)}%`}"/></div><ul class="kv"><li v-for="part in collaboration" :key="part.key"><span><i :class="part.cls"/>{{ part.name }}</span><span>{{ part.n }} 篇<small>{{ Math.round(100*part.n/(collaborationTotal||1)) }}%</small></span></li></ul></section></div>
      </div>
      <div class="cols"><div class="stack"><section><header><h2>固定团队</h2><span>至少合写过 2 篇的作者连成一组；共 {{ teams.length }} 组，列出前 6 组（全部数据）</span></header><ol v-if="teams.length" class="teams"><li v-for="(team,index) in teams.slice(0,6)" :key="team.id || index"><div class="where"><template v-for="(institution,i) in team.institutions.slice(0,2)" :key="institution.id"><span v-if="i">、</span><RadarEntityLink :item="institution"/></template><small>{{ team.members.length }} 人 · 合写 {{ team.papers }} 篇 · 核心 {{ team.core }}</small></div><div class="who"><template v-for="(person,i) in team.members.slice(0,7)" :key="person.id"><span v-if="i" class="sep"> · </span><RadarEntityLink kind="author" :item="person"/></template><span v-if="team.members.length>7"> · 等 {{ team.members.length }} 人</span></div><div class="what">{{ team.domains.map(([id,n])=>`${shortLabel(taxonomy,'finance_domains',id)} ${n}`).join(' · ') }}</div></li></ol><p v-else class="empty">还没有符合条件的固定团队。</p></section></div><div class="stack"><section><header><h2>作者</h2><span>共 {{ totals.authors }} 位，列出前 {{ Math.min(10,current.authors?.length||0) }} 位</span></header><RadarRankList :items="(current.authors||[]).slice(0,10)" kind="author" numbered plain show-core/></section></div></div>
      <p class="note missing">本页只统计网站上展示的论文，也就是和 AI × 金融相关、且用了 AI 方法的论文。没有识别出机构的论文（见“谁和谁合作”）没有计入机构和国家的统计。</p>
    </template><p v-else-if="!loading && !error" class="empty">机构与作者数据尚未生成。</p>
  </div>
</template>
<style scoped src="./people.css"></style>
<style scoped>
ol,ul{list-style:none;padding:0;margin:0}.head h1{margin:0}.missing{margin-top:40px}.matrix{border-collapse:collapse}.matrix thead th:not(:first-child){max-width:4em;white-space:normal}.people :deep(a:hover){text-decoration:underline;text-underline-offset:4px}.sr-only{position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0,0,0,0)}@media(prefers-reduced-motion:reduce){*{transition:none!important}}
</style>
