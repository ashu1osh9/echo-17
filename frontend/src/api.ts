export interface Cycle { id: number }
export interface Sensor { name: string; unit: string; rate_hz: number }
export interface Metadata { sensors: Sensor[]; condition_labels: Record<string, string>; task: string; dataset: string }
export interface Signal { cycle_id: number; sensor: string; unit: string; times: number[]; values: number[]; source: string; rate_hz_original: number }
export interface GhostSignature { cycle_id: number; sensor: string; unit: string; reference_cycle_id: number; reference_definition: string; selection_method: string; distance: number; times: number[]; target_values: number[]; reference_values: number[]; mean_difference: number; interpretation: string }
export interface Pred { model: string; condition: number; label: string; confidence: number; probabilities: Record<string, number> }
export interface Evidence { sensor: string; unit: string; mean: number; std: number; min: number; max: number; p05: number; p95: number }
export interface ModelStatus { available: boolean; status: string; detail?: string; model?: string; model_version?: string }
export interface Diagnosis { cycle_id: number; predictions: Pred[]; inference_mode: string; feature_evidence: Evidence[]; tabpfn_status?: ModelStatus }
export interface Reveal { cycle_id: number; actual: number; label: string }
export interface InvestigatorStatus { available: boolean; status: string; detail: string; model?: string; timeout_seconds?: number; inference_mode?: string }
export interface Report { cycle_id: number; source: string; mode: 'gemma' | 'fallback'; inference_mode: 'live_local' | 'precomputed' | 'non_llm'; narrative: string; structured_evidence: string[]; warning: string; selected_model: string; fallback_reason: string | null; evidence_sha256: string; generation: { model?: string; model_digest?: string; response_seconds?: number; grounding: string }; sections: { title: string; kind: string; statements: string[]; evidence_ids: string[] }[] }
export interface Metric { model: string; accuracy: number; macro_f1: number; train_count: number; test_count: number; classes: number[]; confusion_matrix: number[][]; split: string; wrong_cycle_ids?: number[]; uncertainty_note?: string; timestamp_utc?: string; classification_report?: Record<string, { 'f1-score': number }>; model_version?: string; fit_seconds?: number; predict_seconds?: number; predict_proba_seconds?: number; fallback_reason?: string | null }
export interface ComparisonCase { cycle_id: number; random_forest_condition: number; tabpfn_condition: number }
export interface Comparison { available: boolean; tabpfn_status: ModelStatus; comparison: null | { test_count: number; accuracy_delta: number; macro_f1_delta: number; counts: Record<string, number>; cases: Record<string, ComparisonCase[]>; note: string } }
const apiBase = (import.meta.env?.VITE_API_BASE_URL ?? '').replace(/\/$/, '')
function endpoint(path: string) {
  if (apiBase) {
    try {
      const url = new URL(apiBase)
      if ((url.protocol !== 'https:' && !(url.protocol === 'http:' && ['localhost', '127.0.0.1', '[::1]'].includes(url.hostname))) || url.username || url.password || url.search || url.hash || url.pathname !== '/') throw new Error('Invalid origin')
    } catch { throw new Error('Configure a public HTTPS API origin or local HTTP origin.') }
  }
  return `${apiBase}/api${path}`
}
async function req<T>(path: string, method = 'GET', signal?: AbortSignal): Promise<T> {
  const res = await fetch(endpoint(path), { method, signal })
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
  investigate: (id: number, s?: AbortSignal, model?: string) => req<Report>(`/investigate/${id}${model ? `?model=${encodeURIComponent(model)}` : ''}`, 'POST', s),
  evaluation: (s?: AbortSignal) => req<{ results: Metric[] }>('/evaluation', 'GET', s),
  comparison: (s?: AbortSignal) => req<Comparison>('/comparison', 'GET', s),
  investigatorStatus: (s?: AbortSignal) => req<InvestigatorStatus>('/investigator/status', 'GET', s),
}
