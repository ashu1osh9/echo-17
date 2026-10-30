import type { Cycle, GhostSignature, Signal } from './api'
export const cycleName = (id: number) => `Cycle ${String(id).padStart(4, '0')}`
export const sensorNames: Record<string, string> = { PS1: 'Pressure', FS1: 'Volume flow', TS1: 'Temperature · inlet', TS2: 'Temperature · outlet', VS1: 'Vibration', EPS1: 'Motor power' }
export function parseRoute(hash: string): { page: 'archive' | 'investigation' | 'evaluation' | 'missing'; id?: number } {
  if (hash === '#/evaluation') return { page: 'evaluation' }
  if (!hash || hash === '#/' || hash === '#/archive') return { page: 'archive' }
  const match = /^#\/investigation\/(\d+)$/.exec(hash)
  return match ? { page: 'investigation', id: Number(match[1]) } : { page: 'missing' }
}
export function filterCycles(cycles: Cycle[], query: string, filter: string, opened: number[]) {
  const term = query.trim().replace(/^(cycle\s*#?\s*|#)/i, '').replace(/^0+(?=\d)/, '')
  return cycles.filter(c => (!term || String(c.id).includes(term)) && (filter === 'all' || (filter === 'opened' ? opened.includes(c.id) : !opened.includes(c.id))))
}
export function advanceTime(current: number, deltaMs: number, speed: number, duration = 60) {
  return Math.min(duration, Math.max(0, current + Math.max(0, deltaMs) / 1000 * speed))
}
export function alignedGraph(signal: Signal, ghost: GhostSignature | null, cursor: number) {
  const matches = ghost?.cycle_id === signal.cycle_id && ghost.sensor === signal.sensor && ghost.times.length === signal.times.length && ghost.times.every((t, i) => t === signal.times[i])
  return signal.times.flatMap((t, i) => t <= cursor ? [{ t, value: signal.values[i], reference: matches ? ghost!.reference_values[i] : undefined }] : [])
}
export function previewDifferences(ghost: GhostSignature) {
  const count = ghost.target_values.length
  if (!count || count !== ghost.reference_values.length || count !== ghost.times.length) return null
  const differences = ghost.target_values.map((v, i) => v - ghost.reference_values[i])
  return { mean: differences.reduce((a, b) => a + b, 0) / count, rmse: Math.sqrt(differences.reduce((a, b) => a + b * b, 0) / count) }
}
