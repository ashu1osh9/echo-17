import { useEffect, useState } from 'react'
import { ArrowUpRight, FlaskConical, Info } from 'lucide-react'
import { api, type Metric } from '../api'
import { cycleName } from '../domain'
import { ErrorNotice, Loading } from '../App'
export default function Evaluation({ conditionLabels }: { conditionLabels: Record<string, string> }) {
  const [metrics, setMetrics] = useState<Metric[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [attempt, setAttempt] = useState(0)
  useEffect(() => {
    const request = new AbortController(); setLoading(true); setError('')
    api.evaluation(request.signal).then(data => { if (!request.signal.aborted) setMetrics(data.results) })
      .catch(e => { if (!request.signal.aborted) setError(e.message) })
      .finally(() => { if (!request.signal.aborted) setLoading(false) })
    return () => request.abort()
  }, [attempt])
  return <>
    <section className="heading"><div><div className="eyebrow amber">EVALUATION / OPEN TO SCRUTINY</div><h1>Evidence over <em>assumptions.</em></h1><p>Observed model performance on held-out experimental recordings.<br />Every score comes from saved model results.</p></div><span className="evaluation-symbol"><FlaskConical size={42} /></span></section>
    {loading ? <Loading text="Loading saved evaluation…" /> : error ? <ErrorNotice message={error} retry={() => setAttempt(a => a + 1)} /> : !metrics.length ? <div className="empty panel">No model evaluation artifacts are available.</div> : metrics.map(metric => <section className="evaluation-block" key={metric.model}>
      <div className="section-heading"><h2>{metric.model}</h2><span className="tag">HELD-OUT EVALUATION</span></div>
      <div className="evaluation-stats"><div className="panel"><small>ACCURACY</small><strong>{(metric.accuracy * 100).toFixed(2)}<span>%</span></strong><p>Correct held-out classifications</p></div><div className="panel"><small>MACRO-F1</small><strong>{metric.macro_f1.toFixed(4)}</strong><p>Equal weight for each cooler class</p></div><div className="panel"><small>EVALUATION CYCLES</small><strong>{metric.test_count}</strong><p>{metric.train_count.toLocaleString()} separate training cycles</p></div></div>
      <div className="evaluation-grid"><div className="panel"><div className="panel-label">WHERE THE MODEL WAS RIGHT. AND WRONG.</div><h2>Confusion matrix</h2><p>Rows: recorded condition · Columns: model prediction</p><div className="table-scroll"><table className="confusion"><caption className="sr-only">Confusion matrix for {metric.model}</caption><thead><tr><th scope="col">Actual ↓ / predicted →</th>{metric.classes.map(c => <th scope="col" key={c}>{c}%</th>)}</tr></thead><tbody>{metric.confusion_matrix.map((row, i) => <tr key={i}><th scope="row">{metric.classes[i]}%</th>{row.map((value, j) => <td className={i === j ? 'diagonal' : value ? 'matrix-error' : ''} key={j}>{value}</td>)}</tr>)}</tbody></table></div></div>
        <div className="panel"><div className="panel-label">AUDIT THE EXCEPTIONS</div><h2>Every missed signal.</h2>{metric.wrong_cycle_ids ? <><p>{metric.wrong_cycle_ids.length} incorrect predictions in the saved evaluation. Open a case, diagnose, then reveal its recorded condition.</p><div className="failure-cases">{[...metric.wrong_cycle_ids].sort((a, b) => a - b).map(id => <a key={id} href={`#/investigation/${id}`}><span>{cycleName(id)}<small>MISCLASSIFIED IN SAVED EVALUATION</small></span><ArrowUpRight size={18} /></a>)}</div>{!metric.wrong_cycle_ids.length && <p>No errors occurred on this split.</p>}</> : <p>Per-cycle error IDs were not exported for this model.</p>}</div></div>
      <div className="panel methodology"><Info size={21} className="amber" /><div><h3>What these results can—and cannot—say.</h3><p>Split: {metric.split}. Training and test cycles remain separate. The baseline uses six sensor channels and 36 sensor-summary predictors; cycle IDs, component labels and stability are excluded.</p><p>{metric.uncertainty_note ?? 'A random cycle split on one test rig does not establish unseen-machine generalization. Model probabilities are uncalibrated.'} No remaining-useful-life or imminent-failure claim is supported.</p>{metric.timestamp_utc && <small>Saved run: <time dateTime={metric.timestamp_utc}>{new Date(metric.timestamp_utc).toLocaleString()}</time></small>}</div></div>
    </section>)}
    <div className="condition-legend" aria-label="Cooler-condition class labels">{Object.entries(conditionLabels).map(([code, label]) => <span key={code}><b>{code}%</b> — {label}</span>)}</div>
    <div className="evaluation-note"><span className="statusdot" />Only models with actual saved evaluation results appear here. No TabPFN result is implied by its presence in the source code.</div>
  </>
}
