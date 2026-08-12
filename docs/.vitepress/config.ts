import { defineConfig } from 'vitepress'

// 共享的快速导航配置
const quickNav = {
  text: '快速导航',
  items: [
    { text: '入门指南', link: '/guide/' },
    { text: '数据源与另类数据', link: '/data/' },
    { text: '因子挖掘', link: '/factors/' },
    { text: '回测框架', link: '/backtest/' },
    { text: '投资组合优化', link: '/portfolio/' },
    { text: 'arXiv 日报', link: '/arxiv/' },
    { text: '公开资源', link: '/resources/' }
  ]
}

export default defineConfig({
  title: '量化研究入门',
  description: '基于多因子股票量化投研框架的开源教程',
  lang: 'zh-CN',
  ignoreDeadLinks: true,
  base: '/Introduction-to-Quantitative-Finance/',
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
    ['meta', { property: 'og:description', content: '基于多因子股票量化投研框架的开源教程，每日更新AI+金融论文' }],
    ['meta', { property: 'og:url', content: 'https://barca0412.github.io/Introduction-to-Quantitative-Finance/' }],
    ['meta', { property: 'og:image', content: 'https://barca0412.github.io/Introduction-to-Quantitative-Finance/og-cover.png' }],
    ['meta', { property: 'og:image:alt', content: '量化研究入门：多因子投研框架与 AI 金融论文雷达' }],
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
          description: '基于多因子股票量化投研框架的开源教程，并提供每日更新的 AI 与金融论文雷达。'
        }
      ]
    })],
  ],

  themeConfig: {
    logo: '/logo.png',
    
    nav: [
      { text: '首页', link: '/' },
      { text: '入门指南', link: '/guide/' },
      { text: '因子挖掘', link: '/factors/' },
      { text: '回测', link: '/backtest/' },
      { text: '组合优化', link: '/portfolio/' },
      { text: 'arXiv日报', link: '/arxiv/' },
      { text: '资源', link: '/resources/' }
    ],

    sidebar: {
      '/guide/': [
        {
          text: '入门指南',
          link: '/guide/',
          collapsed: false,
          items: [
            { text: '多因子投研框架', link: '/guide/framework' }
          ]
        },
        quickNav
      ],
      '/data/': [
        {
          text: '数据源',
          link: '/data/',
          collapsed: false,
          items: []
        },
        quickNav
      ],
      '/factors/': [
        {
          text: '因子挖掘',
          link: '/factors/',
          collapsed: false,
          items: [
            { text: '基本面因子', link: '/factors/fundamental' },
            { text: '技术因子', link: '/factors/technical' },
            { text: '机器学习因子', link: '/factors/ml-factors' },
            { text: 'LLM因子挖掘', link: '/factors/llm-factors' }
          ]
        },
        quickNav
      ],
      '/backtest/': [
        {
          text: '回测框架',
          link: '/backtest/',
          collapsed: false,
          items: []
        },
        quickNav
      ],
      '/portfolio/': [
        {
          text: '投资组合优化',
          link: '/portfolio/',
          collapsed: false,
          items: []
        },
        quickNav
      ],
      '/arxiv/': [
        {
          text: 'ArXiv Radar',
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
      '/sentiment/': [
        {
          text: '投资者情绪',
          link: '/sentiment/',
          collapsed: false,
          items: []
        },
        quickNav
      ]
    },

    socialLinks: [
      { icon: 'github', link: 'https://github.com/Barca0412/Introduction-to-Quantitative-Finance' }
    ],

    footer: {
      message: '基于 VitePress 构建',
      copyright: 'Copyright © 2024 湖南大学金融科技协会'
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
