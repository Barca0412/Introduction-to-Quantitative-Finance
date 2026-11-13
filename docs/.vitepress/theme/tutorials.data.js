// Build-time index of all lectures under docs/tutorials/<nn-slug>/index.md.
// Pages read it to list lectures, show lecture metadata, and show
// "practised in these lectures" backlinks on knowledge-base pages.
import { createContentLoader } from 'vitepress'
import { normalizePath } from './paths.js'

const asList = (value) => (Array.isArray(value) ? value : value ? [value] : [])

export default createContentLoader('tutorials/*/index.md', {
  transform(pages) {
    return pages
      .filter((page) => page.frontmatter.tutorial && !page.frontmatter.tutorial.draft)
      .map((page) => {
        const t = page.frontmatter.tutorial
        return {
          url: page.url,
          slug: page.url.replace(/^\/tutorials\//, '').replace(/\/$/, ''),
          title: page.frontmatter.title || page.url,
          description: page.frontmatter.description || '',
          order: Number(t.order ?? 999),
          level: t.level || '',
          duration: t.duration || '',
          wiki: asList(t.wiki).map(normalizePath),
          reports: asList(t.reports),
          papers: asList(t.papers),
        }
      })
      .sort((a, b) => a.order - b.order || a.slug.localeCompare(b.slug))
  },
})
