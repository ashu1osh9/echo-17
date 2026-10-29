# ECHO-17 — The Last Signal: Winning-Focused Build Blueprint

**Build window:** October 29–31, 2026 (IST)  
**Internal code freeze:** October 31, 15:00 IST  
**Internal verified submission target:** October 31, 20:00 IST  
**Status:** A runnable starter exists, and 5 isolated backend tests passed on Oct 29. The real UCI data run, GPU experiment, hosted deployment, frontend build and challenge entry are **not yet verified**.

## 0 — The entry gate: verify the contest FIRST

1. Sign in at https://dev.to/challenges/hacktoberfest-week4-2026-10-26.
2. Check that the actual submission flow accepts a Week 4 entry. The public challenge page currently says **Live Ended**, despite listing an Oct 31 deadline. Do not assume that publishing a DEV post is the same as a confirmed challenge entry.
3. Ensure the new work and GitHub repository date from Oct 26–31, 2026; preserve originality and attribute every external dataset, design or model.
4. Official rules require **one submission**, in **English**, with a DEV post using the submission template/tag, demo link/video, repository URL, and the role of open-source AI. One entry can qualify for several partner categories but **can only win once**.

**Gate result:** If the form is closed, verify announcements or contact organizers immediately; proceed with portfolio build only with clear expectations.

## 1 — Final thesis and differentiator

> ECHO-17 resurrects forgotten machine recordings. It replays a real 60-second hydraulic experiment, contrasts it with an archived full-cooler-efficiency reference, calls an actual open-weight tabular foundation model to classify the condition, generates evidence-grounded analysis, and finally reveals the experimental label so the audience can check whether the prediction was correct.

### The signature 60-second demo: 'The Last Signal'

1. **0–8 seconds:** Open the mysterious historical sensor archive. Show the real dataset attribution and record count.
2. **8–19 seconds:** Select a HELD-OUT experiment cycle, preview the waveform; click **Reveal Ghost Signature** to overlay a real 100%-cooler-efficiency TRAIN reference. Explain that matching is a descriptive similarity, not proof of cause.
3. **19–31 seconds:** Click **Run AI diagnosis**; show RF and, once genuinely run, TabPFN predictions and their **model-reported** probabilities. These are saved precomputed inference results in the demo, not an online GPU model.
4. **31–42 seconds:** Ask the Gemma investigator for its evidence-grounded interpretation if actually available; otherwise label the deterministic fallback without claiming the Gemma prize.
5. **42–52 seconds:** Click **Reveal recorded truth**; show a correct AND an incorrect prediction in the full article/demo if such a case actually exists.
6. **52–60 seconds:** Open evaluation screen showing *observed* accuracy, macro-F1 and confusion matrix with caveats; point to the reproducible open-source repo.

The key narrative is not 'AI predicts future breakdowns'; this dataset supports **classification of experimentally recorded component conditions**. Avoid causal claims and production safety advice.

## 2 — The exact technical scope

**Real dataset:** UCI Hydraulic Condition Monitoring, 2,205 experimental 60-second cycles, 17 channels total, multiple condition labels in profile.txt. Attribution: Helwig, Pignanelli and Schütze (2015), DOI 10.24432/C5CW21, CC BY 4.0.

**MVP implementation:** The starter deliberately uses SIX of the recorded channels (PS1, FS1, TS1, TS2, VS1, EPS1), extracts SIX features each (mean, standard deviation, min, max, 5th and 95th percentiles) = **36 predictor features**. It classifies **cooler condition** into **3, 20 and 100**. It's okay to retain six sensors; breadth must not jeopardize verification. Never report 17 sensors in the starter model unless the code actually processes all 17.

**Baseline:** Random Forest on CPU; stratified 80/20 held-out evaluation; save train/test IDs, class-wise metrics and raw predictions. Exclude IDs, target labels and stability flag from X. Do not cherry-pick only correct examples.

**Partner technology:** TabPFN-3.5 on Google Colab GPU if license and GPU permit, using IDENTICAL train/test IDs and features. Record environment versions, train/test counts, confusion matrix and actual outcome. TabPFN may underperform RF: truthfully report it; this isn't a failure of the project.

