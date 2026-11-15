// Shared by build-time redirects and tutorial/method backlinks.
export const METHOD_ROUTES = {
  '/wiki': '/resources/',
  '/wiki/framework': '/resources/method-framework',
  '/wiki/data': '/resources/method-data',
  '/wiki/factors': '/resources/method-factors',
  '/wiki/factors/fundamental': '/resources/method-fundamental',
  '/wiki/factors/technical': '/resources/method-technical',
  '/wiki/factors/ml-factors': '/resources/method-ml-factors',
  '/wiki/factors/llm-factors': '/resources/method-llm-factors',
  '/wiki/backtest': '/resources/method-backtest',
  '/wiki/portfolio': '/resources/method-portfolio',
  '/wiki/sentiment': '/resources/method-sentiment',
}
export const LEGACY_ROUTES = {
  'guide/': 'resources/',
  'guide/framework': 'resources/method-framework',
  'data/': 'resources/method-data',
  'factors/': 'resources/method-factors',
  'factors/fundamental': 'resources/method-fundamental',
  'factors/technical': 'resources/method-technical',
  'factors/ml-factors': 'resources/method-ml-factors',
  'factors/llm-factors': 'resources/method-llm-factors',
  'backtest/': 'resources/method-backtest',
  'portfolio/': 'resources/method-portfolio',
  'sentiment/': 'resources/method-sentiment',
  ...Object.fromEntries(Object.entries(METHOD_ROUTES).map(([from, to]) => [
    from === '/wiki' || from === '/wiki/factors' ? `${from.slice(1)}/` : from.slice(1), to.slice(1),
  ])),
}
export const METHOD_NAV = [
  ['framework', '多因子投研框架'], ['data', '数据源与另类数据'], ['factors', '因子挖掘'],
  ['fundamental', '基本面因子'], ['technical', '技术因子'], ['ml-factors', '机器学习因子'],
  ['llm-factors', 'LLM 因子挖掘'], ['backtest', '回测框架'], ['portfolio', '投资组合优化'],
  ['sentiment', '投资者情绪与行为金融'],
].map(([slug, text]) => ({ text, link: `/resources/method-${slug}` }))
