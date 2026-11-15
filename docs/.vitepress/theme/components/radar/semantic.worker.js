// Lazy, same-origin inference. Keeping inference in a Worker lets a timeout
// terminate downloads or a stuck WASM session without blocking the interface.
import { env, pipeline } from '@xenova/transformers'

let extractorPromise
let queue = Promise.resolve()

self.onmessage = ({ data }) => {
  queue = queue.then(async () => {
    const { id, query, model, modelBase, wasmBase, dimension } = data
    try {
      if (!extractorPromise) {
        env.allowRemoteModels = false
        env.allowLocalModels = true
        env.localModelPath = modelBase
        env.useBrowserCache = true
        env.backends.onnx.wasm.wasmPaths = wasmBase
        env.backends.onnx.wasm.numThreads = 1
        env.backends.onnx.wasm.proxy = false
        extractorPromise = pipeline('feature-extraction', model, {
          quantized: true,
          local_files_only: true,
        }).catch((error) => { extractorPromise = null; throw error })
      }
      const extractor = await extractorPromise
      const result = await extractor(query, { pooling: 'mean', normalize: true })
      const vector = Float32Array.from(result.data)
      if (vector.length !== dimension || !vector.every(Number.isFinite)) {
        throw new Error('Unexpected embedding dimensions')
      }
      self.postMessage({ id, vector }, [vector.buffer])
    } catch (error) {
      self.postMessage({ id, error: error?.message || 'Model unavailable' })
    }
  })
}
