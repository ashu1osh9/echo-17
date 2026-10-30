# ECHO-17 Architecture / honest scope

- Real original UCI sensor data; cached small downsampled replay points are selected from the recorded samples, not generated.
- Six observed sensor channels (PS1, FS1, TS1, TS2, VS1, EPS1); 36 summary features from mean, std, min, max, p05, p95.
- Only cooler condition classification in the starter; not remaining useful life or real equipment diagnosis.
- Random Forest trained locally on CPU; optional TabPFN checkpoint/inference run on Colab GPU.
- `/api/diagnose` serves real precomputed predictions on held-out cycles, rather than pretending to call the model live.
- `/api/reveal` serves recorded labels after a deliberate user action; labels are not features.
- Genuine local Gemma 3 1B evidence planning is verified through Ollama 0.40.13 on CPU. `investigator.build_evidence` compiles six real sensor summaries (36 statistics), the selected model's saved prediction/probabilities and six aligned Ghost comparisons. The target condition/stability are excluded; reference matching still uses only eligible TRAIN cycles.
- `gemma_service` checks local Ollama/model identity, sends the evidence and a dynamic JSON schema to `/api/generate`, and validates the returned plan with Pydantic. The plan contains only allowed evidence IDs and a closed cautious hypothesis choice. Unknown/duplicate IDs, extra fields, free-form readings, wrong model or incomplete output are rejected. No arbitrary LLM prose is accepted as fact; the backend renders all numbers and statements from evidence.
- `report_schema.ForensicReport` validates the six-section API response: context, measured signal evidence, descriptive reference comparison, selected-model prediction, hypothesis/uncertainty and limitations. Evidence hashes, actual local model digest and response timing support auditing. Probabilities remain uncalibrated; no new calibration or classifier training occurs.
- `/api/investigator/status` checks reachability/model installation without inference. `/api/investigate/{cycle_id}?model=...` performs real local Gemma inference or returns an explicitly labeled deterministic fallback with a sanitized reason. No recorded target label is included in either mode or in error messages; Reveal remains separate.
- Local HTTP loopback URLs only; environment proxies, redirects and cloud model tags are rejected. One generation slot bounds local CPU concurrency. URL/model/timeout are configurable. No private credentials are required or embedded; models and runtime logs remain ignored artifacts. A hosted backend requires its own authorized local runtime; remote hosting cannot use this laptop's localhost. See [GEMMA_INVESTIGATOR.md](GEMMA_INVESTIGATOR.md).
- Random split gives a useful initial benchmark, but multiple cycles from the same experimental rig are correlated. Do blocked/chronological evaluation before making generalization claims.
- Production is intentionally out of scope. TabPFN weights non-commercial; review separate license.

## Public release boundary

The public data allowlist contains original RF experiment inputs, measured previews and four genuine RF-grounded Gemma reports. No TabPFN output or model weight is included. `ECHO_PUBLIC_MODEL_POLICY=rf_only` suppresses optional model prediction, evaluation and comparison routes even if research files exist. A mixed-model report registry is rejected under that policy.

`ECHO_REPORT_MODE=precomputed` prevents live LLM calls. Reports distinguish precomputed/live/non-LLM execution. `ECHO_DATA_ROOT` selects the isolated public dataset; the original research tree is preserved. Public readiness validates RF inputs and measured signal availability without requiring a restricted model.

The Render Blueprint uses one Docker Free service with a non-root runtime, static React assets and same-origin API. It fetches a trusted RF-only bundle at build time. No deployment has occurred. The complete earlier research architecture/logs are preserved in the ignored private snapshot; public docs contain no TabPFN numerical output.
