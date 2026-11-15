// Verify immutable search resources and retain the site's normal 10 MiB ceiling.
import { readFile, readdir, stat } from 'node:fs/promises'
import { createHash } from 'node:crypto'
import { join, relative, resolve } from 'node:path'
const root = resolve(process.argv[2] || 'docs/.vitepress/dist')
const spec = JSON.parse(await readFile(new URL('./search_model.json', import.meta.url)))
const hash = (data) => createHash('sha256').update(data).digest('hex')
const allowed = `models/${spec.revision}/${spec.model}/onnx/model_quantized.onnx`
for (const [file, expected] of Object.entries(spec.files)) {
  const data = await readFile(join(root, 'models', spec.revision, spec.model, file))
  if (data.length !== expected.bytes || hash(data) !== expected.sha256) throw new Error(`Model verification failed: ${file}`)
}
for (const [file, expected] of Object.entries(spec.runtimeFiles)) {
  const data = await readFile(join(root, 'models', 'runtime', `transformers-${spec.transformers}`, file))
  if (data.length !== expected.bytes || hash(data) !== expected.sha256) throw new Error(`WASM verification failed: ${file}`)
}
let count = 0, total = 0
async function scan(dir) {
  for (const entry of await readdir(dir, { withFileTypes: true })) {
    const file = join(dir, entry.name)
    if (entry.isSymbolicLink()) throw new Error(`Symlinks are not publishable: ${file}`)
    if (entry.isDirectory()) { await scan(file); continue }
    const size = (await stat(file)).size; count++; total += size
    if (size > 10 * 1024 * 1024 && relative(root, file).replaceAll('\\', '/') !== allowed) throw new Error(`Unexpected file above 10 MiB: ${file} (${size})`)
  }
}
await scan(root)
console.log(`Build verified: ${count} files, ${(total / 1e6).toFixed(2)} MB; one pinned model-size exception.`)
