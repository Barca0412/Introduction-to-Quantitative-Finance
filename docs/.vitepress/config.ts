import { defineConfig } from 'vitepress'
import { mkdirSync, writeFileSync, readdirSync, readFileSync, existsSync } from 'node:fs'
import { dirname, join } from 'node:path'
// Resource pages are generated from data/registry/; the sidebar lists the same pages.
import { loadRegistry, publishedPages } from '../../scripts/site/registry.mjs'
import { parse as parseYaml } from 'yaml'

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

const SITE_NAME = '量化研究入门'
const OG_IMAGE = `${SITE}og-cover.png`

// docs/wiki/factors/index.md -> 'wiki/factors/', docs/about.md -> 'about' (cleanUrls form)
const pagePath = (relativePath: string) =>
  relativePath.replace(/(^|\/)index\.md$/, '$1').replace(/\.md$/, '')

// Breadcrumb labels for the top-level sections.
// Lectures for the /tutorials/ sidebar, read from each lecture's frontmatter
// (same rule as tutorials.data.js: a `tutorial:` block and not draft).
const TUTORIALS_DIR = join(dirname(new URL(import.meta.url).pathname), '..', 'tutorials')
const LECTURES = (existsSync(TUTORIALS_DIR) ? readdirSync(TUTORIALS_DIR) : [])
  .filter((name) => existsSync(join(TUTORIALS_DIR, name, 'index.md')))
  .map((name) => {
    const fm = readFileSync(join(TUTORIALS_DIR, name, 'index.md'), 'utf8').match(/^---\n([\s\S]*?)\n---/)
    const data = fm ? parseYaml(fm[1]) ?? {} : {}
    return { name, title: data.title ?? name, t: data.tutorial }
  })
  .filter((l) => l.t && !l.t.draft)
  .sort((a, b) => (a.t.order ?? 999) - (b.t.order ?? 999) || a.name.localeCompare(b.name))

// Resource pages with at least one reviewed entry (same rule as gen_resources.mjs).
const REGISTRY = loadRegistry()
const RESOURCE_PAGES = publishedPages(REGISTRY)

const SECTION_NAMES: Record<string, string> = {
  tutorials: '教程',
  wiki: '知识库',
  library: '研报与论文',
  arxiv: '论文雷达',
  resources: '资源',
  about: '关于',
  careers: '求职'
}

