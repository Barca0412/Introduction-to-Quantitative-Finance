import test from 'node:test'
import assert from 'node:assert/strict'
import { createServer } from 'node:http'
import { mkdtemp, mkdir, writeFile, rm } from 'node:fs/promises'
import { tmpdir } from 'node:os'
import { join } from 'node:path'
import { fileURLToPath } from 'node:url'
import { execFileSync, spawn } from 'node:child_process'

const script = fileURLToPath(new URL('../check_release_freshness.py', import.meta.url))

test('release gate refuses old builds, stale commits and unreadable metadata', async () => {
  const root = await mkdtemp(join(tmpdir(), 'quant-release-test-'))
  const repo = join(root, 'checkout'), remote = join(root, 'origin.git'), artifact = join(root, 'site'), template = join(root, 'template')
  for (const folder of [repo, artifact, template]) await mkdir(folder)
  const git = (...args) => execFileSync('git', ['-c', 'core.hooksPath=/dev/null', '-c', 'commit.gpgsign=false', '-c', 'user.name=Deployment Test', '-c', 'user.email=test@example.invalid', ...args], { cwd: repo, encoding: 'utf8', stdio: ['ignore', 'pipe', 'pipe'] }).trim()
  git('init', '--bare', `--template=${template}`, remote)
  git('init', '--initial-branch=main', `--template=${template}`)
  git('commit', '--allow-empty', '-m', 'First build')
  git('remote', 'add', 'origin', remote)
  git('push', 'origin', 'main')
  const commit = git('rev-parse', 'HEAD')
  const local = { commit, built_at: '2026-11-15T12:00:00+00:00' }
  await writeFile(join(artifact, 'build-info.json'), JSON.stringify(local))
  let status = 404, payload = '', requestedPath = ''
  const server = createServer((req, res) => {
    requestedPath = new URL(req.url, 'http://localhost').pathname
    res.writeHead(status, { 'Content-Type': 'application/json' })
    res.end(typeof payload === 'string' ? payload : JSON.stringify(payload))
  })
  await new Promise(resolve => server.listen(0, '127.0.0.1', resolve))
  const target = `http://127.0.0.1:${server.address().port}/Introduction-to-Quantitative-Finance`
  const check = () => new Promise((resolve, reject) => {
    const child = spawn(process.env.SITE_PYTHON || 'python3', [script, artifact, target], { cwd: repo })
    let output = ''
    child.stdout.on('data', data => output += data)
    child.stderr.on('data', data => output += data)
    child.on('error', reject)
    child.on('close', code => resolve({ code, output }))
  })
  try {
    const first = await check()
    assert.equal(first.code, 0, first.output)
    assert.match(first.output, /first migration/)
    assert.equal(requestedPath, '/Introduction-to-Quantitative-Finance/build-info.json')

    status = 200
    payload = { commit, built_at: '2026-11-14T12:00:00+00:00' }
    const newer = await check()
    assert.equal(newer.code, 0, newer.output)

    // The same instant with a different UTC offset is a valid retry.
    payload = { commit, built_at: '2026-11-15T20:00:00+08:00' }
    const retry = await check()
    assert.equal(retry.code, 0, retry.output)

    // Simulate rerunning an older deployment job after a newer data build is live.
    payload = { commit, built_at: '2026-11-16T12:00:00+00:00' }
    const oldBuild = await check()
    assert.notEqual(oldBuild.code, 0)
    assert.match(oldBuild.output, /built before the deployed site/)

    for (const bad of ['<html>unexpected fallback</html>', {}, { commit }, { commit, built_at: '2026-11-15T12:00:00' }]) {
      payload = bad
      const invalid = await check()
      assert.notEqual(invalid.code, 0)
      assert.match(invalid.output, /invalid build metadata/)
    }
    status = 503
    const unavailable = await check()
    assert.notEqual(unavailable.code, 0)
    assert.match(unavailable.output, /HTTP 503/)

    // Advance a real local Git remote; the old artifact must fail even on a 404 site.
    git('commit', '--allow-empty', '-m', 'Newer main')
    git('push', 'origin', 'main')
    status = 404
    const oldCommit = await check()
    assert.notEqual(oldCommit.code, 0)
    assert.match(oldCommit.output, /no longer the current origin\/main HEAD/)

    await writeFile(join(artifact, 'build-info.json'), JSON.stringify({ ...local, commit: git('rev-parse', 'HEAD') }))
    await new Promise(resolve => server.close(resolve))
    const unreachable = await check()
    assert.notEqual(unreachable.code, 0)
    assert.match(unreachable.output, /network request failed/)
  } finally {
    if (server.listening) await new Promise(resolve => server.close(resolve))
    await rm(root, { recursive: true, force: true })
  }
})
