// Build-time counts and file indexes. Never copies the design preview's snapshots.
import { readFileSync, readdirSync } from 'node:fs'
import { join, basename, extname } from 'node:path'
import { ROOT, walk, repoPath, githubUrl, collator } from '../../../scripts/site/lib.mjs'
const resourceFile = join(ROOT, 'docs/resources/index.md')
function library(root, depth) {
 const files = walk(join(ROOT, ...root)).filter(f => extname(f).toLowerCase() === '.pdf')
 const groups = new Map()
 for (const f of files) { const parts = repoPath(f); const name = parts.slice(depth,-1).join(' / ') || '其他'; if (!groups.has(name)) groups.set(name, {name, url: githubUrl('tree', parts.slice(0,-1)), items:[]}); groups.get(name).items.push({title:basename(f,extname(f)),url:githubUrl('blob',parts)}) }
 return {count: files.length, groups:[...groups.values()].sort((a,b)=>collator.compare(a.name,b.name)).map(g=>({...g,items:g.items.sort((a,b)=>collator.compare(a.title,b.title))}))}
}
export default {
 watch: ['../../resources/index.md', '../../resources/method-*.md', '../../../资料/卖方金工研报/**/*.pdf', '../../../论文/**/*.pdf'],
 load() {
  const text = readFileSync(resourceFile,'utf8'); const sections = text.split(/^## /m).slice(1)
  const resourceCategories = Object.fromEntries(sections.map(s => [s.split('\n')[0].trim(), [...s.matchAll(/^\|\s*\[[^\]]+\]\(https?:/gm)].length]).filter(([,count])=>count))
  const counts = Object.values(resourceCategories)
  return {resources:counts.reduce((a,b)=>a+b,0),categories:counts.length,resourceCategories,methods:readdirSync(join(ROOT,'docs/resources')).filter(f=>/^method-.*\.md$/.test(f)).length,reports:{count:library(['资料','卖方金工研报'],2).count},papers:{count:library(['论文'],1).count}}
 }
}