// Search-console verification tokens come from repository variables at build time;
// unset means no tag. They are public by design (they end up in the HTML).
const siteVerification = [
  ['google-site-verification', process.env.GOOGLE_SITE_VERIFICATION],
  ['msvalidate.01', process.env.BING_SITE_VERIFICATION],
  ['baidu-site-verification', process.env.BAIDU_SITE_VERIFICATION]
]
  .filter(([, content]) => content && content.trim())
  .map(([name, content]) => ['meta', { name, content: (content as string).trim() }] as [string, Record<string, string>])

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
  title: SITE_NAME,
  titleTemplate: `:title | ${SITE_NAME}`,
  description: '中文开源量化知识库：项目式多因子量化教程、因子与回测知识库、研报与论文目录，以及每天更新的 AI × 金融论文雷达。',
  // LaTeX in markdown ($…$ and $$…$$), rendered at build time by markdown-it-mathjax3.
  markdown: {
    math: true
  },
  // URLs without .html; canonical, og:url and the sitemap all use this form.
  cleanUrls: true,
  // Per-page "last updated" from git history; also feeds <lastmod> in the sitemap.
  // CI checks out full history (fetch-depth: 0) so these are real edit dates.
  lastUpdated: true,
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
  transformHead: ({ pageData, title, description }) => {
    if (pageData.isNotFound) return []
    const path = pagePath(pageData.relativePath)
    const url = `${SITE}${path}`
    const isHome = path === ''
    const head: [string, Record<string, string>, string?][] = [
      ['link', { rel: 'canonical', href: url }],
      ['meta', { property: 'og:type', content: isHome ? 'website' : 'article' }],
      ['meta', { property: 'og:site_name', content: SITE_NAME }],
      ['meta', { property: 'og:title', content: title }],
      ['meta', { property: 'og:description', content: description }],
      ['meta', { property: 'og:url', content: url }],
      ['meta', { property: 'og:image', content: OG_IMAGE }],
      ['meta', { property: 'og:image:alt', content: `${SITE_NAME}：项目式量化教程与 AI × 金融论文雷达` }],
      ['meta', { property: 'og:locale', content: 'zh_CN' }],
      ['meta', { name: 'twitter:card', content: 'summary_large_image' }],
      ['meta', { name: 'twitter:title', content: title }],
      ['meta', { name: 'twitter:description', content: description }],
      ['meta', { name: 'twitter:image', content: OG_IMAGE }]
    ]

    const graph: Record<string, unknown>[] = []
    // Breadcrumb: 首页 > section > page (section pages stop at the section).
    const section = path.split('/')[0]
    if (!isHome && SECTION_NAMES[section]) {
      const crumbs = [{ name: SITE_NAME, url: SITE }, { name: SECTION_NAMES[section], url: `${SITE}${section}${section === 'about' ? '' : '/'}` }]
      if (path !== section && path !== `${section}/`) crumbs.push({ name: pageData.title || title, url })
      graph.push({
        '@type': 'BreadcrumbList',
        itemListElement: crumbs.map((c, k) => ({ '@type': 'ListItem', position: k + 1, name: c.name, item: c.url }))
      })
    }
    // Knowledge-base concept pages with a `wiki:` block are TechArticles too.
    const wiki = pageData.frontmatter.wiki
    if (wiki && path.startsWith('wiki/')) {
      graph.push({
        '@type': 'TechArticle',
        headline: pageData.title,
        description,
        url,
        inLanguage: 'zh-CN',
        author: { '@type': 'Organization', name: '湖南大学金融科技协会 Quant Group' },
        license: 'https://creativecommons.org/licenses/by/4.0/',
        ...(wiki.level ? { proficiencyLevel: wiki.level } : {}),
        ...(pageData.lastUpdated ? { dateModified: new Date(pageData.lastUpdated).toISOString() } : {}),
        isPartOf: { '@type': 'WebSite', name: SITE_NAME, url: SITE }
      })
    }
    // Lectures are TechArticles with their author, level and dates.
    const tutorial = pageData.frontmatter.tutorial
    if (tutorial && !tutorial.draft) {
      graph.push({
        '@type': 'TechArticle',
        headline: pageData.title,
        description,
        url,
        inLanguage: 'zh-CN',
        author: { '@type': 'Organization', name: tutorial.author || '湖南大学金融科技协会 Quant Group' },
        ...(tutorial.level ? { proficiencyLevel: tutorial.level } : {}),
        ...(pageData.lastUpdated ? { dateModified: new Date(pageData.lastUpdated).toISOString() } : {}),
        isPartOf: { '@type': 'WebSite', name: SITE_NAME, url: SITE }
      })
    }
    if (graph.length) {
      head.push(['script', { type: 'application/ld+json' }, JSON.stringify({ '@context': 'https://schema.org', '@graph': graph })])
    }
    return head
  },

  head: [
    ...siteVerification,
    ['meta', { name: 'author', content: '湖南大学金融科技协会 Quant Group' }],
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
          items: LECTURES.map((l) => ({ text: l.title, link: `/tutorials/${l.name}/` }))
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
          text: '资源',
          link: '/resources/',
          collapsed: false,
          items: [
            ...RESOURCE_PAGES.map((p) => ({ text: p.title, link: `/resources/${p.key}` })),
            ...(RESOURCE_PAGES.length && REGISTRY.options.credits_page ? [{ text: '致谢与来源', link: '/resources/credits' }] : [])
          ]
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
      provider: 'local',
      options: {
        translations: {
          button: { buttonText: '搜索', buttonAriaLabel: '搜索' },
          modal: {
            displayDetails: '显示详情',
            resetButtonTitle: '清除',
            backButtonTitle: '关闭',
            noResultsText: '没有找到相关结果',
            footer: { selectText: '选择', navigateText: '切换', closeText: '关闭' }
          }
        }
      }
    },

    // VitePress' own UI labels in Chinese.
    sidebarMenuLabel: '菜单',
    returnToTopLabel: '回到顶部',
    darkModeSwitchLabel: '外观',
    lightModeSwitchTitle: '切换到浅色模式',
    darkModeSwitchTitle: '切换到深色模式',
    langMenuLabel: '语言',

    lastUpdated: {
      text: '最后更新',
      formatOptions: { dateStyle: 'medium' }
    },

    docFooter: { prev: '上一页', next: '下一页' },

    outline: {
      level: [2, 3],
      label: '目录'
    }
  }
})
