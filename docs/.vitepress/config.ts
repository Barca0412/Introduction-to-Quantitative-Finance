import { defineConfig } from 'vitepress'
import { mkdirSync, writeFileSync } from 'node:fs'
import { dirname, join } from 'node:path'

const BASE = '/Introduction-to-Quantitative-Finance/'
const SITE = `https://barca0412.github.io${BASE}`

// Sidebar block shared by every section.
const quickNav = {
  text: '全部栏目',
  items: [
    { text: '教程', link: '/tutorials/' },
    { text: '知识库', link: '/wiki/' },
    { text: '研报与论文', link: '/library/' },
    { text: 'FinPaperRadar 论文雷达', link: '/arxiv/' },
    { text: '资源', link: '/resources/' },
    { text: '关于与引用', link: '/about' }
  ]
}

// Pages that moved into /wiki/ in the 2026-11 restructure. Old URLs keep
// working through static redirect pages written in buildEnd below.
// Keys are old paths (without base): 'x/' was x/index.md, 'x/y' was x/y.md.
const MOVED_PAGES: Record<string, string> = {
  'guide/': 'wiki/',
  'guide/framework': 'wiki/framework',
  'data/': 'wiki/data',
  'factors/': 'wiki/factors/',
  'factors/fundamental': 'wiki/factors/fundamental',
  'factors/technical': 'wiki/factors/technical',
  'factors/ml-factors': 'wiki/factors/ml-factors',
  'factors/llm-factors': 'wiki/factors/llm-factors',
  'backtest/': 'wiki/backtest',
  'portfolio/': 'wiki/portfolio',
  'sentiment/': 'wiki/sentiment'
}

function redirectPage(target: string) {
  const url = `${SITE}${target}`
  return `<!doctype html><html lang="zh-CN"><head><meta charset="utf-8">
<title>页面已移动</title>
<link rel="canonical" href="${url}">
<meta name="robots" content="noindex">
<meta http-equiv="refresh" content="0; url=${url}">
<script>location.replace(${JSON.stringify(url)} + location.hash)</script>
</head><body><p>页面已移动到 <a href="${url}">${url}</a>。</p></body></html>
`
}

