import { lazy, Suspense, useEffect, useRef, useState } from 'react'
import { ArrowLeft, ArrowUpRight, BrainCircuit, Check, Eye, FileText, LockKeyhole, ShieldAlert } from 'lucide-react'
import { api, type Cycle, type Diagnosis, type Metadata, type Report, type Reveal } from '../api'
import { cycleName, sensorNames } from '../domain'
import { ErrorNotice, Loading } from '../App'
const Replay = lazy(() => import('./Replay'))

export function Investigation({ id, cycles, meta }: { id: number; cycles: Cycle[]; meta: Metadata }) {
  const [sensorName, setSensorName] = useState(meta.sensors[0].name)
  const [diag, setDiag] = useState<Diagnosis | null>(null)
  const [truth, setTruth] = useState<Reveal | null>(null)
  const [report, setReport] = useState<Report | null>(null)
  const [busy, setBusy] = useState('')
  const [error, setError] = useState('')
  const pending = useRef<AbortController | null>(null)
  useEffect(() => () => pending.current?.abort(), [])
  async function act(name: string) {
    pending.current?.abort()
    const request = new AbortController(); pending.current = request
    setBusy(name); setError('')
    try {
      if (name === 'diagnose') {
        const data = await api.diagnose(id, request.signal)
        if (!request.signal.aborted && data.cycle_id === id) { setDiag(data); setTruth(null); setReport(null) }
      } else if (name === 'reveal') {
        const data = await api.reveal(id, request.signal)
        if (!request.signal.aborted && data.cycle_id === id) setTruth(data)
      } else {
        const data = await api.investigate(id, request.signal)
        if (!request.signal.aborted && data.cycle_id === id) setReport(data)
      }
    } catch (e) { if (!request.signal.aborted) setError(e instanceof Error ? e.message : String(e)) }
    finally { if (!request.signal.aborted) setBusy('') }
  }
  const sensor = meta.sensors.find(s => s.name === sensorName)!
  return <>
    <div className="breadcrumb"><a href="#/archive"><ArrowLeft size={14} />Machine archive</a><span>/</span><span>{cycleName(id)}</span></div>
    <section className="heading investigation-heading"><div><div className="eyebrow amber">CASE FILE / UCI—{String(id).padStart(4, '0')}</div><h1>The last <em>sixty seconds.</em></h1><p>A real recording. A model's interpretation. An answer you can verify.</p></div><label className="cycle-select">CURRENT RECORDING<select aria-label="Selected cycle" value={id} onChange={e => { location.hash = `/investigation/${e.target.value}` }}>{cycles.map(c => <option key={c.id} value={c.id}>{cycleName(c.id)}</option>)}</select></label></section>
    <div className="investigation-layout"><div className="lab-main"><div className="sensor-tabs" role="group" aria-label="Sensor channels">{meta.sensors.map(s => <button key={s.name} aria-pressed={sensorName === s.name} className={sensorName === s.name ? 'active' : ''} onClick={() => setSensorName(s.name)}><span>{s.name}</span><small>{sensorNames[s.name] ?? s.name}</small></button>)}</div><Suspense fallback={<Loading />}><Replay key={`${id}:${sensorName}`} id={id} sensor={sensor} /></Suspense></div>
      <aside className="panel case-file"><div className="panel-label">01 / RECORDING DOSSIER</div><div className="dossier-id">{String(id).padStart(4, '0')}<span>HELD-OUT EXPERIMENT</span></div><dl><div><dt>Source</dt><dd>{meta.dataset}</dd></div><div><dt>Recording window</dt><dd>60 seconds</dd></div><div><dt>Available channels</dt><dd>{meta.sensors.length} sensors</dd></div><div><dt>Task</dt><dd>Cooler condition</dd></div><div><dt>Recorded truth</dt><dd className={truth ? 'sea' : ''}>{truth ? `${truth.label} (${truth.actual}%)` : <><LockKeyhole size={12} /> Concealed</>}</dd></div></dl><div className="dossier-note"><Eye size={17} /><p>Make your observation before uncovering the recorded answer.</p></div><ol className="workflow"><li className="done">Inspect the measured signal</li><li className={diag ? 'done' : ''}>Run model diagnosis</li><li className={truth ? 'done' : ''}>Reveal &amp; verify</li></ol></aside>
    </div>
    {error && <ErrorNotice message={error} />}
    <section className="cards">
      <div className="panel diagnosis"><div className="panel-label">03 / MODEL INTERPRETATION</div><h2><BrainCircuit size={21} className="amber" />Diagnostic engine</h2><p>Cooler-condition classification from recorded sensor statistics.</p><span className="inference-label">Precomputed from model inference</span><button className="primary" disabled={!!busy} onClick={() => act('diagnose')}><BrainCircuit size={16} />{busy === 'diagnose' ? 'Retrieving prediction…' : diag ? 'Run diagnosis again' : 'Run AI diagnosis'}<ArrowUpRight size={15} /></button>
        {diag && <div className="diagnosis-results" aria-live="polite">{diag.predictions.map(prediction => <div className="model-result" key={prediction.model}><div className="model-name"><span>{prediction.model}</span><span className="tag">SAVED INFERENCE</span></div><h3>{prediction.label}</h3><div className="prediction-value"><b>{prediction.condition}%</b><span>predicted cooler condition</span></div><div className="probabilities">{Object.entries(prediction.probabilities).map(([label, probability]) => <div key={label}><div><span>{meta.condition_labels[label] ?? label} ({label}%)</span><b>{(probability * 100).toFixed(1)}%</b></div><progress aria-label={`${prediction.model} probability for cooler class ${label}`} max={1} value={probability} /></div>)}</div></div>)}<p className="footnote">Model probabilities are uncalibrated. They are not probabilities of imminent failure.</p></div>}
        {!diag && <div className="dashed-placeholder"><BrainCircuit size={26} /><span>No prediction retrieved yet.</span></div>}
      </div>
      <div className="panel reality"><div className="panel-label">04 / RECORDED EVIDENCE</div><h2><Eye size={21} className="sea" />The reality check</h2><p>Reveal the original experimental label after diagnosis, then compare each model with the recording.</p><button className="secondary" disabled={!diag || !!busy || !!truth} onClick={() => act('reveal')}><Eye size={16} />{busy === 'reveal' ? 'Opening recorded label…' : truth ? 'Actual condition revealed' : 'Reveal Actual Condition'}</button>
        {truth && diag ? <div className="truth" aria-live="polite"><small>RECORDED COOLER CONDITION</small><strong>{truth.actual}%</strong><h3>{truth.label}</h3>{diag.predictions.map(prediction => <div className={'verdict ' + (prediction.condition === truth.actual ? 'correct' : 'incorrect')} key={prediction.model}>{prediction.condition === truth.actual ? <Check size={19} /> : <ShieldAlert size={19} />}<div><b>{prediction.condition === truth.actual ? 'Prediction matches' : 'Prediction differs'}</b><span>{prediction.model}: {prediction.label} ({prediction.condition}%) predicted / {truth.label} ({truth.actual}%) recorded</span></div></div>)}<p className="footnote">Recorded condition from UCI profile.txt, aligned by cycle row.</p></div> : <div className="concealed"><LockKeyhole size={30} /><strong>The answer stays in the archive.</strong><p>{diag ? 'Your prediction is ready. Reveal the recorded condition when you are ready to compare.' : 'Run the diagnosis first to compare prediction with evidence.'}</p></div>}
      </div>
    </section>
    {diag && diag.feature_evidence?.length > 0 && <section className="panel evidence-panel"><div className="panel-label">MEASURED FEATURE EVIDENCE</div><h2>What the model was given.</h2><p>Full-recording sensor summaries, before any label is revealed. Measurements describe the cycle; they do not establish a cause.</p><div className="table-scroll"><table><caption className="sr-only">Recorded sensor summary features for cycle {id}</caption><thead><tr><th>Sensor / unit</th><th>Mean</th><th>Std. dev.</th><th>Minimum</th><th>Maximum</th><th>5th pct.</th><th>95th pct.</th></tr></thead><tbody>{diag.feature_evidence.map(e => <tr key={e.sensor}><th>{e.sensor} <span className="muted">/ {e.unit}</span></th>{(['mean', 'std', 'min', 'max', 'p05', 'p95'] as const).map(stat => <td key={stat}>{e[stat].toFixed(3)}</td>)}</tr>)}</tbody></table></div></section>}
    <section className="panel investigator"><div className="section-heading"><div><div className="panel-label">05 / FORENSIC NARRATIVE</div><h2><FileText size={20} className="amber" />The investigator's report</h2><p>Structured evidence, model interpretation and explicit source attribution.</p></div><button className="secondary" disabled={!diag || !!busy} onClick={() => act('investigate')}><FileText size={16} />{busy === 'investigate' ? 'Preparing report…' : 'Generate investigation'}</button></div>{busy === 'investigate' && <Loading text="Requesting the investigator. A local model can take up to 45 seconds…" />}{report && <div className="report"><div className="report-source"><span className="statusdot" /><strong>{report.source.startsWith('ollama:') ? 'LLM-generated interpretation' : 'Rule-based / non-LLM fallback'}</strong><small>{report.source}</small></div><p className="narrative">{report.narrative}</p><h3>Measured evidence</h3><ul className="fact-grid">{report.structured_evidence.map(fact => <li key={fact}>{fact}</li>)}</ul><p className="footnote">{report.warning}</p></div>}{!report && !busy && <p className="footnote">When Gemma is unavailable, the report uses a clearly labeled deterministic summary. This does not count as Gemma integration.</p>}</section>
  </>
}