**Ghost Signature:** Select closest *training* cycle with cooler efficiency 100, preferably stable, using standardized sensor-summary distance computed using train-only scaling. Overlay measured downsampled samples from UCI. **A full cooler does not imply all other components are healthy.** The distance is NOT an anomaly probability or cause attribution. Backend route: `GET /api/ghost/{cycle_id}?sensor=PS1`.

**Report:** Gemma 3, locally via Ollama, uses only structured evidence + model outputs. The UI must show its source; if Gemma unavailable, deterministic fallback displays explicitly and does not count as Gemma integration. Constrain numerical claims and allow the reader to inspect raw evidence.

**Deployment:** The public demo may serve genuine precomputed ML results. It MUST be visibly labeled as such; live CPU-based backend may run on Render if feasible. Do not imply GPU inference is happening on Render. Never ship checkpoint weights/tokens or claim licensed noncommercial TabPFN weights as unrestricted OSS.

## 3 — Hard priorities and cut line

| Priority | Feature | Done only when |
|---|---|---|
| P0 | Working challenge entry | Signed-in form is verified, new GitHub repo is present |
| P0 | Actual UCI pipeline | 2,205 aligned records, 36 feature columns, real recorded signals |
| P0 | RF metrics | Run produces numeric JSON + CSV from held-out actual predictions |
| P0 | Full app demo | Select cycle → measured waveform → diagnose → reveal → evaluation works |
| P0 | English submission | Real demo, repo, detailed story, evidence and required tags |
| P1 high | TabPFN-3.5 | Genuine GPU/CPU run, same IDs, actual scores; licenses accepted |
| P1 high | Ghost Signature | Measured overlay only, reproducible reference selection, truthful labels |
| P1 | Gemma | Actual model output + evidence restrictions; fallback is labeled |
| P1 | Render | Accessible hosted URL with real data and no fake claims |
| P2 CUT | RAG, voice, multi-agent frameworks, authentication, database, 17-sensor model, 4-component classification | Do not start before full submission ready |

Even when an advertised partner category applies, only LIST it after verified meaningful integration. Do not spread energy across 20 partner technologies; primary targets are **Overall + TabPFN**, then **Gemma + Render** only if actually implemented.

## 4 — Day-by-day: owner, commands, proof

### Oct 29, remaining time — Foundation, no design distractions

**You:** check official signed-in contest entry flow; create a new public GitHub repository named `echo-17`; push code; set up Colab + Prior Labs license acceptance. Do not upload any API tokens.

**Codex in VS Code:** 

```powershell
cd backend
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m pytest -q
python -m ml.download_data
python -m ml.prepare
python -m ml.train_baseline
python -m uvicorn app.main:app --reload
```

**Acceptance evidence:** `features.csv` has 2,205 rows, 36 predictors (not 102); the actual baseline metrics JSON and held-out CSV exist; `/api/health` is ready; `/api/diagnose/{id}` produces saved model predictions. Include actual outputs with exact commands in `docs/RUN_LOG.md`. No reported metrics until executed.

**If dataset download fails:** get the official 73.1 MB ZIP manually from UCI and extract required files, then retry preprocessing. Do not use mocked data.

### Oct 30 — Colab and full working app

**You:** Open `notebooks/tabpfn_colab.ipynb` in Colab; runtime → T4 GPU (if available); upload the updated project ZIP; run cells in order. TabPFN 3.5 may request license login/token; keep token out of the repository. Download `echo17_results.zip` with the original test IDs, prediction CSV, metrics JSON and processed replay files.

**Codex:** Make the API/UI reliable; load actual artifacts. Confirm `Ghost Signature` reference is a measured training cycle, and make sure swapping sensors/cycles cannot show stale predictions or mismatched signals. Document that inference in hosted demo is precomputed. Run:

```powershell
cd frontend
npm install
npm run build
npm run dev
```

**Acceptance evidence (Oct 30 21:00 IST):** Watch a complete screen-recordable investigation from a real held-out cycle. Frontend production build succeeds; API tests pass. If TabPFN fails after reasonable troubleshooting, keep the RF demo and do not make a false partner claim.

### Oct 31 — No major new features; publish and submit

