import { withBase } from 'vitepress'
import config from '../../../../../scripts/site/search_model.json'
import { createSemanticSession } from './semanticSession.mjs'

export const SEARCH_MODEL = config.model
export const SEARCH_DIMENSION = config.dimension

export function createSemanticClient() {
  return createSemanticSession({
    makeWorker: () => new Worker(new URL('./semantic.worker.js', import.meta.url), { type: 'module' }),
    payload: () => ({ model: config.model, dimension: config.dimension,
      modelBase: new URL(withBase(`/models/${config.revision}/`), location.origin).href,
      wasmBase: new URL(withBase(`/models/runtime/transformers-${config.transformers}/`), location.origin).href,
    }),
  })
}
