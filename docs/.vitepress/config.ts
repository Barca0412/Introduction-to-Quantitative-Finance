import { defineConfig } from 'vitepress'

export default defineConfig({
  title: '量化研究入门',
  description: '基于多因子股票量化投研框架的开源教程',
  lang: 'zh-CN',
  ignoreDeadLinks: true,
  base: '/Introduction-to-Quantitative-Finance/',
  
  head: [
    ['link', { rel: 'icon', href: '/favicon.ico' }]
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
          items: [
            { text: '简介', link: '/guide/' },
            { text: '多因子投研框架', link: '/guide/framework' }
          ]
        },
        {
          text: '快速导航',
          items: [
            { text: '数据源与另类数据', link: '/data/' },
            { text: '因子挖掘', link: '/factors/' },
            { text: '回测框架', link: '/backtest/' },
            { text: '投资组合优化', link: '/portfolio/' },
            { text: 'arXiv 日报', link: '/arxiv/' },
            { text: '公开资源', link: '/resources/' }
          ]
        }
      ],
      '/data/': [
        {
          text: '数据源',
          items: [
            { text: '概述', link: '/data/' }
          ]
        }
      ],
      '/factors/': [
        {
          text: '因子挖掘',
          items: [
            { text: '概述', link: '/factors/' },
            { text: '基本面因子', link: '/factors/fundamental' },
            { text: '技术因子', link: '/factors/technical' },
            { text: '机器学习因子', link: '/factors/ml-factors' },
            { text: 'LLM因子挖掘', link: '/factors/llm-factors' }
          ]
        }
      ],
      '/backtest/': [
        {
          text: '回测框架',
          items: [
            { text: '概述', link: '/backtest/' }
          ]
        }
      ],
      '/portfolio/': [
        {
          text: '投资组合优化',
          items: [
            { text: '概述', link: '/portfolio/' }
          ]
        }
      ],
      '/arxiv/': [
        {
          text: 'arXiv AI+金融论文',
          items: [
            { text: '论文索引', link: '/arxiv/' },
            { text: '标签分类', link: '/arxiv/tags/' }
          ]
        }
      ],
      '/resources/': [
        {
          text: '公开资源',
          items: [
            { text: '资源汇总', link: '/resources/' }
          ]
        }
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
