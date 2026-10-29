import { useEffect, useState } from 'react'
import { Activity, Archive, GitCompareArrows, BrainCircuit, CircleCheck, Eye, FileText, FlaskConical, Play, Radio, RefreshCw, ShieldAlert, Waves } from 'lucide-react'
import { ResponsiveContainer, AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip } from 'recharts'
import { api, Cycle, Signal, GhostSignature, Diagnosis, Report, Metric } from './api'

const sensors = ['PS1','FS1','TS1','TS2','VS1','EPS1']
export default function App() {
  const [cycles,setCycles] = useState<Cycle[]>([])
  const [total,setTotal] = useState(0)
  const [id,setId] = useState<number | null>(null)
  const [sensor,setSensor] = useState('PS1')
  const [signal,setSignal] = useState<Signal | null>(null)
  const [ghost,setGhost] = useState<GhostSignature | null>(null)
  const [diag,setDiag] = useState<Diagnosis | null>(null)
  const [reveal,setReveal] = useState<{actual:number,label:string} | null>(null)
  const [report,setReport] = useState<Report | null>(null)
  const [metrics,setMetrics] = useState<Metric[]>([])
  const [error,setError] = useState('')
  const [busy,setBusy] = useState('')
  const [tab,setTab] = useState<'investigation'|'evaluation'>('investigation')

  useEffect(() => {
    api.cycles().then(a => { setCycles(a.cycles);setTotal(a.total);setId(a.cycles[0]?.id ?? null) }).catch(e => setError(String(e.message)))
    api.evaluation().then(a=>setMetrics(a.results)).catch(()=>{})
  },[])
  useEffect(()=>{
    setDiag(null);setReveal(null);setReport(null)
  },[id])
  useEffect(()=>{
    setSignal(null);setGhost(null)
    if (id === null) return
    let active=true
    api.signal(id,sensor).then(a=>{if(active)setSignal(a)}).catch(e=>{if(active)setError(String(e.message))})
    return ()=>{active=false}
  },[id,sensor])
  async function act(name: string, fn: ()=>Promise<void>) { setError('');setBusy(name);try{await fn()}catch(e){setError(e instanceof Error?e.message:String(e))}finally{setBusy('')} }
  const graph = (signal?.values ?? []).map((value,i)=>({ t: signal?.times[i], value, reference: ghost?.reference_values[i] }))
  const best = diag?.predictions[diag.predictions.length-1]
  return <div className="app">
    <aside className="sidebar">
      <div className="brand"><div className="logo"><Radio size={24}/></div><div><strong>ECHO<span>—17</span></strong><small>FORENSIC INTELLIGENCE</small></div></div>
      <div className="navtitle">WORKSPACE</div>
      <button className={'nav '+(tab==='investigation'?'selected':'')} onClick={()=>setTab('investigation')}><Waves size={17}/> Signal laboratory</button>
      <button className={'nav '+(tab==='evaluation'?'selected':'')} onClick={()=>setTab('evaluation')}><FlaskConical size={17}/> Model evaluation</button>
      <div className="sidefoot"><div className="statusdot"/> UCI DATA · REAL RECORDINGS <p>Evidence-first AI<br/>Experimental fault classification</p></div>
    </aside>
    <main className="main">
      <header className="top"><div className="eyebrow"><span className="bright">●</span> ACTIVE FORENSIC SESSION <span className="slash">/</span> UCI HYDRAULIC ARCHIVE</div><div className="topbadge">RESEARCH BUILD • v0.1</div></header>
      {tab==='investigation'?<>
        <section className="heading"><div><div className="eyebrow amber">ARCHIVE / INVESTIGATION</div><h1>The Machine That <em>Remembers.</em></h1><p>Listen to recorded sensor evidence. Let the models speak. Then reveal the truth.</p></div><div className="count"><Archive size={20}/><div><b>{total || '—'}</b><small>HELD-OUT CYCLES</small></div></div></section>
        {error&&<div className="error"><ShieldAlert size={19}/><div><strong>Action required</strong><p>{error}</p><small>See README.md to download the UCI dataset and train the CPU baseline.</small></div></div>}
        <section className="panel selection"><div><div className="panel-label">01 / SELECT ARCHIVED MACHINE RECORDING</div><h2>Cycle selection</h2></div><div className="control"><label htmlFor="cycle">RECORDED CYCLE</label><select id="cycle" value={id ?? ''} disabled={!cycles.length} onChange={e=>setId(Number(e.target.value))}>{cycles.length? cycles.map(c=><option value={c.id} key={c.id}>Cycle #{String(c.id).padStart(4,'0')}</option>):<option value="">No data prepared</option>}</select></div></section>
        <section className="chartpanel"><div className="charthead"><div><div className="panel-label">02 / ORIGINAL MEASURED SIGNALS</div><h2><Activity size={22} className="sea"/> Sensor waveform</h2><p>60-second experimental recording · downsampled actual measurements</p></div><div className="sensor-tabs">{sensors.map(s=><button key={s} className={s===sensor?'active':''} onClick={()=>setSensor(s)}>{s}</button>)}</div></div>
          <div className="chartarea">{graph.length?<ResponsiveContainer width="100%" height="100%"><AreaChart data={graph}><defs><linearGradient id="fill" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stopColor="#45e0cc" stopOpacity={.24}/><stop offset="100%" stopColor="#45e0cc" stopOpacity={0}/></linearGradient></defs><CartesianGrid stroke="#24333b" vertical={false} strokeDasharray="3 5"/><XAxis dataKey="t" stroke="#69838c" tick={{fontSize:11}} minTickGap={35} unit="s"/><YAxis stroke="#69838c" tick={{fontSize:11}} domain={['auto','auto']} width={55}/><Tooltip contentStyle={{background:'#10222a',border:'1px solid #34505a',color:'#fff'}} formatter={(v,name)=>[`${Number(v).toFixed(3)} ${signal?.unit}`,name==='reference'?'Full-cooler reference':'Measured target']}/><Area type="monotone" dataKey="value" stroke="#45e0cc" fill="url(#fill)" strokeWidth={2} dot={false} isAnimationActive={false}/>{ghost&&<Area type="monotone" dataKey="reference" stroke="#f6b667" fill="none" strokeWidth={2} strokeDasharray="5 3" dot={false} isAnimationActive={false}/>}</AreaChart></ResponsiveContainer>:<div className="no-data"><Waves size={38}/><p>Run dataset preparation to display original recorded waveforms.</p></div>}</div><div className="ghostcontrols"><button className="secondary" disabled={id===null||!signal||!!busy} onClick={()=>act('ghost',async()=>setGhost(await api.ghost(id!,sensor)))}><GitCompareArrows size={17}/>{busy==='ghost'?'Searching archive...':'Reveal Ghost Signature'}</button>{ghost&&<div className="ghostmeta"><strong>Measured comparison: Cycle #{ghost.reference_cycle_id}</strong><span>{ghost.reference_definition}</span><span>Sensor mean difference: {ghost.mean_difference.toFixed(3)} {ghost.unit} · {ghost.interpretation}</span></div>}</div><div className="chartfoot"><div className="chip"><span className="statusdot"/> {signal? `${signal.sensor} · ${signal.unit}`:'Awaiting real signals'}</div><span>{signal?`${signal.values.length} measured points · original sensor ${signal.source}`:'No simulated data'}</span></div>
        </section>
        <section className="cards"><div className="panel"><div className="panel-label">03 / AI FAULT CLASSIFICATION</div><h2><BrainCircuit size={21} className="ambericon"/> Diagnostic engine</h2><p>Models predict cooler condition from recorded sensor statistics.</p><button className="primary" disabled={id===null||!!busy} onClick={()=>act('diagnose',async()=>{setDiag(await api.diagnose(id!));setReveal(null);setReport(null)})}><Play size={17}/>{busy==='diagnose'?'Analyzing...':'Run AI diagnosis'}</button>{diag&&<div className="result"><small>MODEL PREDICTIONS</small>{diag.predictions.map(p=><div key={p.model} className="predict"><div><b>{p.model}</b><span>{p.label} · {p.condition}% cooler condition</span></div><strong>{(p.confidence*100).toFixed(1)}%</strong></div>)}<div className="footnote">Model confidence is not a calibrated failure probability.</div></div>}</div>
        <div className="panel"><div className="panel-label">04 / GROUND-TRUTH VERIFICATION</div><h2><Eye size={21} className="sea"/> Reality check</h2><p>Unlock the actual experiment label only after the model has predicted.</p><button className="secondary" disabled={!diag||!!busy} onClick={()=>act('reveal',async()=>setReveal(await api.reveal(id!)))}><Eye size={17}/> Reveal recorded truth</button>{reveal&&<div className="truth"><CircleCheck size={22}/><div><small>RECORDED CONDITION</small><strong>{reveal.label} · {reveal.actual}%</strong><span>{best?.condition === reveal.actual?'Model prediction matches the experimental label.':'Prediction differs from the experimental label.'}</span></div></div>}</div></section>
        <section className="panel investigator"><div><div className="panel-label">05 / EXPLANATION ENGINE</div><h2><FileText size={21} className="ambericon"/> Ghost investigator</h2><p>Evidence-restricted interpretation from Gemma (or an explicitly labeled deterministic fallback).</p></div><button className="secondary" disabled={!diag||!!busy} onClick={()=>act('investigate',async()=>setReport(await api.investigate(id!)))}><RefreshCw size={16}/>{busy==='investigate'?'Investigating...':'Generate investigation'}</button>{report&&<div className="report"><small>REPORT SOURCE: {report.source}</small><p>{report.narrative}</p><details><summary>See measured evidence</summary>{report.structured_evidence.map(s=><div key={s} className="fact">{s}</div>)}</details><div className="footnote">{report.warning}</div></div>}</section>
      </>:<><section className="heading"><div><div className="eyebrow amber">VALIDATION / TRANSPARENCY</div><h1>Performance, <em>not promises.</em></h1><p>All scores below come from held-out predictions, not handcrafted values.</p></div></section>{!metrics.length?<div className="panel"><p>No model evaluation artifacts. Run the CPU baseline first.</p></div>:<div className="metricgrid">{metrics.map(m=><div className="panel" key={m.model}><div className="panel-label">MODEL EVALUATION</div><h2>{m.model}</h2><div className="numbers"><div><strong>{(m.accuracy*100).toFixed(2)}%</strong><small>ACCURACY</small></div><div><strong>{m.macro_f1.toFixed(4)}</strong><small>MACRO F1</small></div></div><p>Train: {m.train_count} / Test: {m.test_count}</p><div className="matrix">{m.confusion_matrix.map((row,i)=>row.map((n,j)=><div key={`${i}-${j}`} className={i===j?'diagonal':''} title={`actual ${m.classes[i]}, predicted ${m.classes[j]}`}>{n}</div>))}</div><p className="tiny">Confusion matrix: rows = actual (3, 20, 100), columns = predicted (3, 20, 100).</p></div>)}</div>}</>}
      <footer>© 2026 ECHO-17 · Research prototype · UCI 447 · Never substitute for maintenance safety decisions.</footer>
    </main>
  </div>
}
