export interface Cycle { id: number }
export interface Signal { cycle_id: number; sensor: string; unit: string; times: number[]; values: number[]; source: string }
export interface GhostSignature { cycle_id: number; sensor: string; unit: string; reference_cycle_id: number; reference_definition: string; selection_method: string; distance: number; times: number[]; target_values: number[]; reference_values: number[]; mean_difference: number; interpretation: string }
export interface Pred { model: string; condition: number; label: string; confidence: number; probabilities: Record<string, number> }
export interface Diagnosis { cycle_id: number; predictions: Pred[] }
export interface Report { source: string; narrative: string; structured_evidence: string[]; warning: string }
export interface Metric { model: string; accuracy: number; macro_f1: number; train_count: number; test_count: number; classes: number[]; confusion_matrix: number[][] }
async function req<T>(path: string, method = 'GET'): Promise<T> {
  const res = await fetch(`/api${path}`, { method })
  if (!res.ok) {
    let err = `Request failed (${res.status})`
    try { const body = await res.json(); err = body.detail || err } catch { /* server error */ }
    throw new Error(err)
  }
  return res.json()
}
export const api = {
  health: () => req<{ok:boolean, data_ready:boolean}>('/health'),
  cycles: () => req<{total:number,cycles:Cycle[]}>('/cycles?limit=100'),
  signal: (id:number,sensor:string) => req<Signal>(`/cycles/${id}/signals?sensor=${sensor}`),
  ghost: (id:number,sensor:string) => req<GhostSignature>(`/ghost/${id}?sensor=${sensor}`),
  diagnose: (id:number) => req<Diagnosis>(`/diagnose/${id}`, 'POST'),
  reveal: (id:number) => req<{actual:number,label:string}>(`/reveal/${id}`, 'POST'),
  investigate: (id:number) => req<Report>(`/investigate/${id}`, 'POST'),
  evaluation: () => req<{results:Metric[]}>('/evaluation'),
}
