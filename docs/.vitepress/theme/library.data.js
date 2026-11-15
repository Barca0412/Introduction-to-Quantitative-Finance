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
 watch: ['../../../资料/卖方金工研报/**/*.pdf', '../../../论文/**/*.pdf'],
 load() { return { reports: library(['资料','卖方金工研报'],2), papers: library(['论文'],1) } }
}