export default defineConfig({
  vite: {
    define: {
      // Full-dataset location for the FinPaperRadar pages, read at build time.
      // Empty (the default) hides the Hugging Face link.
      __HF_DATASET_REPO__: JSON.stringify((process.env.HF_DATASET_REPO || '').trim()),
      __RADAR_RELEASE_URL__: JSON.stringify(
        `https://github.com/${process.env.GITHUB_REPOSITORY || 'Barca0412/Introduction-to-Quantitative-Finance'}/releases/tag/${process.env.RADAR_RELEASE_TAG || 'radar-data'}`
      ),
    },
  },
  title: '量化研究入门',
  description: '基于多因子股票量化投研框架的开源教程',
  lang: 'zh-CN',
  ignoreDeadLinks: true,
  base: BASE,
  // Lecture code/ and data/ folders hold notebooks and sample data, not pages.
  srcExclude: ['tutorials/*/code/**', 'tutorials/*/data/**'],

  // Old URL -> new URL. Both 'old.html' and 'old/index.html' are written so the
  // redirect also works once cleanUrls is turned on.
  buildEnd({ outDir }) {
    for (const [from, to] of Object.entries(MOVED_PAGES)) {
      const files = from.endsWith('/')
        ? [join(outDir, from, 'index.html')]
        : [join(outDir, `${from}.html`), join(outDir, from, 'index.html')]
      for (const file of files) {
        mkdirSync(dirname(file), { recursive: true })
        writeFileSync(file, redirectPage(to))
      }
    }
  },
  sitemap: {
    hostname: 'https://barca0412.github.io',
    transformItems: (items) => items.map((item) => ({
      ...item,
      url: `/Introduction-to-Quantitative-Finance/${item.url}`,
      links: item.links?.map((link) => ({
        ...link,
        url: `/Introduction-to-Quantitative-Finance/${link.url}`
      }))
    }))
  },
  transformHead: ({ page }) => {
    const path = page
      .replace(/(^|\/)index\.md$/, '$1')
      .replace(/\.md$/, '')

    return [[
      'link',
      {
        rel: 'canonical',
        href: `https://barca0412.github.io/Introduction-to-Quantitative-Finance/${path}`
      }
    ]]
  },
  
  head: [
    ['link', { rel: 'icon', href: '/favicon.ico' }],
    // SEO meta
    ['meta', { name: 'keywords', content: '量化投资,多因子模型,量化交易,机器学习,LLM金融,arXiv论文,因子挖掘,回测框架,投资组合优化' }],
    ['meta', { name: 'author', content: '湖南大学金融科技协会' }],
    // Open Graph
    ['meta', { property: 'og:type', content: 'website' }],
    ['meta', { property: 'og:title', content: '量化研究入门 - 多因子投研框架教程' }],
    ['meta', { property: 'og:description', content: '基于多因子股票量化投研框架的开源教程，每日更新 FinPaperRadar（AI × 金融论文雷达）' }],
    ['meta', { property: 'og:url', content: 'https://barca0412.github.io/Introduction-to-Quantitative-Finance/' }],
    ['meta', { property: 'og:image', content: 'https://barca0412.github.io/Introduction-to-Quantitative-Finance/og-cover.png' }],
    ['meta', { property: 'og:image:alt', content: '量化研究入门：多因子投研框架与 FinPaperRadar（AI × 金融论文雷达）' }],
    // Twitter Card
    ['meta', { name: 'twitter:card', content: 'summary_large_image' }],
    ['meta', { name: 'twitter:image', content: 'https://barca0412.github.io/Introduction-to-Quantitative-Finance/og-cover.png' }],
    ['script', { type: 'application/ld+json' }, JSON.stringify({
      '@context': 'https://schema.org',
      '@graph': [
        {
          '@type': 'Organization',
          name: '湖南大学金融科技协会 Quant Group',
          url: 'https://barca0412.github.io/Introduction-to-Quantitative-Finance/',
          sameAs: ['https://github.com/Barca0412/Introduction-to-Quantitative-Finance']
        },
        {
          '@type': 'WebSite',
          name: '量化研究入门',
          url: 'https://barca0412.github.io/Introduction-to-Quantitative-Finance/',
          inLanguage: 'zh-CN',
          description: '基于多因子股票量化投研框架的开源教程，并提供每日更新的 FinPaperRadar（AI × 金融论文雷达）。'
        }
      ]
    })],
  ],

  themeConfig: {
    logo: '/logo.png',
    
    nav: [
      { text: '首页', link: '/' },
      { text: '教程', link: '/tutorials/', activeMatch: '^/tutorials/' },
      { text: '知识库', link: '/wiki/', activeMatch: '^/wiki/' },
      { text: '研报与论文', link: '/library/', activeMatch: '^/library/' },
      { text: '论文雷达', link: '/arxiv/', activeMatch: '^/arxiv/' },
      { text: '资源', link: '/resources/', activeMatch: '^/resources/' }
    ],

    sidebar: {
      '/tutorials/': [
        {
          text: '教程',
          link: '/tutorials/',
          collapsed: false,
          items: []
        },
        quickNav
      ],
      '/wiki/': [
        {
          text: '知识库',
          link: '/wiki/',
          collapsed: false,
          items: [
            { text: '多因子投研框架', link: '/wiki/framework' },
            { text: '数据源与另类数据', link: '/wiki/data' },
            {
              text: '因子挖掘',
              link: '/wiki/factors/',
              collapsed: false,
              items: [
                { text: '基本面因子', link: '/wiki/factors/fundamental' },
                { text: '技术因子', link: '/wiki/factors/technical' },
                { text: '机器学习因子', link: '/wiki/factors/ml-factors' },
                { text: 'LLM 因子挖掘', link: '/wiki/factors/llm-factors' }
              ]
            },
            { text: '回测框架', link: '/wiki/backtest' },
            { text: '投资组合优化', link: '/wiki/portfolio' },
            { text: '投资者情绪与行为金融', link: '/wiki/sentiment' }
          ]
        },
        quickNav
      ],
      '/library/': [
        {
          text: '研报与论文',
          link: '/library/',
          collapsed: false,
          items: [
            { text: '卖方金工研报', link: '/library/reports' },
            { text: '论文', link: '/library/papers' }
          ]
        },
        quickNav
      ],
      '/arxiv/': [
        {
          text: 'FinPaperRadar',
          link: '/arxiv/',
          collapsed: false,
          items: [
            { text: '总览', link: '/arxiv/' },
            { text: 'Papers', link: '/arxiv/papers' },
            { text: 'Trends', link: '/arxiv/trends' },
            { text: 'About', link: '/arxiv/about' }
          ]
        },
        quickNav
      ],
      '/resources/': [
        {
          text: '公开资源',
          link: '/resources/',
          collapsed: false,
          items: []
        },
        quickNav
      ],
      '/about': [quickNav]
    },

    socialLinks: [
      { icon: 'github', link: 'https://github.com/Barca0412/Introduction-to-Quantitative-Finance' }
    ],

    footer: {
      message: [
        `<a href="${BASE}about">关于</a>`,
        '<a href="https://github.com/Barca0412/Introduction-to-Quantitative-Finance/blob/main/CONTRIBUTING.md">参与贡献</a>',
        `<a href="${BASE}about#如何引用">如何引用</a>`,
        `<a href="${BASE}about#合作与联系">合作联系</a>`
      ].join(' · '),
      copyright: 'Copyright © 2024–2026 湖南大学金融科技协会 Quant Group · 仅供教育与研究，不构成投资建议'
    },

    search: {
      provider: 'local'
    },

    outline: {
      level: [2, 3],
      label: '目录'
    }
  }
})
