<script setup>
import { computed, onMounted, onUnmounted, ref, watch } from 'vue'
import { withBase, useRoute } from 'vitepress'
import { loadTaxonomy, loadAggregate, loadPapersByIds } from '../../radarData.js'
import RadarLoadState from './RadarLoadState.vue'
import RadarRankList from './RadarRankList.vue'
import RadarEntityLink from './RadarEntityLink.vue'
import { label, shortLabel } from './sectionData.js'
const props=defineProps({kind:{type:String,default:'institution'}}), route=useRoute()
const entity=ref(null),taxonomy=ref(null),papers=ref([]),loading=ref(true),error=ref(''),missing=ref(false)
let generation=0
const kindName=computed(()=>props.kind==='author'?'作者':'机构')
const related=computed(()=>props.kind==='author'?entity.value?.coauthors||[]:entity.value?.authors||[])
const finding=computed(()=>{
  const x=entity.value;if(!x)return ''
  const dom=x.domains?.[0], second=x.domains?.[1], method=x.methods?.[0], partner=(props.kind==='author'?x.coauthors:x.co_institutions)?.[0]
  return (dom?`${props.kind==='author'?'主要做':'做得最多的是'}${label(taxonomy.value,'finance_domains',dom[0])}（${dom[1]} 篇）${second?`和${label(taxonomy.value,'finance_domains',second[0])}（${second[1]} 篇）`:''}`:'还没有金融领域的分类')+(method?`，方法以${label(taxonomy.value,'methods',method[0])}为主（${method[1]} 篇）`:'')+'。'+(partner?`${props.kind==='author'?'合写最多的是':'最常一起署名的是'} ${partner.name}（${partner.n} 篇）。`:'')
})
const pairRows=(pairs,group)=>(pairs||[]).slice(0,6).map(([id,n])=>({id,name:label(taxonomy.value,group,id),n}))
const plus=(n)=>`${n}${n>=10?'+':''}`
async function load(){
  const ticket=++generation;loading.value=true;error.value='';missing.value=false;entity.value=null;papers.value=[]
  const id=new URLSearchParams(window.location.search).get('id')
  if(!id || !/^[a-zA-Z0-9_-]+$/.test(id)){missing.value=true;loading.value=false;return}
  try{const [x,t]=await Promise.all([loadAggregate(`${props.kind}/${id}`),loadTaxonomy()]);if(ticket!==generation)return;if(!x){missing.value=true;return}entity.value=x;taxonomy.value=t;const p=await loadPapersByIds(x.papers||[]);if(ticket!==generation)return;papers.value=[...p].sort((a,b)=>b.published_date.localeCompare(a.published_date)||a.id.localeCompare(b.id));document.title=`${x.name} · ${kindName.value} · FinPaperRadar`}
  catch(e){if(ticket===generation)error.value=e.message||'请稍后重试。'}finally{if(ticket===generation)loading.value=false}
}
onMounted(()=>{load();window.addEventListener('popstate',load)})
watch(()=>route.path,()=>{if(typeof window!=='undefined')load()})
watch(()=>props.kind,()=>{if(typeof window!=='undefined')load()})
onUnmounted(()=>{generation++;window.removeEventListener('popstate',load)})
</script>
<template>
  <div class="page people">
    <a class="back" :href="withBase('/arxiv/people')">← 机构与作者</a>
    <RadarLoadState :loading="loading" :error="error" @retry="load"/>
    <div v-if="missing && !loading" class="entity"><div><h1>没有找到这个{{ kindName }}</h1><p class="sub">只有发文至少 2 篇的{{ kindName }}才有单独页面。可以回到机构与作者页，从排行里点进去。</p></div></div>
    <template v-else-if="entity && !loading && !error">
      <div class="entity"><div><h1>{{ entity.name }}</h1><p v-if="kind==='institution'" class="sub"><template v-if="entity.name_en && entity.name_en!==entity.name">{{ entity.name_en }} · </template>{{ entity.type_zh || '类型未知' }} · {{ entity.country_zh || entity.country || '国家未知' }}</p><p v-else class="sub"><template v-if="entity.institutions?.length"><template v-for="(institution,index) in entity.institutions" :key="institution.id"><span v-if="index">、</span><RadarEntityLink :item="institution"/></template></template><span v-else>机构未识别</span><template v-if="entity.spellings?.length>1"> · 署名写法：{{ entity.spellings.join(' / ') }}</template><template v-if="entity.openalex"> · <a :href="entity.openalex" target="_blank" rel="noopener">OpenAlex 主页</a></template></p></div><div class="figures"><div><b>{{ entity.papers.length }}</b><span>篇论文</span></div><div><b>{{ entity.core }}</b><span>篇核心</span></div><div><b>{{ plus(related.length) }}</b><span>{{ kind==='author'?'位合作者':'位作者' }}</span></div></div></div>
      <p class="finding">{{ finding }}</p><p v-if="kind==='author'" class="note">作者根据 OpenAlex 编号、ORCID、邮箱指纹及合作关系识别；缺少这些信息时只能使用姓名，重名的作者仍可能被合并。网页不保存或展示邮箱明文。</p>
      <div class="cols"><div class="stack"><section><header><h2>论文</h2><span>从新到旧；圆点是核心论文<template v-if="entity.papers.length>papers.length">；另有 {{ entity.papers.length-papers.length }} 篇暂不在网站论文数据中</template></span></header><ol class="papers"><li v-for="paper in papers" :key="paper.id"><span class="date">{{ paper.published_date.slice(2).replaceAll('-','.') }}</span><span v-if="paper.relevance===3" class="core" role="img" aria-label="核心论文" title="核心论文"/><span v-else/><div><a class="title" :href="paper.abs_link" lang="en" target="_blank" rel="noopener">{{ paper.title }}</a><div v-if="paper.tldr_zh" class="tl">{{ paper.tldr_zh }}</div><div class="meta"><template v-if="paper.venue"><b>{{ paper.venue.name }}</b>{{ paper.venue.official?'（官方中稿名单）':'' }}　</template>{{ paper.finance_domains.map((id)=>shortLabel(taxonomy,'finance_domains',id)).join(' · ') }}</div></div></li></ol><p v-if="!papers.length" class="empty">暂时没有可展示的论文。</p></section></div>
        <div class="stack"><section v-if="kind==='author'"><header><h2>合作者</h2><span>合写的篇数</span></header><RadarRankList :items="(entity.coauthors||[]).slice(0,8)" kind="author" compact/></section><section><header><h2>金融领域</h2><span>一篇可以属于多个</span></header><RadarRankList :items="pairRows(entity.domains,'finance_domains')" compact/></section><section><header><h2>方法</h2></header><RadarRankList :items="pairRows(entity.methods,'methods')" compact/></section><section v-if="kind==='institution'"><header><h2>常合作的机构</h2></header><RadarRankList :items="(entity.co_institutions||[]).slice(0,6)" kind="institution" compact/></section><section v-if="kind==='institution'"><header><h2>作者</h2><span>在这个机构署名的篇数</span></header><RadarRankList :items="(entity.authors||[]).slice(0,8)" kind="author" compact/></section><section v-else><header><h2>署名机构</h2></header><RadarRankList :items="entity.institutions||[]" kind="institution" compact/></section></div>
      </div>
    </template>
  </div>
</template>
<style scoped src="./people.css"></style>
<style scoped>ol{list-style:none;padding:0;margin:0}.entity h1{margin:0}.people :deep(a:hover){text-decoration:underline;text-underline-offset:4px}.papers .core{background:var(--accent);border:1px solid var(--ink)}@media(prefers-reduced-motion:reduce){*{transition:none!important}}</style>
