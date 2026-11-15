import test from 'node:test'
import assert from 'node:assert/strict'
import { readFileSync } from 'node:fs'
import { parse } from 'yaml'
import { createServer } from 'node:http'
import { mkdtemp, mkdir, writeFile, rm } from 'node:fs/promises'
import { tmpdir } from 'node:os'
import { join } from 'node:path'
import { spawn } from 'node:child_process'
const workflow = parse(readFileSync(new URL('../../../.github/workflows/deploy-site.yml', import.meta.url), 'utf8'))
const daily = parse(readFileSync(new URL('../../../.github/workflows/daily-arxiv.yml', import.meta.url), 'utf8'))
test('reusable deployment receives its explicit key and publishes independent targets', () => {
  assert.ok('DEPLOY_SSH_KEY' in workflow.on.workflow_call.secrets)
  assert.equal(daily.jobs['deploy-site'].secrets.DEPLOY_SSH_KEY, '${{ secrets.DEPLOY_SSH_KEY }}')
  assert.equal(workflow.jobs['deploy-pages'].needs, 'build')
  assert.equal(workflow.jobs['deploy-server'].needs, 'build')
  assert.equal(workflow.concurrency.group, 'site-release')
  assert.equal(workflow.concurrency['cancel-in-progress'], false)
  assert.ok(!workflow.jobs.build.steps.some(step => /(?:configure-pages|upload-pages-artifact|deploy-pages)@/.test(step.uses || '')))
  const pages = workflow.jobs['deploy-pages'].steps
  assert.ok(pages.some(step => step.uses === 'actions/configure-pages@v5'))
  assert.ok(pages.some(step => step.uses === 'actions/upload-pages-artifact@v3'))
  for (const name of ['deploy-pages', 'deploy-server']) {
    const steps = workflow.jobs[name].steps
    assert.equal(steps.find(step => step.uses === 'actions/checkout@v4').with.ref, '${{ needs.build.outputs.source_ref }}')
    assert.equal(steps.find(step => step.uses === 'actions/download-artifact@v4').with.name, '${{ needs.build.outputs.artifact_name }}')
    assert.ok(steps.some(step => (step.run || '').includes('check_release_freshness.py')))
  }
})
test('server verification compares the exact public manifest', () => {
  const script = readFileSync(new URL('../verify_deployment.py', import.meta.url), 'utf8')
  assert.match(script, /hashlib.sha256\(actual\).*digest/)
  const deploy = readFileSync(new URL('../deploy_server.sh', import.meta.url), 'utf8')
  assert.match(deploy, /StrictHostKeyChecking=yes/)
  assert.doesNotMatch(deploy, /StrictHostKeyChecking=no|set -x/)
})
test('deployment verification rejects old UI even with the correct data manifest', async () => {
  const root = await mkdtemp(join(tmpdir(), 'quant-deploy-test-'))
  const pages = ['/', '/tutorials/', '/resources/', '/library/', '/contact', '/arxiv/', '/arxiv/papers', '/arxiv/trends', '/arxiv/people', '/arxiv/about']
  const files = new Map(pages.map(path => [path, `<html><body>${path}: new UI</body></html>`]))
  files.set('/arxiv-data/manifest.json', JSON.stringify({ latest_published_date: '2026-11-14' }))
  files.set('/build-info.json', JSON.stringify({ commit: 'tested-commit', base: '/' }))
  for (const [path, contents] of files) {
    const name = path.endsWith('.json') ? path : path.endsWith('/') ? path + 'index.html' : path + '.html'
    const target = join(root, name)
    await mkdir(join(target, '..'), { recursive: true })
    await writeFile(target, contents)
  }
  let oldUi = false
  const server = createServer((req, res) => {
    const path = new URL(req.url, 'http://localhost').pathname
    res.setHeader('Content-Type', path.endsWith('.json') ? 'application/json' : 'text/html')
    res.end(oldUi && path === '/' ? '<html>old UI</html>' : files.get(path))
  })
  await new Promise(resolve => server.listen(0, '127.0.0.1', resolve))
  const verify = () => new Promise(resolve => {
    const child = spawn(process.env.SITE_PYTHON || 'python3', ['scripts/site/verify_deployment.py', root, `http://127.0.0.1:${server.address().port}`])
    let output = ''
    child.stdout.on('data', data => output += data)
    child.stderr.on('data', data => output += data)
    child.on('close', code => resolve({ code, output }))
  })
  try {
    const good = await verify()
    assert.equal(good.code, 0, good.output)
    oldUi = true
    const stale = await verify()
    assert.notEqual(stale.code, 0)
    assert.match(stale.output, /published page differs/)
  } finally {
    await new Promise(resolve => server.close(resolve))
    await rm(root, { recursive: true, force: true })
  }
})
