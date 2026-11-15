<script setup>
import { computed, onMounted, ref } from 'vue'
import { loadManifest, loadStats } from '../../radarData.js'
import { REPOSITORY, COLLECTION_START, zhDate } from './sectionData.js'
const manifest=ref(null),stats=ref(null),error=ref('')
const collectionStart=computed(()=>manifest.value?.collection_since || COLLECTION_START)
const hfRepo=__HF_DATASET_REPO__
const releaseUrl=__RADAR_RELEASE_URL__
const contents=[['what-h','这是什么'],['pick-h','论文怎么选出来'],['src-h','数据从哪里来'],['dl-h','下载数据'],['cite-h','怎么引用'],['ack-h','致谢']]
const citation=`@misc{finpaperradar2026,\n  title        = {FinPaperRadar: AI × Finance Paper Radar},\n  author       = {Quant Group, Hunan University FinTech Association},\n  year         = {2026},\n  howpublished = {\\url{${REPOSITORY}}}\n}`
async function load(){error.value='';try{const [m,s]=await Promise.all([loadManifest(),loadStats()]);manifest.value=m;stats.value=s}catch{error.value='当前篇数暂时无法读取。'}}
onMounted(load)
</script>
<template>
  <div class="page doc radar-about">
    <div class="doc-head"><h1>AI × 金融论文雷达 FinPaperRadar</h1><p class="doc-lead">说明：这个雷达是什么、论文怎么选、数据从哪来，以及怎么下载和引用。</p></div>
    <nav class="toc" aria-label="本页目录"><a v-for="[id,name] in contents" :key="id" :href="`#${id}`">{{ name }}</a></nav>
    <div class="doc-body">
      <section aria-labelledby="what-h"><h2 id="what-h">这是什么</h2><p>AI × 金融论文雷达（FinPaperRadar）从每天新出的论文和顶会的中稿名单里，挑出“用 AI 方法研究金融问题”的那部分，替你先读一遍。每篇论文都配一句中文总结，再用问题、方法、结果、局限四句话讲清楚，并按金融领域、任务和方法分好类。现在雷达上一共有 <span class="num">{{ stats?.summary?.total_papers ?? '—' }}</span> 篇，其中 <span class="num">{{ stats?.summary?.core_papers ?? '—' }}</span> 篇是核心论文。</p><p v-if="error" class="count-error" role="status">{{ error }} <button type="button" @click="load">重试</button></p><p>它适合想跟进 AI × 金融研究、但没时间每天翻 arXiv 的学生和研究者。中文总结和分类由大模型生成，可能有错，引用前请读原文。</p></section>
      <section aria-labelledby="pick-h"><h2 id="pick-h">论文怎么选出来</h2><p>每篇论文先按“和金融有多大关系”打一个 0 到 3 的分：</p><dl class="rel"><div><dt><span class="core-mark">3 核心</span></dt><dd>研究的问题本身就是金融问题，AI 是方法。比如用大模型挖 A 股因子、用强化学习做组合配置、从财报文字预测违约。专门为金融做的模型、数据集和评测基准也算。</dd></div><div><dt>2 主要应用</dt><dd>方法是通用的，但金融是主要或第一个验证场景，而且有专门为金融做的设计。</dd></div><div><dt>1 顺带</dt><dd>金融数据只是几个测试集之一，没有专门为金融做设计。不上雷达。</dd></div><div><dt>0 无关</dt><dd>和金融没有关系。不上雷达。</dd></div></dl><p>只有 2 分和 3 分的论文会出现在这里。还有一条：论文必须用了 AI 方法，也就是大模型、智能体、强化学习、深度学习、图模型、生成模型或传统机器学习中的至少一种。只用计量和统计方法的金融论文不在这个雷达的收录范围内。</p></section>
      <section aria-labelledby="src-h"><h2 id="src-h">数据从哪里来</h2><ul class="src"><li><b>arXiv。</b>从 {{ collectionStart.slice(0,4) }} 年 {{ zhDate(collectionStart) }}起，每天收录 arXiv 上新出的论文。</li><li><b>顶会和期刊的中稿名单。</b>KDD、AAAI、ACL、EMNLP、CIKM、ACM ICAIF 等会议公布的录用论文，其中包含较早发表的研究。</li><li><b>NBER 工作论文。</b>补充金融经济方向的研究，同样经过 AI 方法与金融相关度筛选。</li></ul><p>每篇论文会标出发表状态：已发表、已录用、工作论文，或者还只是预印本。SSRN 等来源计划接入。</p></section>
      <section aria-labelledby="dl-h"><h2 id="dl-h">下载数据</h2><p>雷达上的论文元数据、分类和中文总结可以整份下载，供研究和教学使用。我们生成的分类、中文总结和整理结果按 CC BY 4.0 授权，论文内容遵循原作者许可。</p><ul class="links"><li v-if="hfRepo"><a class="text-link" :href="`https://huggingface.co/datasets/${hfRepo}`" target="_blank" rel="noopener">Hugging Face 数据集 {{ hfRepo }}</a></li><li><a class="text-link" :href="releaseUrl" target="_blank" rel="noopener">GitHub Release：radar-data（下载镜像）</a></li><li><a class="text-link" :href="REPOSITORY" target="_blank" rel="noopener">GitHub 仓库：代码、讲义和雷达都在这里</a></li></ul><p v-if="hfRepo">Hugging Face 无法访问时，可以使用 GitHub Release 下载镜像。</p></section>
      <section aria-labelledby="cite-h"><h2 id="cite-h">怎么引用</h2><p>如果这个雷达或它的数据对你的研究有帮助，可以这样引用：</p><pre class="cite">{{ citation }}</pre><p>引用某一篇论文时，请引用它的原文，不要引用这里的中文总结。</p></section>
      <section aria-labelledby="ack-h"><h2 id="ack-h">致谢</h2><p lang="en" class="ack">Thank you to arXiv for use of its open access interoperability.</p><p>感谢 arXiv 开放接口。论文内容的版权属于原作者；雷达展示论文信息和我们生成的中文概括，链接到原文，不转载全文。</p></section>
    </div>
  </div>
</template>
<style scoped src="./visuals.css"></style>
<style scoped src="./about.css"></style>
<style scoped>
.doc h1{margin:0}.doc-body ul{list-style:none;padding:0}.doc dd{margin:0}.doc h2{scroll-margin-top:calc(var(--head-h,106px) + 20px)}.count-error{color:var(--muted)}.count-error button{text-decoration:underline;text-underline-offset:4px}.doc .toc{inset-block-start:calc(var(--head-h,106px) + 24px)}
</style>
