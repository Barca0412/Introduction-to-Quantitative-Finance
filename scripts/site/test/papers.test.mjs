import test from 'node:test'
import assert from 'node:assert/strict'
import { initialState, stateQuery, dateSpan, matches, matrixCounts, publication, entityPath, orderPapers, keywordMatch } from '../../../docs/.vitepress/theme/components/radar/paperFilters.mjs'
import { createSemanticSession } from '../../../docs/.vitepress/theme/components/radar/semanticSession.mjs'

function paper(id, date, domains, tasks, relevance = 2) {
  return { id, published_date: date, title: `Paper ${id}`, authors: [{ name: 'Wei Zhang' }],
    affiliations: ['南洋理工大学'], finance_domains: domains, task_types: tasks, methods: ['llm'],
    paper_type: 'method', data_market: [], relevance, has_code: false, tldr_zh: '金融风险预测' }
}

test('day, week, month, year and rolling dates use dataset date across a year boundary', () => {
  assert.deepEqual(dateSpan('day', '2026-12-31', '2027-01-03'), ['2026-12-31', '2026-12-31'])
  assert.deepEqual(dateSpan('week', '2027-01-03', '2027-01-03'), ['2026-12-28', '2027-01-03'])
  assert.deepEqual(dateSpan('week', '2026-12-24', '2027-01-03'), ['2026-12-21', '2026-12-27'])
  assert.deepEqual(dateSpan('month', '2027-01-03', '2027-01-03'), ['2027-01-01', '2027-01-03'])
  assert.deepEqual(dateSpan('year', '2027-01-03', '2027-01-03'), ['2027-01-01', '2027-01-03'])
  assert.deepEqual(dateSpan('30d', '2027-01-03', '2027-01-03'), ['2026-12-05', '2027-01-03'])
  assert.deepEqual(dateSpan('90d', '2027-01-03', '2027-01-03'), ['2026-10-06', '2027-01-03'])
  assert.deepEqual(dateSpan('all', '2027-01-03', '2027-01-03'), ['', '2027-01-03'])
})

test('shared deep links and aliases survive a state/URL round trip', () => {
  const state = initialState('?range=all&domain=credit-banking,fin-nlp&task=forecasting&core=1&code=1&mode=sem&q=fraud&sort=rel', '2026-11-14')
  assert.deepEqual(initialState(stateQuery(state, '2026-11-14'), '2026-11-14'), state)
  assert.equal(initialState('?date=2026-11-01', '2026-11-14').range, 'day')
  assert.equal(initialState('?d=2026-11-01&search=semantic', '2026-11-14').mode, 'sem')
  assert.equal(initialState('?range=broken&d=bad', '2026-11-14').anchor, '2026-11-14')
})

test('every domain/task grid count equals its all-history linked paper list', () => {
  const rows = [paper('1', '2020-01-01', ['a'], ['x']), paper('2', '2026-11-14', ['a', 'b'], ['x', 'y'], 3),
    paper('3', '2025-02-01', ['b'], ['y']), paper('4', '2026-11-13', ['c'], ['x', 'z']), paper('5', '2024-04-12', ['a'], ['z'])]
  const grid = matrixCounts(rows)
  assert.equal(Object.keys(grid.counts).length, 7)
  for (const [cell, count] of Object.entries(grid.counts)) {
    const [domain, task] = cell.split('|')
    const state = initialState(`range=all&domain=${domain}&task=${task}`, '2026-11-14')
    assert.equal(rows.filter((row) => matches(row, state, dateSpan(state.range, state.anchor, '2026-11-14'))).length, count, cell)
  }
})

test('facet selections OR within one group and AND between groups; keyword search uses public text', () => {
  const rows = [paper('1', '2026-11-14', ['a'], ['x']), paper('2', '2026-11-14', ['b'], ['y'], 3), paper('3', '2026-11-14', ['c'], ['x'])]
  const state = initialState('range=all&domain=a,b&task=x', '2026-11-14')
  assert.deepEqual(rows.filter((row) => matches(row, state, ['', '2026-11-14'])).map((row) => row.id), ['1'])
  assert.equal(keywordMatch(rows[0], '南洋理工'), true)
  assert.equal(keywordMatch(rows[0], 'Wei Zhang'), true)
  assert.equal(keywordMatch({ ...rows[0], abstract: 'secret abstract text' }, 'secret abstract'), false)
})

test('NBER is a working paper; different people with the same name link by identity only', () => {
  assert.equal(publication({ id: 'nber:w35987', venue: { name: 'NBER 工作论文' } }), 'working-paper')
  assert.equal(publication({ id: 'doi:10.1145/example', venue: { status: 'accepted' } }), 'accepted')
  assert.equal(entityPath('author', { name: 'Wei Zhang', page: 'a123' }), '/arxiv/author?id=a123')
  assert.equal(entityPath('author', { name: 'Wei Zhang', page: 'a456' }), '/arxiv/author?id=a456')
  assert.equal(entityPath('author', { id: 'A789', name: 'Wei Zhang', page: '' }), '')
  assert.equal(entityPath('institution', { page: 'name:a/b' }), '/arxiv/institution?id=name%3Aa%2Fb')
})

test('semantic order is deterministic and excludes papers without a vector', () => {
  const rows = [paper('1', '2026-11-14', [], []), paper('2', '2026-11-13', [], [], 3), paper('3', '2026-11-12', [], [])]
  const state = initialState('range=all&mode=sem&q=trading', '2026-11-14')
  const scores = { 1: .2, 2: .7 }
  const found = rows.filter((row) => matches(row, state, ['', '2026-11-14'], { scores }))
  assert.deepEqual(orderPapers(found, 'new', scores).map((row) => row.id), ['2', '1'])
})

function mockWorker() {
  return { messages: [], terminated: false, postMessage(message) { this.messages.push(message) }, terminate() { this.terminated = true }, reply(id, vector) { this.onmessage({ data: { id, vector } }) } }
}
test('semantic timeout terminates stuck worker, rejects pending request, and retry creates a fresh worker', async () => {
  const workers = []
  const client = createSemanticSession({ makeWorker: () => { const worker = mockWorker(); workers.push(worker); return worker }, payload: () => ({}), timeoutMs: 10 })
  await assert.rejects(client.embed('slow query'), /timed out/)
  assert.equal(workers[0].terminated, true)
  const retry = client.embed('fresh query')
  assert.equal(workers.length, 2)
  const id = workers[1].messages[0].id
  workers[0].reply(id - 1, [99])
  workers[1].reply(id, [.2, .3])
  assert.deepEqual(await retry, [.2, .3])
  client.stop()
})
test('out-of-order worker replies are correlated; stop rejects all pending work', async () => {
  const worker = mockWorker()
  const client = createSemanticSession({ makeWorker: () => worker, payload: () => ({}), timeoutMs: 1000 })
  const old = client.embed('old'), current = client.embed('current')
  worker.reply(worker.messages[1].id, [2]); worker.reply(worker.messages[0].id, [1])
  assert.deepEqual(await current, [2]); assert.deepEqual(await old, [1])
  const pending = client.embed('pending')
  client.stop()
  await assert.rejects(pending, /cancelled/)
  assert.equal(worker.terminated, true)
})
