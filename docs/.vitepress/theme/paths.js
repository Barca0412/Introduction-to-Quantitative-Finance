// '/wiki/factors/index.html', '/wiki/factors/' and '/wiki/factors' all -> '/wiki/factors'.
// Kept outside tutorials.data.js: a data loader only exposes `data` to the client.
export function normalizePath(path) {
  return String(path || '')
    .replace(/[?#].*$/, '')
    .replace(/(index)?\.(html|md)$/, '')
    .replace(/\/+$/, '') || '/'
}
