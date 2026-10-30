import { useEffect, useState } from 'react'
import { api, type Comparison as ComparisonData } from '../api'
import { cycleName } from '../domain'
import { ErrorNotice, Loading } from '../App'

const groupNames: Record<string, string> = { disagreements: 'Different predictions', tabpfn_improved: 'TabPFN correct / RF incorrect', tabpfn_worse: 'RF correct / TabPFN incorrect', both_wrong: 'Both incorrect', both_correct: 'Both correct' }
export default function Comparison({ labels }: { labels: Record<string, string> }) {
  const [data, setData] = useState<ComparisonData | null>(null)
  const [error, setError] = useState('')
  const [attempt, setAttempt] = useState(0)
  const [group, setGroup] = useState('disagreements')
  const [page, setPage] = useState(1)
  useEffect(() => {
    const controller = new AbortController(); setError(''); setData(null)
    api.comparison(controller.signal).then(value => { if (!controller.signal.aborted) setData(value) })
      .catch(e => { if (!controller.signal.aborted) setError(e.message) })
    return () => controller.abort()
  }, [attempt])
  if (error) return <ErrorNotice message={error} retry={() => setAttempt(v => v + 1)} />
  if (!data) return <Loading text="Checking validated model comparison…" />
  if (!data.available || !data.comparison) return <section className="panel methodology"><div><div className="panel-label">MODEL COMPARISON / {data.tabpfn_status.status === 'restricted' ? 'OFFLINE RESEARCH' : 'AWAITING REAL OUTPUTS'}</div><h3>{data.tabpfn_status.status === 'restricted' ? 'TabPFN stays in the research archive' : 'TabPFN evaluation unavailable'}</h3><p>{data.tabpfn_status.detail ?? 'No validated GPU outputs have been imported.'} Random Forest results remain available above.</p><p>{data.tabpfn_status.status === 'restricted' ? 'This public experience includes genuine Random Forest results and RF-grounded Gemma reports. Restricted model outputs are not served.' : 'Complete the Colab run and validated import before comparing models. No foundation-model score is implied here.'}</p></div></section>
  const result = data.comparison, rows = result.cases[group] ?? []
  const visible = rows.slice((page - 1) * 20, page * 20)
  return <section className="panel evidence-panel"><div className="panel-label">SAME HELD-OUT CYCLES / PRECOMPUTED FROM MODEL INFERENCE</div><h2>Random Forest vs {data.tabpfn_status.model}</h2><p>{result.test_count} identical held-out cycles. Accuracy delta: {result.accuracy_delta.toFixed(8)}; macro-F1 delta: {result.macro_f1_delta.toFixed(8)} (TabPFN minus RF).</p><div className="condition-legend">{Object.entries(groupNames).map(([key, title]) => <span key={key}>{title}: <b>{result.counts[key]}</b></span>)}</div>
    <label className="filter-label">Audit cases<select aria-label="Model comparison cases" value={group} onChange={e => { setGroup(e.target.value); setPage(1) }}>{Object.entries(groupNames).map(([key, title]) => <option key={key} value={key}>{title}</option>)}</select></label>
    <div className="table-scroll"><table><caption className="sr-only">All model comparison cases, paginated without selecting only successes</caption><thead><tr><th>Recording</th><th>Random Forest prediction</th><th>{data.tabpfn_status.model} prediction</th></tr></thead><tbody>{visible.map(row => <tr key={row.cycle_id}><th><a href={`#/investigation/${row.cycle_id}`}>{cycleName(row.cycle_id)} ↗</a></th><td>{labels[String(row.random_forest_condition)]} ({row.random_forest_condition}%)</td><td>{labels[String(row.tabpfn_condition)]} ({row.tabpfn_condition}%)</td></tr>)}</tbody></table></div>
    {!rows.length && <p>No cases in this group for the actual saved run.</p>}<div className="pagination"><span>{rows.length} cases · page {page} / {Math.max(1, Math.ceil(rows.length / 20))}</span><div><button className="secondary" disabled={page === 1} onClick={() => setPage(page - 1)}>Previous</button><button className="secondary" disabled={page * 20 >= rows.length} onClick={() => setPage(page + 1)}>Next</button></div></div><p className="footnote">{result.note} Open an investigation and click Reveal to inspect the recorded label. Both improvements and regressions are retained.</p>
  </section>
}
