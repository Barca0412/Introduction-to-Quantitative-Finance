// Prepare immutable, same-origin assets. No model binaries are committed to git.
import { createHash } from 'node:crypto'
import { copyFile, mkdir, readFile, writeFile } from 'node:fs/promises'
import { dirname, join, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'

const here = dirname(fileURLToPath(import.meta.url))
const root = resolve(here, '../..')
const spec = JSON.parse(await readFile(join(here, 'search_model.json'), 'utf8'))
const transformers = join(root, 'node_modules/@xenova/transformers')
const installed = JSON.parse(await readFile(join(transformers, 'package.json'), 'utf8'))
if (installed.version !== spec.transformers) throw new Error(`Expected Transformers.js ${spec.transformers}; got ${installed.version}`)
const output = join(root, 'docs/public/models')
const modelDir = join(output, spec.revision, spec.model)
const caches = [process.env.SEARCH_MODEL_CACHE_DIR, join(transformers, '.cache', spec.model)].filter(Boolean)
const sha256 = (bytes) => createHash('sha256').update(bytes).digest('hex')
const valid = (bytes, expected) => bytes.length === expected.bytes && sha256(bytes) === expected.sha256

async function download(url, expected) {
  const response = await fetch(url, { signal: AbortSignal.timeout(120_000) })
  if (!response.ok) throw new Error(`Model asset download failed (${response.status}): ${url}`)
  const bytes = Buffer.from(await response.arrayBuffer())
  if (!valid(bytes, expected)) throw new Error(`Model asset failed SHA256/size verification: ${url}`)
  return bytes
}

for (const [file, expected] of Object.entries(spec.files)) {
  const destination = join(modelDir, file)
  let bytes
  for (const candidate of [destination, ...caches.map((cache) => join(cache, file))]) {
    try {
      const cached = await readFile(candidate)
      if (valid(cached, expected)) { bytes = cached; break }
    } catch (error) { if (error.code !== 'ENOENT') throw error }
  }
  if (!bytes) bytes = await download(`https://huggingface.co/${spec.model}/resolve/${spec.revision}/${file}`, expected)
  await mkdir(dirname(destination), { recursive: true })
  await writeFile(destination, bytes)
  console.log(`Verified ${file}: ${bytes.length} bytes`)
}

const runtimeDir = join(output, 'runtime', `transformers-${spec.transformers}`)
await mkdir(runtimeDir, { recursive: true })
for (const file of spec.wasmFiles) {
  const bytes = await readFile(join(transformers, 'dist', file))
  if (!valid(bytes, spec.runtimeFiles[file])) throw new Error(`WASM runtime failed verification: ${file}`)
  await writeFile(join(runtimeDir, file), bytes)
}

// The license source files are checked in, so offline builds do not need a second
// network dependency. --refresh-model-card retrieves the pinned upstream copy.
const licenseDir = join(here, 'search-model-licenses')
if (process.argv.includes('--refresh-model-card')) {
  await writeFile(join(licenseDir, 'MODEL_CARD.md'), await download(spec.modelCard.url, spec.modelCard))
}
const card = await readFile(join(licenseDir, 'MODEL_CARD.md'))
if (!valid(card, spec.modelCard)) throw new Error('Stored model card failed verification')
await writeFile(join(modelDir, 'README.md'), card)
await copyFile(join(licenseDir, 'APACHE-2.0.txt'), join(modelDir, 'LICENSE.txt'))
await copyFile(join(licenseDir, 'APACHE-2.0.txt'), join(runtimeDir, 'TRANSFORMERS-LICENSE.txt'))
await copyFile(join(licenseDir, 'ONNXRUNTIME-LICENSE'), join(runtimeDir, 'ONNXRUNTIME-LICENSE.txt'))
await copyFile(join(licenseDir, 'SOURCES.md'), join(output, 'SOURCES.md'))
await writeFile(join(output, 'manifest.json'), JSON.stringify(spec, null, 2) + '\n')
console.log(`Search assets ready in ${output}`)
