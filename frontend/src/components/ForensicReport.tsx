import type { Report } from '../api'

const fallbackReasons: Record<string, string> = {
  model_not_installed: 'The configured Gemma model is not installed locally.',
  ollama_timeout: 'Local generation exceeded its time limit.',
  ollama_busy: 'The local investigator is already processing another request.',
  invalid_configuration: 'The local investigator configuration needs attention.',
  precomputed_report_missing: 'No genuine saved Gemma report exists for this recording and model.',
  precomputed_report_invalid: 'The saved report did not match the current measured evidence.',
  ungrounded_output: 'The generated evidence references did not pass validation.',
  invalid_or_unavailable_output: 'The local response was unavailable or did not pass validation.',
}

export default function ForensicReport({ report }: { report: Report }) {
  return <div className="report" aria-live="polite">
    <div className="report-source"><span className="statusdot" /><strong>{report.mode === 'gemma' ? report.inference_mode === 'precomputed' ? 'Precomputed Gemma / validated evidence plan' : 'Local Gemma / validated evidence plan' : 'Rule-based / non-LLM fallback'}</strong><small>{report.source}</small></div>
    {report.fallback_reason && <p role="status">{fallbackReasons[report.fallback_reason] ?? 'Local Gemma could not provide a validated report.'} The report below uses deterministic evidence selection.</p>}
    {report.mode === 'gemma' && <p className="footnote">{report.generation.model} · {report.generation.response_seconds?.toFixed(2)} s original generation time · {report.inference_mode === 'precomputed' ? 'Precomputed from genuine model inference. No live LLM inference on this server.' : 'Live local evidence selection.'} Numerical facts are rendered from recorded evidence.</p>}
    {report.sections.map(section => <section key={section.title}><div className="section-heading"><h3>{section.title}</h3><span className="tag">{section.kind.replace('_', ' ')}</span></div><ul className="fact-grid">{section.statements.map(statement => <li key={statement}>{statement}</li>)}</ul></section>)}
    <h3>Measured evidence index</h3><ul className="fact-grid">{report.structured_evidence.map(fact => <li key={fact}>{fact}</li>)}</ul>
    <p className="footnote">{report.warning}</p>
  </div>
}
