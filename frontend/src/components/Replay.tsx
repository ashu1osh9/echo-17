import { useEffect, useMemo, useRef, useState } from 'react'
import { Activity, GitCompareArrows, Pause, Play, RotateCcw, Waves } from 'lucide-react'
import { Area, CartesianGrid, ComposedChart, Line, ReferenceLine, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'
import { api, type GhostSignature, type Sensor, type Signal } from '../api'
import { advanceTime, alignedGraph, previewDifferences, sensorNames } from '../domain'
import { ErrorNotice, Loading } from '../App'

export default function Replay({ id, sensor }: { id: number; sensor: Sensor }) {
  const [signal, setSignal] = useState<Signal | null>(null)
  const [ghost, setGhost] = useState<GhostSignature | null>(null)
  const [error, setError] = useState('')
  const [ghostError, setGhostError] = useState('')
  const [attempt, setAttempt] = useState(0)
  const [ghostBusy, setGhostBusy] = useState(false)
  const [cursor, setCursor] = useState(60)
  const [playing, setPlaying] = useState(false)
  const [speed, setSpeed] = useState(1)
  const position = useRef(60)
  const ghostRequest = useRef<AbortController | null>(null)
  const move = (value: number) => { position.current = value; setCursor(value) }
  useEffect(() => {
    const request = new AbortController()
    setSignal(null); setGhost(null); setError('')
    api.signal(id, sensor.name, request.signal).then(data => {
      if (!request.signal.aborted && data.cycle_id === id && data.sensor === sensor.name) setSignal(data)
    }).catch(e => { if (!request.signal.aborted) setError(e.message) })
    return () => { request.abort(); ghostRequest.current?.abort() }
  }, [id, sensor.name, attempt])
  useEffect(() => {
    if (!playing) return
    let frame = 0, last = performance.now()
    const tick = (now: number) => {
      if (now - last >= 70) {
        const next = advanceTime(position.current, now - last, speed)
        move(next); last = now
        if (next >= 60) { setPlaying(false); return }
      }
      frame = requestAnimationFrame(tick)
    }
    frame = requestAnimationFrame(tick)
    return () => cancelAnimationFrame(frame)
  }, [playing, speed])
  useEffect(() => { const hidden = () => { if (document.hidden) setPlaying(false) }; document.addEventListener('visibilitychange', hidden); return () => document.removeEventListener('visibilitychange', hidden) }, [])
  const graph = useMemo(() => signal ? alignedGraph(signal, ghost, cursor) : [], [signal, ghost, cursor])
  const domain = useMemo(() => {
    const values = [...(signal?.values ?? []), ...(ghost?.reference_values ?? [])]
    if (!values.length) return [0, 1]
    const min = Math.min(...values), max = Math.max(...values), padding = (max - min || 1) * .12
    return [min - padding, max + padding]
  }, [signal, ghost])
  const difference = ghost ? previewDifferences(ghost) : null
  async function loadGhost() {
    ghostRequest.current?.abort()
    const request = new AbortController(); ghostRequest.current = request
    setGhostBusy(true); setGhostError('')
    try {
      const data = await api.ghost(id, sensor.name, request.signal)
      if (!request.signal.aborted && data.cycle_id === id && data.sensor === sensor.name) {
        if (!signal || data.times.length !== signal.times.length || !data.times.every((t, i) => t === signal.times[i])) throw new Error('Reference timestamps do not align with this recording.')
        setGhost(data)
      }
    } catch (e) { if (!request.signal.aborted) setGhostError(e instanceof Error ? e.message : String(e)) }
    finally { if (!request.signal.aborted) setGhostBusy(false) }
  }
  return <section className="panel replay-panel" aria-labelledby="replay-title">
    <div className="section-heading"><div><div className="panel-label">02 / SENSOR REPLAY</div><h2 id="replay-title"><Activity size={20} className="sea" />{sensorNames[sensor.name] ?? sensor.name} <span className="tag">{sensor.name}</span></h2></div><div className="signal-readout"><span>LAST VISIBLE MEASUREMENT</span><b>{graph.length ? `${graph[graph.length - 1].value.toFixed(3)} ` : '—'}<small>{signal?.unit}</small></b></div></div>
    <div className="chart-legend"><span><i />Selected cycle</span>{ghost && <span className="reference"><i />Train reference #{ghost.reference_cycle_id}</span>}<span className="chart-unit">{sensor.unit} / {sensor.rate_hz} Hz original</span></div>
    <div className="chartarea" aria-label={`${sensor.name} measured waveform for cycle ${id}`} role="img">
      {error ? <ErrorNotice message={error} retry={() => setAttempt(a => a + 1)} /> : !signal ? <Loading text="Loading original sensor samples…" /> : <ResponsiveContainer width="100%" height="100%" debounce={80}><ComposedChart data={graph} margin={{ left: 0, right: 12, top: 14, bottom: 4 }}>
        <defs><linearGradient id="signal-fill" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stopColor="#5bdcc2" stopOpacity={.22} /><stop offset="100%" stopColor="#5bdcc2" stopOpacity={0} /></linearGradient></defs>
        <CartesianGrid stroke="#23343a" strokeDasharray="2 6" vertical={false} />
        <XAxis dataKey="t" type="number" domain={[0, 60]} ticks={[0, 10, 20, 30, 40, 50, 60]} stroke="#8a9da5" axisLine={false} tickLine={false} tick={{ fontSize: 11 }} tickFormatter={v => `${v}s`} />
        <YAxis domain={domain} width={60} stroke="#8a9da5" axisLine={false} tickLine={false} tick={{ fontSize: 11 }} tickFormatter={v => Number(v).toFixed(1)} />
        <Tooltip contentStyle={{ background: '#12252b', border: '1px solid #43616a', borderRadius: 8, color: '#edf6f4', fontSize: 12 }} labelFormatter={v => `Recorded at ${Number(v).toFixed(3)} s`} formatter={(value, name) => [`${Number(value).toFixed(3)} ${sensor.unit}`, name === 'reference' ? 'Training reference' : 'Selected recording']} />
        <Area type="linear" dataKey="value" stroke="#5bdcc2" fill="url(#signal-fill)" strokeWidth={1.8} isAnimationActive={false} dot={false} />
        {ghost && <Line type="linear" dataKey="reference" stroke="#efb46e" strokeDasharray="5 4" strokeWidth={1.7} dot={false} isAnimationActive={false} />}
        <ReferenceLine x={cursor} stroke="#e7efed" strokeOpacity={.55} strokeDasharray="3 4" />
      </ComposedChart></ResponsiveContainer>}
    </div>
    <div className="transport"><button className="play-button" disabled={!signal} aria-label={playing ? 'Pause replay' : 'Play replay'} onClick={() => { if (cursor >= 60) move(0); setPlaying(!playing) }}>{playing ? <Pause size={17} /> : <Play size={17} />}</button><button className="icon-button" aria-label="Reset replay" disabled={!signal} onClick={() => { setPlaying(false); move(0) }}><RotateCcw size={17} /></button><span className="timecode" data-testid="replay-time">{cursor.toFixed(1)}<small> / 60.0 s</small></span><input type="range" min={0} max={60} step={.1} value={cursor} aria-label="Replay position in seconds" disabled={!signal} onChange={e => { setPlaying(false); move(Number(e.target.value)) }} /><select aria-label="Replay speed" value={speed} onChange={e => setSpeed(Number(e.target.value))}>{[.25, .5, 1, 2, 4].map(value => <option value={value} key={value}>{value}×</option>)}</select></div>
    <div className="chartfoot"><span>{graph.length} / {signal?.values.length ?? '—'} recorded preview points</span><span>{playing ? 'REPLAYING ARCHIVE' : cursor >= 60 ? 'FULL RECORDING PREVIEW' : 'REPLAY PAUSED'} · Lines connect recorded samples</span></div>
    <div className="ghost-section"><div className="section-heading"><div><div className="panel-label amber">GHOST SIGNATURE</div><h3>A reference from the archive.</h3><p>Compare with a measured training recording with full cooler efficiency.</p></div><button className="secondary" disabled={!signal || ghostBusy} onClick={loadGhost}><GitCompareArrows size={17} />{ghostBusy ? 'Finding reference…' : ghost ? 'Refresh comparison' : 'Reveal Ghost Signature'}</button></div>
      {ghostError && <ErrorNotice message={ghostError} retry={loadGhost} />}
      {ghost && <div className="ghost-result"><div className="ghost-title"><Waves size={22} /><div><strong>Training cycle #{ghost.reference_cycle_id}</strong><p>{ghost.reference_definition}</p></div><span className="tag amber">TRAIN ONLY</span></div>{difference && <div className="difference-grid"><div><small>PREVIEW MEAN Δ</small><b>{difference.mean.toFixed(3)} <span>{ghost.unit}</span></b></div><div><small>ALIGNED PREVIEW RMSE</small><b>{difference.rmse.toFixed(3)} <span>{ghost.unit}</span></b></div><p>Selected minus reference, using aligned displayed samples. Descriptive differences do not establish causality.</p></div>}<details><summary>How this reference was selected</summary><p>{ghost.selection_method}. Standardization and candidate selection use training data only. Other components may differ. Summary-profile distance: {ghost.distance.toFixed(5)} (dimensionless); not an anomaly probability.</p></details></div>}
    </div>
  </section>
}
