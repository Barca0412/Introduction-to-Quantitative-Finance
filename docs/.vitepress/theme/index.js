import { computed, defineAsyncComponent, h } from 'vue'
import DefaultTheme from 'vitepress/theme'
import { useData, withBase } from 'vitepress'
import './tokens.css'
import './content.css'
import './style.css'
import SiteHeader from './components/SiteHeader.vue'
import SiteFooter from './components/SiteFooter.vue'
import TutorialSidebar from './components/TutorialSidebar.vue'
import RadarNotice from './components/radar/RadarNotice.vue'
import ResourceIntro from './components/ResourceIntro.vue'
import ResourceOutline from './components/ResourceOutline.vue'
import WikiBacklinks from './components/WikiBacklinks.vue'
import WikiMeta from './components/WikiMeta.vue'
import TutorialList from './components/TutorialList.vue'
import { installAnalytics } from './analytics.js'
import SubscribeCard from './components/SubscribeCard.vue'
import { installSubscribeTimer } from './subscribe.js'
const TutorialIndex = defineAsyncComponent(() => import('./components/TutorialIndex.vue'))
const HomePage = defineAsyncComponent(() => import('./components/HomePage.vue'))
const LibraryIndex = defineAsyncComponent(() => import('./components/LibraryIndex.vue'))
const SiteArticle = defineAsyncComponent(() => import('./components/SiteArticle.vue'))
const asyncComponent = name => defineAsyncComponent(name)
const RadarOverview = asyncComponent(() => import('./components/radar/RadarOverview.vue'))
const RadarPapers = asyncComponent(() => import('./components/radar/RadarPapers.vue'))
const RadarTrends = asyncComponent(() => import('./components/radar/RadarTrends.vue'))
const RadarPeople = asyncComponent(() => import('./components/radar/RadarPeople.vue'))
const RadarEntity = asyncComponent(() => import('./components/radar/RadarEntity.vue'))
const RadarAbout = asyncComponent(() => import('./components/radar/RadarAbout.vue'))
const IconWrapper = asyncComponent(() => import('./components/IconWrapper.vue'))
const externalLink = (href,text) => h('a',{href,target:'_blank',rel:'noopener'},text)
export const RadarDatasetLinks = {setup(){ return ()=>h('span',{class:'radar-dataset-links'},[
 '完整数据：', ...(__HF_DATASET_REPO__ ? [externalLink(`https://huggingface.co/datasets/${__HF_DATASET_REPO__}`,'Hugging Face'),' · '] : []), externalLink(__RADAR_RELEASE_URL__,'GitHub Release')
])}}
const Layout = {setup(){const {frontmatter,page}=useData();const tutorial=computed(()=>Boolean(frontmatter.value.tutorial));const resource=computed(()=>page.value.relativePath.startsWith('resources/'));const radar=computed(()=>page.value.relativePath.startsWith('arxiv/'));return ()=>h(DefaultTheme.Layout,{class:{'lecture-page':tutorial.value,'resource-page':resource.value}},{
 'layout-top':()=>[h(SiteHeader), radar.value ? h(RadarNotice) : null, tutorial.value ? h('div',{class:'lecture-intro page'},[h('nav',{class:'lecture-crumbs','aria-label':'位置'},[h('a',{href:withBase('/tutorials/')},'教程')]),h('header',{class:'lecture-heading'},[h('h1',frontmatter.value.title),h('p',{class:'read-lead'},frontmatter.value.description)]),h(TutorialSidebar,{class:'lecture-mobile-sidebar',mobile:true})]) : null],
 'sidebar-nav-before':()=>tutorial.value?h(TutorialSidebar):null,
 'doc-before':()=>tutorial.value?null:[resource.value?h(ResourceIntro):null,h(WikiMeta)],
 'aside-outline-before':()=>resource.value?h(ResourceOutline):null,
 'doc-after':()=>h(WikiBacklinks),
 'layout-bottom':()=>[h(SiteFooter),h(SubscribeCard)]
})}}
export default {extends:DefaultTheme,Layout,enhanceApp({app,router}){
 if(typeof window!=='undefined') installAnalytics(router)
 if(typeof window!=='undefined') installSubscribeTimer()
 if(typeof window!=='undefined') document.addEventListener('click',event=>{const img=event.target.closest?.('.vp-doc img');if(img&&!img.closest('a'))window.open(img.currentSrc||img.src,'_blank','noopener')})
 for(const [name,component] of Object.entries({HomePage,TutorialIndex,TutorialList,LibraryIndex,SiteArticle,RadarOverview,RadarPapers,RadarTrends,RadarPeople,RadarEntity,RadarAbout,IconWrapper,RadarDatasetLinks}))app.component(name,component)
}}