- **09:00–11:00:** fix crashes and misleading copy; test at least 3 real cycles and at least 2 sensors; check no ground-truth leak before reveal.
- **11:00–13:00:** optional genuine Gemma run; if it cannot be verified, use honest deterministic fallback.
- **13:00–15:00:** deploy if feasible; record a usable video even if hosting fails; create screenshots only from actual running app.
- **15:00:** **CODE FREEZE**, no new framework or database.
- **15:00–17:00:** produce English DEV article, architecture, method, results and limitations.
- **17:00–19:00:** publish DEV entry, ensure unique challenge tags/template and listed prize categories are justified; submit through actual challenge flow.
- **20:00:** verify entry appears successfully; record link or receipt. This is our hard internal deadline.

## 5 — Official rules: what must be in the post

Write an English narrative with the required submission template and `#devchallenge`, `#hf26challenge` tags. Include:

- The emotional hook behind 'The Last Signal' and how it interprets Ghost in the Machine.
- What exactly the viewer can do; a visible 45–75-second demo with no fabricated outcomes.
- UCI dataset origin, row structure, target labels, sensor count and credit.
- Feature engineering, split protocol, baseline RF, actual TabPFN version and real metrics where available.
- Three evidence screenshots: ghost overlay, truth reveal, confusion matrix.
- Open model role, local reproducibility, model licenses, when cloud/GPU is used and why openness matters.
- An honest limitations section (dataset from one test rig, random held-out split tests within-rig interpolation, no guaranteed failure prediction, no calibrated probabilities).
- GitHub URL, demo/video URL, categories where genuinely eligible and reproducible commands.
- One meaningful failure case and what it teaches, if verified.

**Suggested article title:** *I Replayed the Last Signals of a Machine — and Let Open AI Investigate What Happened*.

## 6 — Exact Codex handoff

Paste the following into VS Code Codex from the extracted project root:

```text
You are the senior engineer for ECHO-17, a new Week-4 Hacktoberfest 2026 project.
HARD deadline: finished and verifiably submitted by Oct 31 20:00 IST.
Read AGENTS.md, README.md, docs/31_OCT_DEADLINE_SPRINT.md,
docs/WINNING_BLUEPRINT_31_OCT.md and docs/TASK_CHECKLIST.md first.

This starter ALREADY contains React, FastAPI, UCI data scripts, RF training,
TabPFN training, Gemma fallback, and Ghost Signature API/UI. Do not scaffold
from scratch or introduce an agent framework/database.

First P0 unit of work: install backend requirements, run tests, fetch UCI 447,
prepare exactly 2205 aligned cycles with the six chosen sensor files and 36
statistical predictors, run the RF baseline, save actual metrics/predictions.
Then test /api/health, /api/cycles, /api/ghost/{id}, /api/diagnose/{id},
/api/reveal/{id}, /api/evaluation. Verify the frontend production build.

No invented datasets, hardcoded metrics, mock production predictions, false
'live GPU' labels, hidden data leakage, or unsupported maintenance claims.
When blocked by a required external step (Colab license, login, DEV upload),
report the exact action the human must do and continue other P0 tasks.
After each task: report changed files, commands ACTUALLY run, outputs,
errors, and next action; update docs/TASK_CHECKLIST.md ONLY after verification.
Prioritize end-to-end functionality and submission over polish.
```

## 7 — Decisions to avoid wasting time

**Never** run uncontrolled AI code generation that rewrites the entire repository. Commit at each green milestone. Use one Codex task at a time with measurable acceptance criteria. Human performs login, license acceptance, Colab GPU selection, GitHub repo creation and final DEV submission; Codex handles local code/testing. If Codex access to Colab isn't connected, manually run the provided notebook.

**What 'win-worthy' means:** not maximum feature count, but the combination of one unforgettable live reveal, actual reusable code, independently checkable evidence, excellent clear writing and honest limitations. There is no guarantee of winning.

## 8 — Source links

- Challenge and judging: https://dev.to/challenges/hacktoberfest-week4-2026-10-26
- Official contest rules: https://dev.to/page/hacktoberfest-week4-2026-10-26-contest-rules
- UCI dataset: https://archive.ics.uci.edu/dataset/447/condition+monitoring+of+hydraulic+systems
- UCI DOI: https://doi.org/10.24432/C5CW21
- TabPFN: https://github.com/PriorLabs/TabPFN
- TabPFN-3.5 non-commercial model card: https://huggingface.co/Prior-Labs/tabpfn_3_5
