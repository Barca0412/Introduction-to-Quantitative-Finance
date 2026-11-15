export const FACETS = {
  domain: { title: '金融领域', field: 'finance_domains', taxonomy: 'finance_domains' },
  task: { title: '任务', field: 'task_types', taxonomy: 'task_types' },
  method: { title: '方法', field: 'methods', taxonomy: 'methods' },
  type: { title: '论文类型', field: 'paper_type', taxonomy: 'paper_types' },
  market: { title: '市场', field: 'data_market', taxonomy: 'data_markets' },
  pub: { title: '发表状态' },
  discipline: { title: '学科', field: 'discipline' },
}
export const PUBLICATION = { published: '已发表', accepted: '已录用', 'working-paper': '工作论文', preprint: '预印本' }
export const DISCIPLINE = { cs: '计算机', 'finance-econ': '金融经济', interdisciplinary: '交叉', other: '其他' }
// Approved short labels from the static design; full labels come from taxonomy.json.
export const SHORT = {
  'asset-pricing': '资产定价', trading: '交易执行', 'portfolio-risk': '组合风险', derivatives: '衍生品', 'credit-banking': '信用银行',
  'corporate-finance': '公司金融', 'fin-nlp': '文本舆情', 'crypto-defi': '加密资产', 'macro-policy': '宏观政策',
  'insurance-household': '保险个人', 'market-structure': '市场结构', general: '通用金融', forecasting: '预测', pricing: '定价',
  decision: '交易决策', 'signal-mining': '因子挖掘', understanding: '理解问答', 'risk-assessment': '风险评估', generation: '生成',
  simulation: '市场模拟', 'multi-task': '多任务', 'llm-agent': '智能体', llm: '大模型', rl: '强化学习', 'deep-ts': '深度学习',
  graph: '图模型', generative: '生成模型', 'classic-ml': '传统机器学习', econometrics: '计量统计', other: '其他',
  method: '新方法', benchmark: '基准数据', empirical: '实证', system: '系统工具', survey: '综述', theory: '理论',
}
export function publication(paper) {
  if (paper.venue?.kind === 'working-paper' || paper.id.startsWith('nber:')) return 'working-paper'
  return PUBLICATION[paper.venue?.status] ? paper.venue.status : 'preprint'
}
export function entityPath(kind, entity) {
  return entity.page ? `/arxiv/${kind}?id=${encodeURIComponent(entity.page)}` : ''
}
export function values(paper, group) {
  if (group === 'pub') return [publication(paper)]
  const value = paper[FACETS[group].field]
  return Array.isArray(value) ? value : value ? [value] : []
}
export function initialState(search = '', latest = '') {
  const params = new URLSearchParams(search)
  const date = params.get('date') || params.get('d') || ''
  const ranges = ['day', 'week', 'month', 'all', '30d', '90d', 'year']
  return {
    range: ranges.includes(params.get('range')) ? params.get('range') : date ? 'day' : 'week',
    anchor: /^\d{4}-\d{2}-\d{2}$/.test(date) && !Number.isNaN(Date.parse(`${date}T00:00:00Z`)) ? date : latest,
    sort: ['rel', 'relevance'].includes(params.get('sort')) ? 'rel' : 'new',
    mode: params.get('mode') === 'sem' || params.get('search') === 'semantic' ? 'sem' : 'kw',
    query: params.get('q') || '', core: params.get('core') === '1', code: params.get('code') === '1',
    facets: Object.fromEntries(Object.keys(FACETS).map((key) => [key, (params.get(key) || '').split(',').filter(Boolean)])),
  }
}
export function stateQuery(state, latest) {
  const params = new URLSearchParams()
  if (state.range !== 'week') params.set('range', state.range)
  if (state.anchor && state.anchor !== latest) params.set('d', state.anchor)
  for (const [group, ids] of Object.entries(state.facets)) if (ids.length) params.set(group, ids.join(','))
  if (state.sort !== 'new') params.set('sort', state.sort)
  if (state.mode !== 'kw') params.set('mode', state.mode)
  if (state.query) params.set('q', state.query)
  if (state.core) params.set('core', '1')
  if (state.code) params.set('code', '1')
  return params.toString()
}
export const utc = (day) => Date.parse(`${day}T00:00:00Z`)
export const iso = (time) => new Date(time).toISOString().slice(0, 10)
export function dateSpan(range, anchor, latest) {
  if (!latest || !anchor) return ['', '9999-12-31']
  if (range === 'all') return ['', latest]
  if (range === 'day') return [anchor, anchor]
  if (range === 'week') {
    const start = utc(anchor) - ((new Date(utc(anchor)).getUTCDay() + 6) % 7) * 86400000
    return [iso(start), iso(Math.min(start + 6 * 86400000, utc(latest)))]
  }
  if (range === '30d' || range === '90d') return [iso(utc(latest) - (Number.parseInt(range) - 1) * 86400000), latest]
  if (range === 'year') return [`${latest.slice(0, 4)}-01-01`, latest]
  return [`${anchor.slice(0, 7)}-01`, latest]
}
export function keywordMatch(paper, query) {
  const text = [paper.title, paper.tldr_zh, paper.summary_zh, ...paper.authors.map((a) => a.name),
    ...(paper.affiliations || []), ...(paper.keywords || []), ...(paper.keywords_std || []).map((k) => k.label),
    paper.venue?.name || ''].join(' ').toLocaleLowerCase()
  const clean = query.trim().toLocaleLowerCase()
  if (!clean) return true
  return text.includes(clean) || clean.split(/[\s,，;；]+/).filter(Boolean).some((word) => text.includes(word))
}
export function matches(paper, state, span, { skip = '', scores = null } = {}) {
  if (paper.published_date < span[0] || paper.published_date > span[1]) return false
  if (state.core && paper.relevance !== 3) return false
  if (state.code && skip !== 'code' && !paper.has_code) return false
  for (const [group, ids] of Object.entries(state.facets)) {
    if (group !== skip && ids.length && !values(paper, group).some((id) => ids.includes(id))) return false
  }
  if (state.query.trim()) {
    if (scores) return Number.isFinite(scores[paper.id])
    return keywordMatch(paper, state.query)
  }
  return true
}
export function orderPapers(papers, sort, scores = null) {
  return [...papers].sort((a, b) => {
    if (scores) {
      const delta = (scores[b.id] ?? -Infinity) - (scores[a.id] ?? -Infinity)
      if (delta) return delta
    } else if (sort === 'rel') {
      const delta = (b.relevance || 0) - (a.relevance || 0)
      if (delta) return delta
    }
    return b.published_date.localeCompare(a.published_date) || b.id.localeCompare(a.id)
  })
}
export function matrixCounts(papers) {
  const counts = {}
  for (const paper of papers) for (const domain of paper.finance_domains) for (const task of paper.task_types) {
    const key = `${domain}|${task}`
    counts[key] = (counts[key] || 0) + 1
  }
  return { counts, max: Math.max(0, ...Object.values(counts)) }
}
