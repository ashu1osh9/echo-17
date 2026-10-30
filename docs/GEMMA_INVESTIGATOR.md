# Mission 4: real local Gemma investigator

Verified on 30 October 2026 using **Gemma 3 1B**, `gemma3:1b`, Q4_K_M, Ollama **0.40.13**, CPU inference (`/api/ps` reported `size_vram: 0`). The machine had 15.4 GiB RAM, about 3.21 GiB available at inspection, so 1B was chosen over 4B. No sensor data was sent to an external inference provider. Initial model download uses the official Ollama registry; subsequent report generation is local.

The installed Ollama 0.16.1 was not running and could not pull the current model (HTTP 412, newer runtime required). The official [portable Windows release](https://github.com/ollama/ollama/releases/tag/v0.40.13) was downloaded into ignored workspace storage. Archive SHA-256 matched the official release metadata: `7afa38624fa62ee5d8293422d0ab084c1bb4603134c7f4dafce11a033b57cc19`. No system installation or global environment settings were changed. The existing installed runtime and unrelated models were preserved.

## Local setup and restart

With this prepared workspace, from `D:\AI_Space\echo-17\backend`:

```powershell
# Reuses a responding localhost server; otherwise starts the prepared portable runtime hidden.
& ./.venv/mission1/Scripts/python.exe -m ml.start_ollama
Invoke-RestMethod http://127.0.0.1:11434/api/version
Invoke-RestMethod http://127.0.0.1:11434/api/tags
& ./.venv/mission1/Scripts/python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

The runtime, model weights and runtime logs are all under ignored `backend/artifacts/ollama/`. They are not Git deliverables. On a fresh checkout, obtain a current official Ollama runtime using the [Windows instructions](https://docs.ollama.com/windows); review the [Gemma model terms](https://ollama.com/library/gemma3:1b). Start `ollama serve` with `OLLAMA_HOST=127.0.0.1:11434`, `OLLAMA_MODELS` pointing inside ignored workspace storage and cloud disabled, then run `ollama pull gemma3:1b`. Do not overwrite the prepared model directory or copy secrets. The helper only starts an existing prepared runtime; it does not download, install or accept terms.

The FastAPI process reads these optional settings at request time:

| Variable | Default / constraint |
|---|---|
| `OLLAMA_URL` | `http://127.0.0.1:11434`; HTTP loopback only, explicit port, no credentials/path/query/fragment |
| `OLLAMA_MODEL` | `gemma3:1b`; installed local `gemma3:` tag required; cloud tags rejected |
| `OLLAMA_TIMEOUT_SECONDS` | `120`; permitted range 5–180 seconds |

No keys or authentication tokens are needed. Environment proxies and HTTP redirects are disabled for evidence requests. The backend checks `/api/version` and `/api/tags`, including family `gemma3` and the model digest. `/api/investigator/status` returns clear ready/unavailable state without invoking the model. Ready status means installed and reachable, not guaranteed successful generation. One report generation is allowed per backend process; concurrent requests receive a labeled fallback rather than queueing unbounded CPU work.

## Evidence and output contract

`build_evidence()` uses the selected model's saved prediction and uncalibrated probabilities, six measured full-recording sensor summaries (36 statistics), and aligned measured Ghost comparisons for all six channels. It reuses the existing TRAIN-only full-cooler reference selection. RMSE is calculated on the rounded preview values supplied by Ghost; mean difference uses the existing Ghost field. These are preview statistics, not additional model inputs or calibrated anomaly scores. The target cycle's recorded condition and stability never enter the evidence or prompt.

Gemma is a **bounded evidence planner**, not a free-form report writer. It receives a JSON schema and the supplied evidence. It selects/orders three to six distinct sensor summaries, one to three reference comparisons and one of two cautious uncertainty framings. Pydantic rejects extra fields, duplicate/unknown references, fabricated numbers, invalid JSON and unsupported hypotheses. Incomplete generation or a different returned model is rejected. The backend renders all numerical statements and model diagnosis from source evidence. This prevents generated numerical claims rather than attempting to certify arbitrary LLM prose.

The Pydantic-validated API report contains six sections: case summary, observed signal evidence, comparison to training reference, model diagnosis, hypothesis/uncertainty and limitations. Each distinguishes measurement, prediction, hypothesis or limitation. The report also returns selected model, evidence hash, local model identity/digest, timing and the validated plan. The source label is **Local Gemma / validated evidence plan**, with an explicit explanation of backend rendering. A genuine LLM call is required for this label. Connection/model/timeout/schema/grounding failures return **Rule-based / non-LLM fallback**, a safe reason code and the same grounded report structure. Raw invalid output and error bodies are not returned or persisted.

Neither report mode knows whether the prediction matches the held-out label. Reveal is still a separate deliberate UI/API interaction. This is narrative concealment, not access control. TRAIN reference labels may identify a full cooler; that says nothing about the selected held-out label or other reference components.

## Actual execution evidence

Model digest: `97558784bdc9175075a72655bf360b15da17df6b3b9e5182af9f8c0c8e58ba7c`; local model size 806,067,407 bytes. Generation uses temperature 0, seed 42, context 4096, maximum 256 output tokens and two-minute keep-alive. Hardware/timing can change results and latency.

From `backend`, this executed genuine local calls through the frontend proxy and failed unless both reports were real Gemma:

```powershell
& ./.venv/mission1/Scripts/python.exe -m ml.verify_investigator --base-url http://127.0.0.1:5173 --model 'Random Forest' --require-gemma --output mission4_gemma_final_verification.json
```

| Cycle | Source | Local generation/adaptor time | Selected evidence |
|---|---|---:|---|
| 735 | `ollama:gemma3:1b` | 19.889 s | All six sensor summaries; PS1, FS1 and TS1 comparisons against TRAIN 1850 |
| 5 | `ollama:gemma3:1b` | 18.990 s | All six sensor summaries; PS1 comparison against TRAIN 2169 |

Both returned `mode: gemma`, no fallback, and passed schema, evidence membership, hash and exact rendering checks. The earlier `mission4_gemma_verification.json` is preserved: it also records genuine calls (29.379/27.933 seconds), but its first plan repeatedly selected pressure statistics; summaries were then grouped per sensor to improve coverage. The final file's legacy `http_seconds` field includes HTTP plus local revalidation, not pure HTTP latency; the CLI now names that measure `verification_seconds`. The table uses the actual adapter `response_seconds`, excluding evidence compilation/CLI validation. The sanitized files remain ignored and contain no credentials.

Actual cycle 735 report excerpts (numbers are backend-rendered from measured evidence, selected by Gemma):

> TS1: mean=54.0405; std=0.1404; min=53.7620; max=54.4260; p05=53.8478; p95=54.2586 °C (measured full-recording statistics; every value uses this unit).
>
> TS1: aligned preview mean difference +17.6889 °C; RMSE 17.6902 °C against TRAIN recording 1850.

RF diagnosis in that same report is near failure (3%) with model-reported confidence 50.4%; it is explicitly a **prediction**, not the recorded condition. The uncertainty section says reference differences do not establish a physical fault cause. No causal fault explanation or maintenance advice was generated.

## Verification and deployment limits

`python -m pytest -q` covers real evidence compilation, invariance to changed held-out labels, strict schema, prompt concealment, invalid/unknown fields, failed connections, timeouts, unavailable/wrong models, external URL/redirect rejection, proxy isolation and busy state. `npm test` uses actual API reports for model switching, concealment, section rendering, loading and HTTP-error retry; chart layout alone is stubbed. See [RUN_LOG.md](RUN_LOG.md) for exact environment commands/results.

The frontend is at `http://127.0.0.1:5173/#/investigation/735` (also cycle `5`); API docs at `http://127.0.0.1:8000/docs`. Diagnose, select RF or TabPFN, generate the report and inspect the source/time/sections before Reveal. Stop or misconfigure Ollama to inspect the transparent fallback, then restore the configuration. Existing replay, Ghost and evaluation behavior is preserved.

This is a local research demonstration. A remotely hosted backend cannot reach this laptop via its own `localhost`; it needs a separately provisioned, licensed local inference runtime or must show fallback. No deployment or public GPU service was configured. Small-model evidence selection is not expert diagnosis. Probabilities remain uncalibrated; the original single-rig random split and causal limitations still apply. No new browser visual verification or screenshot is claimed by the automated report checks.

The final public candidate uses `ECHO_REPORT_MODE=precomputed` and `ECHO_PUBLIC_MODEL_POLICY=rf_only`. It includes four genuine RF-grounded reports for the four demo cycles. Reports based on the restricted research model are excluded. The local default remains live-local; no hosted live inference is claimed. See RELEASE_HANDOFF.md for current instructions.
