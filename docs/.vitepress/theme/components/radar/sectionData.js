import { withBase } from 'vitepress'

export const REPOSITORY = 'https://github.com/Barca0412/Introduction-to-Quantitative-Finance'
// The date collection began is historical, not the date of the current snapshot.
export const COLLECTION_START = '2026-11-01'
export const DAY = 86_400_000
export const isoDate = (date) => new Date(date).toISOString().slice(0, 10)
export const atUTC = (date) => Date.parse(`${String(date).slice(0, 10)}T00:00:00Z`)
export const monthDay = (date, withYear = false) => date ? `${withYear ? `${date.slice(0, 4)}/` : ''}${Number(date.slice(5, 7))}/${Number(date.slice(8, 10))}` : '—'
export const zhDate = (date, withYear = false) => date ? `${withYear ? `${date.slice(0, 4)} 年 ` : ''}${Number(date.slice(5, 7))} 月 ${Number(date.slice(8, 10))} 日` : '—'
export const dateRange = (from, until) => {
  const withYear = Boolean(from && until && from.slice(0, 4) !== until.slice(0, 4))
  return from === until ? zhDate(from) : `${zhDate(from, withYear)}至 ${zhDate(until, withYear)}`
}
export const weekStart = (date) => {
  const value = atUTC(date)
  return Number.isFinite(value) ? isoDate(value - ((new Date(value).getUTCDay() + 6) % 7) * DAY) : ''
}
export const weekday = (date) => ['周日', '周一', '周二', '周三', '周四', '周五', '周六'][new Date(atUTC(date)).getUTCDay()]
export const label = (taxonomy, group, id) => taxonomy?.[group]?.get(id) || id || '尚未分类'
// Display abbreviations from the approved static design; IDs and full labels stay in taxonomy.json.
const SHORT = {
  'asset-pricing': '资产定价', trading: '交易执行', 'portfolio-risk': '组合风险', derivatives: '衍生品', 'credit-banking': '信用银行',
  'corporate-finance': '公司金融', 'fin-nlp': '文本舆情', 'crypto-defi': '加密资产', 'macro-policy': '宏观政策', 'insurance-household': '保险个人',
  'market-structure': '市场结构', general: '通用金融', forecasting: '预测', pricing: '定价', decision: '交易决策', 'signal-mining': '因子挖掘',
  understanding: '理解问答', 'risk-assessment': '风险评估', generation: '生成', simulation: '市场模拟', 'multi-task': '多任务',
  'llm-agent': '智能体', llm: '大模型', rl: '强化学习', 'deep-ts': '深度学习', graph: '图模型', generative: '生成模型', 'classic-ml': '传统机器学习', econometrics: '计量统计', other: '其他',
}
export const shortLabel = (taxonomy, group, id) => SHORT[id] || label(taxonomy, group, id)
export const listUrl = (params = {}, paperId = '') => {
  const query = new URLSearchParams(Object.entries(params).filter(([, value]) => value !== undefined && value !== null && value !== ''))
  return `${withBase('/arxiv/papers')}${query.size ? `?${query}` : ''}${paperId ? `#paper=${encodeURIComponent(paperId)}` : ''}`
}
export const entityUrl = (kind, page) => page ? `${withBase(`/arxiv/${kind}`)}?id=${encodeURIComponent(page)}` : ''
export const rankNumbers = (items) => {
  let rank = 0
  return items.map((item, index) => {
    if (!index || items[index - 1].n !== item.n) rank = index + 1
    return rank
  })
}
export const periodOptions = (leaders) => ['30d', '90d', ...Object.keys(leaders?.periods || {}).filter((key) => /^\d{4}$/.test(key)).sort().reverse(), 'all'].filter((key) => leaders?.periods?.[key]).map((key) => ({
  key,
  name: key === '30d' ? '近 30 天' : key === '90d' ? '近 90 天' : key === 'all' ? '全部' : `${key} 年`,
}))
