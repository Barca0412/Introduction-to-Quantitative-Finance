/** A testable Worker session: replies are correlated by id; timeout terminates it. */
export function createSemanticSession({ makeWorker, payload, timeoutMs = 60_000 }) {
  let worker
  let request = 0
  const pending = new Map()
  function stop(reason = 'Search cancelled') {
    worker?.terminate()
    worker = null
    for (const item of pending.values()) {
      clearTimeout(item.timer)
      item.reject(new Error(reason))
    }
    pending.clear()
  }
  function ensureWorker() {
    if (worker) return
    worker = makeWorker()
    worker.onmessage = ({ data }) => {
      const item = pending.get(data.id)
      if (!item) return
      pending.delete(data.id)
      clearTimeout(item.timer)
      if (data.error) item.reject(new Error(data.error))
      else item.resolve(data.vector)
    }
    worker.onerror = (event) => {
      event.preventDefault?.()
      stop('Search model could not start')
    }
  }
  return {
    embed(query) {
      return new Promise((resolve, reject) => {
        let id
        try {
          ensureWorker()
          id = ++request
          pending.set(id, { resolve, reject, timer: setTimeout(() => stop('Search model timed out'), timeoutMs) })
          worker.postMessage({ ...payload(), id, query })
        } catch (error) {
          const item = pending.get(id)
          if (item) clearTimeout(item.timer)
          pending.delete(id)
          reject(error)
        }
      })
    },
    stop,
  }
}
