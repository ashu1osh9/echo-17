import { lazy, Suspense, useEffect, useState } from 'react'
import { ArrowUpRight, Archive as ArchiveIcon, FlaskConical, Radio, Waves, ShieldAlert } from 'lucide-react'
import { api, type Cycle, type Metadata } from './api'
import { parseRoute } from './domain'
import { Archive } from './components/Archive'
import { Investigation } from './components/Investigation'
const Evaluation = lazy(() => import('./components/Evaluation'))
export function ErrorNotice({ message, retry }: { message: string; retry?: () => void }) {
  return <div className="error" role="alert"><ShieldAlert size={20} /><div><strong>Unable to complete this request</strong><p>{message}</p>{retry && <button className="text-button" onClick={retry}>Try again <ArrowUpRight size={14} /></button>}</div></div>
}
export function Loading({ text = 'Retrieving recorded evidence…' }: { text?: string }) {
  return <div className="loading" role="status"><span className="spinner" />{text}</div>
}
export default function App() {
  const [route, setRoute] = useState(() => parseRoute(location.hash))
  const [cycles, setCycles] = useState<Cycle[]>([])
  const [meta, setMeta] = useState<Metadata | null>(null)
  const [ready, setReady] = useState(false)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [attempt, setAttempt] = useState(0)
  const [opened, setOpened] = useState<number[]>([])
  useEffect(() => { const change = () => { setRoute(parseRoute(location.hash)); window.scrollTo(0, 0) }; window.addEventListener('hashchange', change); return () => window.removeEventListener('hashchange', change) }, [])
  useEffect(() => {
    const controller = new AbortController()
    setLoading(true); setError('')
    Promise.all([api.health(controller.signal), api.meta(controller.signal), api.cycles(controller.signal)])
      .then(([health, metadata, archive]) => { if (!controller.signal.aborted) { setReady(health.data_ready); setMeta(metadata); setCycles(archive.cycles) } })
      .catch(e => { if (!controller.signal.aborted) setError(e.message) })
      .finally(() => { if (!controller.signal.aborted) setLoading(false) })
    return () => controller.abort()
  }, [attempt])
  useEffect(() => { if (route.page === 'investigation' && route.id && cycles.some(c => c.id === route.id)) setOpened(previous => previous.includes(route.id!) ? previous : [...previous, route.id!]) }, [route, cycles])
  const inArchive = route.page === 'archive'
  return <div className="app">
    <a href="#content" className="skip-link" onClick={e => { e.preventDefault(); document.getElementById('content')?.focus() }}>Skip to content</a>
    <aside className="sidebar">
      <a className="brand" href="#/archive" aria-label="ECHO-17 home"><span className="logo"><Radio size={23} /></span><span><strong>ECHO<span>—17</span></strong><small>MACHINE FORENSICS</small></span></a>
      <div className="navtitle">INVESTIGATION WORKSPACE</div>
      <nav aria-label="Main navigation">
        <a href="#/archive" className={'nav ' + (inArchive ? 'selected' : '')} aria-current={inArchive ? 'page' : undefined}><ArchiveIcon size={18} />Machine archive<span>01</span></a>
        <a href={route.id ? `#/investigation/${route.id}` : cycles[0] ? `#/investigation/${cycles[0].id}` : '#/archive'} className={'nav ' + (route.page === 'investigation' ? 'selected' : '')} aria-current={route.page === 'investigation' ? 'page' : undefined}><Waves size={18} />Signal laboratory<span>02</span></a>
        <a href="#/evaluation" className={'nav ' + (route.page === 'evaluation' ? 'selected' : '')} aria-current={route.page === 'evaluation' ? 'page' : undefined}><FlaskConical size={18} />Model evaluation<span>03</span></a>
      </nav>
      <div className="side-note"><span className="crosshair">+</span><p>Every machine<br />leaves a trace.</p><small>FOLLOW THE EVIDENCE.</small></div>
      <div className="sidefoot"><span className={'statusdot ' + (!ready ? 'offline' : '')} />{ready ? 'REAL DATA CONNECTED' : loading ? 'CONNECTING TO ARCHIVE' : 'ARCHIVE UNAVAILABLE'}<p>UCI hydraulic test rig<br />Research prototype · v0.2</p></div>
    </aside>
    <main className="main" id="content" tabIndex={-1}>
      <header className="top"><div className="eyebrow"><span className="sea">EVIDENCE ROOM</span><span className="slash">/</span>{route.page === 'evaluation' ? 'MODEL VALIDATION' : inArchive ? 'HISTORICAL RECORDINGS' : 'SIGNAL INVESTIGATION'}</div><span className="topbadge"><span className="statusdot" /> UCI 447 · RECORDED DATA</span></header>
      {loading ? <Loading text="Connecting to the machine archive…" /> : error ? <ErrorNotice message={error} retry={() => setAttempt(a => a + 1)} /> : meta && <>
        {inArchive && <Archive cycles={cycles} meta={meta} opened={opened} />}
        {route.page === 'investigation' && (cycles.some(c => c.id === route.id) ? <Investigation key={route.id} id={route.id!} cycles={cycles} meta={meta} /> : <div className="empty panel"><h1>Recording not found.</h1><p>This cycle is not part of the held-out archive.</p><a className="secondary" href="#/archive">Return to archive</a></div>)}
        {route.page === 'evaluation' && <Suspense fallback={<Loading />}><Evaluation conditionLabels={meta.condition_labels} /></Suspense>}
        {route.page === 'missing' && <div className="empty panel"><h1>Page not found.</h1><a className="secondary" href="#/archive">Return to archive</a></div>}
      </>}
      <footer><span><b>ECHO—17</b> / THE MACHINE THAT REMEMBERS</span><p>Historical condition classification · Not a maintenance or future-failure forecast.</p><a href="https://doi.org/10.24432/C5CW21" target="_blank" rel="noreferrer">Helwig, Pignanelli &amp; Schütze · UCI 447 · CC BY 4.0 <ArrowUpRight size={12} /></a></footer>
    </main>
  </div>
}
