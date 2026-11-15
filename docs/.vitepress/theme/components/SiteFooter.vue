<script setup>
import { withBase } from 'vitepress'
import GitHubStar from './GitHubStar.vue'
const groups = [
 {title:'资源',links:[['开源资源清单','/resources/'],['研报与论文','/library/'],['教程','/tutorials/']]},
 {title:'AI × 金融论文雷达',links:[['总览','/arxiv/'],['论文','/arxiv/papers'],['趋势','/arxiv/trends'],['机构与作者','/arxiv/people'],['说明','/arxiv/about']]},
 {title:'关于',links:[['投稿与联系','/contact'],['关于与引用','/about']]}
]
</script>
<template><footer id="site-footer" class="site-foot"><div class="foot-inner">
<div class="foot-star"><p>觉得有用，欢迎在 GitHub 点一个 Star。代码、讲义和雷达的数据都在这个仓库里。</p><GitHubStar /></div>
<div class="foot-grid"><div v-for="g in groups" :key="g.title"><p>{{ g.title }}</p><a v-for="[name,url] in g.links" :key="url" :href="withBase(url)">{{ name }}</a><a v-if="g.title === '关于'" href="https://github.com/Barca0412/Introduction-to-Quantitative-Finance" target="_blank" rel="noopener">GitHub 仓库</a></div><div><p>来源</p><span>论文来自 arXiv、NBER 与顶会录用名单</span><span>中文总结由模型生成</span><span>湖南大学金融科技协会 Quant Group</span></div></div>
<p class="foot-name" aria-hidden="true"><i></i>量化研究入门与AI+金融资源站</p>
<p class="foot-legal">Thank you to arXiv for use of its open access interoperability. 感谢 arXiv 开放接口。</p>
</div></footer></template>
