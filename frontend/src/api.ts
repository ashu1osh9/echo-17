export interface Cycle { id: number }
export interface Sensor { name: string; unit: string; rate_hz: number }
export interface Metadata { sensors: Sensor[]; condition_labels: Record<string, string>; task: string; dataset: string }
export interface Signal { cycle_id: number; sensor: string; unit: string; times: number[]; values: number[]; source: string; rate_hz_original: number }
export interface GhostSignature { cycle_id: number; sensor: string; unit: string; reference_cycle_id: number; reference_definition: string; selection_method: string; distance: number; times: number[]; target_values: number[]; reference_values: number[]; mean_difference: number; interpretation: string }
export interface Pred { model: string; condition: number; label: string; confidence: number; probabilities: Record<string, number> }
export interface Evidence { sensor: string; unit: string; mean: number; std: number; min: number; max: number; p05: number; p95: number }
export interface Diagnosis { cycle_id: number; predictions: Pred[]; inference_mode: string; feature_evidence: Evidence[] }
export interface Reveal { cycle_id: number; actual: number; label: string }
export interface Report { cycle_id: number; source: string; narrative: string; structured_evidence: string[]; warning: string }
export interface Metric { model: string; accuracy: number; macro_f1: number; train_count: number; test_count: number; classes: number[]; confusion_matrix: number[][]; split: string; wrong_cycle_ids?: number[]; uncertainty_note?: string; timestamp_utc?: string }
async function req<T>(path: string, method = 'GET', signal?: AbortSignal): Promise<T> {
  const res = await fetch(`/api${path}`, { method, signal })
  if (!res.ok) {
    let message = `Request failed (${res.status}). Please try again.`
    try { const body = await res.json(); if (typeof body.detail === 'string') message = body.detail } catch { /* preserve HTTP error */ }
    throw new Error(message)
  }
  return res.json()
}
export const api = {
  health: (s?: AbortSignal) => req<{ ok: boolean; data_ready: boolean }>('/health', 'GET', s),
  meta: (s?: AbortSignal) => req<Metadata>('/meta', 'GET', s),
  cycles: (s?: AbortSignal) => req<{ total: number; cycles: Cycle[] }>('/cycles?limit=441', 'GET', s),
  signal: (id: number, sensor: string, s?: AbortSignal) => req<Signal>(`/cycles/${id}/signals?sensor=${encodeURIComponent(sensor)}`, 'GET', s),
  ghost: (id: number, sensor: string, s?: AbortSignal) => req<GhostSignature>(`/ghost/${id}?sensor=${encodeURIComponent(sensor)}`, 'GET', s),
  diagnose: (id: number, s?: AbortSignal) => req<Diagnosis>(`/diagnose/${id}`, 'POST', s),
  reveal: (id: number, s?: AbortSignal) => req<Reveal>(`/reveal/${id}`, 'POST', s),
  investigate: (id: number, s?: AbortSignal) => req<Report>(`/investigate/${id}`, 'POST', s),
  evaluation: (s?: AbortSignal) => req<{ results: Metric[] }>('/evaluation', 'GET', s),
}
