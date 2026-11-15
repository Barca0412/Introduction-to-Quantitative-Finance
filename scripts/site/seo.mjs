import { mkdirSync, writeFileSync } from 'node:fs'
import { dirname, join } from 'node:path'
import { LEGACY_ROUTES } from './routes.mjs'

export function siteOrigin(value = 'https://quant.hfthnu.com') {
  const url = new URL(value)
  if (!['http:', 'https:'].includes(url.protocol) || url.pathname !== '/' || url.search || url.hash) throw new Error('SITE_URL must be an HTTP(S) origin without a base path')
  return url.origin
}
export function siteBase(value = '/Introduction-to-Quantitative-Finance/') {
  if (!/^\/(?:[A-Za-z0-9_-]+\/)*$/.test(value)) throw new Error('SITE_BASE must start and end with /')
  return value
}
export function redirectPage(target, base, origin) {
  const local = base + target
  const canonical = `${origin}/${target}`
  return `<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><title>页面已移动</title><link rel="canonical" href="${canonical}"><meta name="robots" content="noindex"><meta http-equiv="refresh" content="0; url=${local}"><script>location.replace(${JSON.stringify(local)} + location.search + location.hash)</script></head><body><p>页面已移动到 <a href="${local}">新位置</a>。</p></body></html>`
}
export function writeSeoFiles(outDir, base, origin) {
  for (const [from, to] of Object.entries(LEGACY_ROUTES)) {
    const files = from.endsWith('/') ? [join(outDir, from, 'index.html')] : [join(outDir, `${from}.html`), join(outDir, from, 'index.html')]
    for (const file of files) { mkdirSync(dirname(file), { recursive: true }); writeFileSync(file, redirectPage(to, base, origin)) }
  }
  writeFileSync(join(outDir, 'robots.txt'), `User-agent: *\nAllow: /\n\nSitemap: ${origin}/sitemap.xml\n`)
  writeFileSync(join(outDir, 'llms.txt'), `# 量化研究入门与AI+金融资源站\n\n> 量化研究的开源资源与研报论文、AI × 金融前沿论文，以及和 AI 一起学的量化研究教程。\n\n## 网站栏目\n\n- 首页：${origin}/\n- 教程：${origin}/tutorials/\n- 开源资源清单与研究方法：${origin}/resources/\n- 研报与论文：${origin}/library/\n- AI × 金融论文雷达 FinPaperRadar：${origin}/arxiv/\n- 投稿与联系：${origin}/contact\n- 关于与引用：${origin}/about\n- 源码：https://github.com/Barca0412/Introduction-to-Quantitative-Finance\n- 数据下载镜像：https://github.com/Barca0412/Introduction-to-Quantitative-Finance/releases/tag/radar-data\n\n## 引用\n\n请使用上述主站网址，并注明湖南大学金融科技协会 Quant Group。论文观点请引用论文页面中的原始来源。\n\nThank you to arXiv for use of its open access interoperability.\n`)
}
