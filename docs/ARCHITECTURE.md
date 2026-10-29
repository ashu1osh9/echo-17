# ECHO-17 Architecture / honest scope

- Real original UCI sensor data; cached small downsampled replay points are selected from the recorded samples, not generated.
- Six observed sensor channels (PS1, FS1, TS1, TS2, VS1, EPS1); 36 summary features from mean, std, min, max, p05, p95.
- Only cooler condition classification in the starter; not remaining useful life or real equipment diagnosis.
- Random Forest trained locally on CPU; optional TabPFN checkpoint/inference run on Colab GPU.
- `/api/diagnose` serves real precomputed predictions on held-out cycles, rather than pretending to call the model live.
- `/api/reveal` serves recorded labels after a deliberate user action; labels are not features.
- Optional Gemma interpretations can hallucinate. UI surfaces source and structured evidence; do not over-claim factual enforcement of prose.
- Random split gives a useful initial benchmark, but multiple cycles from the same experimental rig are correlated. Do blocked/chronological evaluation before making generalization claims.
- Production is intentionally out of scope. TabPFN weights non-commercial; review separate license.
