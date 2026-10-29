# ECHO-17 — WINNING-FOCUSED IMPLEMENTATION PLAN

> **Project:** ECHO-17 — The Machine That Remembers  
> **Challenge:** DEV Hacktoberfest Open-Source AI, Week 4 — *Ghost in the Machine*  
> **Plan prepared:** 29 October 2026 (Asia/Kolkata)  
> **Hard delivery target:** 31 Oct 2026 **20:00 IST**, with code freeze **15:00 IST**; see `31_OCT_DEADLINE_SPRINT.md`.
> **Project mode:** Reproducible research prototype; not a production industrial safety system  
> **Source of truth:** `31_OCT_DEADLINE_SPRINT.md` for hard cutoffs and feature cuts, this file for detailed implementation; `TASK_CHECKLIST.md` for task tracking; `AGENTS.md` for Codex rules.

---

## 0. READ THIS FIRST (5 MINUTES)

We are **not starting from an empty folder**. A functional starter already exists in this bundle: a FastAPI API, React/TypeScript UI, data downloader/preprocessor, Random Forest baseline, optional TabPFN script, optional Ollama/Gemma integration, and a Colab notebook.

**Verified locally on 29 Oct:** `cd backend && python -m pytest -q` → **4 tests passed**.  
**NOT verified yet:** UCI download, full data preprocessing, actual trained accuracy, TabPFN GPU evaluation, running frontend build, live Gemma output, hosted deployment. **Do not claim they succeeded.**

**MVP promise:** Select a genuinely recorded hydraulic machine cycle → inspect real sensor signals → obtain a real model prediction → read an evidence-restricted explanation → reveal the known condition → compare models using held-out metrics.

**Scope discipline:** First prove ONE end-to-end cooler-condition investigation. Never replace missing measurements or results with dummy signals, hardcoded model scores, or fabricated screenshots.

**Current starter uses 6 real sensor channels** (PS1, FS1, TS1, TS2, VS1, EPS1) × 6 summary statistics = **36 input features**, not all 17 available channels. This is a deliberate rapid-build baseline; adding more channels is a later experiment. The API currently shows a **static signal chart**; animated play/pause/replay is **to be implemented**.

### First thing the builder should do today

1. Sign into DEV and verify that Week 4 submissions are actually enabled. The page text says `Challenge Status: Live Ended` even though its rules list an Oct 31 deadline. Resolve this before investing heavily.
2. Create a **new GitHub repository during Oct 26–31**, not a fork of an old project; push the starter and an initial commit.
3. On Windows, run the baseline pipeline against the **real UCI files** and record measured metrics. This is the single most important technical gate.

---

## 1. Why this project might stand out

**One-sentence hook:** "Can an open-source AI reconstruct what was wrong with a machine from the recordings it left behind?" 

The UCI Condition Monitoring of Hydraulic Systems dataset contains **2,205 real experimental 60-second cycles**, with several sensor recordings and cycle-level annotations for cooler, valve, pump and accumulator conditions. This MVP predicts **cooler condition only**: class `3` = near-total cooler failure, `20` = reduced efficiency, `100` = full efficiency. Those are experimental condition labels, not forecasts of future breakdowns.

**Core innovation beyond an ordinary dashboard:** the viewer sees the **model's prediction before the ground-truth label**, and can inspect both correct and incorrect results. The project should show exactly where model inference ends and actual measured evidence begins.

**What the demo must prove:**
- The waveforms come from UCI recordings, not generated examples.
- A real model was evaluated against a held-out split.
- TabPFN is genuinely used, not mentioned only as a technology badge.
- The explanation is constrained by real sensor summaries; if Gemma is unavailable, display "deterministic fallback," not "Gemma analysis."
- A judge can reproduce at least the CPU baseline using documented commands.

---

## 2. Critical contest rules and submission strategy

**Contest:** https://dev.to/challenges/hacktoberfest-week4-2026-10-26

- **Window:** Oct 26–31, 2026. New project **and its repository** must be started and completed in the challenge window. Any later commits should be identified in README per rules.
- **Published deadline:** Oct 31, 2026 **11:59 PM PDT**, which is **Nov 1, 2026 12:29 PM IST**. Our **internal target is Oct 31 by 8:00 PM IST** to avoid last-minute failures.
- **Page discrepancy:** at the time of planning the DEV page says `Live Ended`; submission availability must be checked by signing in. Do not assume the form is available.
- **Judging:** writing quality carries the most weight; other criteria include prompt/theme relevance, creativity, technical execution, and meaningful partner use.
- **Submission language:** English required for prize eligibility. Template applies `#devchallenge` and `#hf26challenge`.
- **Partner targets:** Best Use of TabPFN; Best Use of Gemma **only if actual Gemma execution is demonstrated**; Best Use of Render **only if actually hosted there**. One submission can enter multiple genuine categories but **can receive at most one prize**.
- **Evidence:** repository URL, public demonstration or reproducible local run, 45–75s demo video, dated measurements and confusion matrix, screenshots of real workflow, source acknowledgments.

### Non-negotiable ethical and licensing boundaries

1. No medical, industrial safety or future-failure guarantee. This is **experimental cooler-condition classification** on a single historical test rig.
2. UCI dataset attribution and terms must be included. Check conditions before redistributing any derived data files.
3. TabPFN 3.5 model weights are under **a separate non-commercial license** (the source code has a different license). Accept license before running; do not bundle weights, tokens or model checkpoint in the ZIP or GitHub repo.
4. Do not publish `.env`, API keys, personal data, unlicensed model weights or large raw files.
5. Cite borrowed components and open-source libraries. The project code's MIT license does not relicense the TabPFN weights.

---

## 3. Architecture (actually implemented or planned)

```text
UCI 447 (raw sensor .txt + profile.txt)
       |
       v
backend/ml/download_data.py [exists]
       |
       v
backend/ml/prepare.py [exists]
  -> backend/data/processed/features.csv   (36 sensor statistics + metadata)
  -> backend/data/processed/signals.npz     (real samples downsampled for display)
       |
       +-----------------------------------------+
       |                                         |
       v                                         v
backend/ml/train_baseline.py [exists]    backend/ml/train_tabpfn.py [exists]
    Random Forest / CPU                     TabPFN-3.5 / Colab GPU
       |                                         |
       +-----------------+-----------------------+
                         v
       backend/artifacts/ (real metrics + predictions + split IDs)
                         |
                         v
        backend/app/main.py (FastAPI) [exists]
                  |                     |
                  v                     v
        React/TypeScript UI      Gemma via Ollama [optional]
         [exists; needs QC]      (structured evidence → narrative)
                  |
                  v
         Predict → Investigate → Reveal truth → Evaluate
```

### Dependencies and hardware

| Work | Runs where | Needs GPU? | Owner |
|---|---|---|---|
| Git, VS Code, Codex, React, FastAPI | Windows laptop | No | Builder + Codex |
| Download / extract UCI / feature statistics | Windows or Colab | No | Codex / Python |
| Random Forest baseline | Windows or Colab | No | Python |
| TabPFN-3.5 evaluation | Google Colab T4 GPU preferred; Kaggle backup | Recommended, not mandatory for very small tasks | Python notebook |
| Gemma via Ollama | Laptop if it fits; optional cloud inference | GPU speeds up, not required | Ollama + API |
| Public demo | Render frontend + lightweight API | No **if serving real precomputed outputs** | Builder |

**GPU is for TabPFN experiments, not for serving the static archive.** A free hosted runtime may not have capacity to run Gemma+TabPFN continuously. Label offline/precomputed predictions honestly.

---

## 4. Real directory layout (already exists)

```text
echo-17/
  README.md                  ← run instructions; explain current capabilities
  AGENTS.md                  ← Codex guardrails & code boundaries
  .gitignore / LICENSE
  backend/
    requirements.txt / .env.example
    ml/
      config.py              ← six channels + UCI path + labels
      download_data.py       ← fetch public archive
      prepare.py             ← compute 36 measured features + preview NPZ
      train_baseline.py      ← RF, split, train/test ids + real metrics
      train_tabpfn.py        ← TabPFN on same split; GPU preferred
    app/
      main.py                ← API endpoint definitions
      services/archive.py    ← real signals/predictions/evaluation
      services/investigator.py ← Gemma prompt + explicit fallback
    data/raw/                ← download-only, gitignored
    data/processed/          ← generated by prep; gitignored
    artifacts/               ← measured outputs, gitignored
    tests/                   ← currently 4 tests passing
  frontend/
    src/App.tsx              ← investigation + evaluation UI
    src/api.ts / style.css
    package.json
  notebooks/
    tabpfn_colab.ipynb       ← GPU run + downloadable results archive
  docs/
    IMPLEMENTATION_PLAN.md  ← this plan
    TASK_CHECKLIST.md       ← tasks, P0/P1 and pass criteria
    CODEX_MASTER_PROMPT.md  ← paste into Codex
    ARCHITECTURE.md
    CODEX_TASK.md
```

---

## 5. Engineering phases with dependencies and acceptance gates

### M0. Repository, environment and rules (Oct 29, ~first session)

**Files:** `README.md`, `.gitignore`, `AGENTS.md`, `docs/*`, `backend/requirements.txt`, `frontend/package.json`.

1. Confirm contest entry is still available by logging in; if not, investigate before continuing under competition expectations.
2. Create a brand-new private/public GitHub repository with dated initial commit; make public when ready. Name suggestion: `echo-17-machine-forensics`.
3. Open the ZIP extracted project in VS Code on Windows. Do **not** overwrite the starter with a fresh Vite scaffold.
4. Install Python 3.12 or compatible Python (3.10+ for TabPFN), Node + npm, Git. For backend use venv; frontend run `npm install`.
5. Run backend tests; capture exact output. Test frontend build when dependencies are installed.

**Pass:** Local tests pass and repository has a dated clean first commit. No secrets, no generated data in Git.

### M1. Real data & reproducible CPU model (Oct 29 — highest priority)

**Files:** `backend/ml/download_data.py`, `prepare.py`, `train_baseline.py`, `tests/*`.

1. Download the original UCI archive (~73 MB compressed; expanded files can be much larger).
2. Confirm `profile.txt` has 2,205 rows / five columns, confirm each selected signal file aligns exactly by row/cycle.
3. Extract 6 statistics × 6 channels = 36 numeric predictors. Exclude `cooler_condition`, **all other profile targets**, stability flag and `cycle_id` from X.
4. Save exact train/test cycle IDs using seed 42 and stratified 80/20 split. **441 test cycles expected** with 2,205 complete rows.
5. Fit Random Forest; save actual metrics, prediction probabilities and held-out cycle IDs.
6. Add tests for shapes, label mapping, no target leakage, deterministic splits and API failure when artifacts are absent.

**Run from `backend` (PowerShell):**

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m ml.download_data
python -m ml.prepare
python -m ml.train_baseline
python -m pytest -q
python -m uvicorn app.main:app --reload
```

**Pass:** `backend/data/processed/features.csv`, `signals.npz`, `backend/artifacts/baseline_metrics.json`, `baseline_predictions.csv`, `train_ids.csv`, `test_ids.csv` exist, based on a real successful run. JSON reports actual accuracy/macro-F1, no hardcoded metrics. `/api/health` has `data_ready: true` and `/api/cycles` lists recorded held-out cycles.

**Important:** If the UCI download fails or runs out of memory, use Google Colab CPU for data preparation. Don't silently truncate or fake data.

### M2. TabPFN-3.5 / Colab GPU (Oct 30 — category-critical)

**Files:** `notebooks/tabpfn_colab.ipynb`, `backend/ml/train_tabpfn.py`, `backend/artifacts/*`.

1. Go to https://colab.research.google.com, select **T4 GPU** if available. If GPU unavailable, Kaggle is the fallback, not an automatic guarantee.
2. Upload the provided `echo-17-starter.zip`. The notebook expects it to unpack into `/content/echo-17`.
3. Open `notebooks/tabpfn_colab.ipynb` (from the ZIP or upload it separately); run the cells sequentially.
4. Accept Prior Labs license/auth flow as required, and verify CUDA availability in notebook. Install the current `tabpfn` package there.
5. Run the **same train/test IDs** from baseline and compare actual metrics; never compare unrelated splits.
6. Download `echo17_results.zip` from the notebook. Extract `artifacts/*.csv`, `artifacts/*.json`, `data/processed/*.csv`, `.npz` into the corresponding **local backend** directories. No need to re-train for every UI test.

**Pass:** `tabpfn_predictions.csv`, `tabpfn_metrics.json` exist and correspond to the same 441 held-out cycle IDs. README includes exact model version, split strategy, runtime/environment and real metrics. If licensing/auth blocks TabPFN, record the blocker truthfully; do not claim category use.

**Research caveat:** random split on consecutive rig cycles can be optimistic. Add a chronological/blocked split as a **secondary robustness experiment** if time allows; keep the existing fixed split for UI comparison. No claim of deployment onto new industrial machines.

### M3. Backend and user journey (Oct 30)

**Files:** `backend/app/main.py`, `services/archive.py`, `services/investigator.py`, `backend/tests/`.

Endpoints already in starter:

| Request | Output / behavior |
|---|---|
| `GET /api/health` | API + whether baseline output exists |
| `GET /api/meta` | sensor list, units, task metadata |
| `GET /api/cycles` | held-out cycle IDs, no actual labels |
| `GET /api/cycles/{id}/signals?sensor=PS1` | downsampled **real** signal samples |
| `POST /api/diagnose/{id}` | real prediction(s) & model probabilities |
| `POST /api/investigate/{id}` | Gemma report **or labeled fallback** |
| `POST /api/reveal/{id}` | actual cooler condition (after UI reveal click) |
| `GET /api/evaluation` | real metrics and confusion matrix |

1. Verify API from `http://localhost:8000/docs` using at least 3 different actual held-out cycles (including a misclassified one, if any).
2. Set error handling for missing artifacts, invalid sensor, invalid ID, and disabled Gemma service.
3. Keep labels hidden in normal selection/diagnosis calls. The reveal endpoint is an **educational UI action**, not a security boundary.
4. Add a verifiable report/evidence schema; record which model, its version and measured sensor summaries contributed to a narrative.

**Pass:** backend has no fake data, stable JSON API, and tests demonstrating missing-data/invalid-ID behavior.

### M4. Distinctive React demo (Oct 30–31)

**Files:** `frontend/src/App.tsx`, `api.ts`, `style.css` and refactored components if needed.

**Already present:** dark forensic dashboard, cycle selection, static real waveform, model prediction, label reveal, evidence display, evaluation screen.

**Build next:**
- Animated **play/pause/scrub** with accurate time axis using existing recorded values; NO synthesized interpolated measurements. Animated progressive reveal may display only samples that were actually recorded.
- Clear "Baseline" vs "TabPFN" model result cards; show both, even when TabPFN loses.
- Highlight a **wrong prediction** deliberately to prove honesty and add narrative depth.
- Better loading/error states, keyboard accessibility, responsive width, disclaimer, and attribution.
- Add "Copy report" or a downloadable HTML/JSON investigation dossier **only after** core is stable.

**Pass:** in 45–75 seconds a judge can select cycle → replay waveform → click Diagnose → click Investigate → click Reveal → open Evaluation, with no blank screen or fictitious values. `npm run build` succeeds.

### M5. Gemma investigation (Oct 31, after P0 works)

**Files:** `backend/app/services/investigator.py`, tests, optional prompt templates.

1. Install Ollama and pull `gemma3:1b` (or another Gemma variant that runs on available hardware).
2. Feed Gemma a **structured evidence object**: real sensor statistics, exact prediction, actual model name, uncertainty note and zero ground-truth label until reveal.
3. Make Gemma state what was measured vs what was inferred. Validate numerical claims against structured fields; reject/hide unsupported sensor numbers or speculative maintenance recommendations.
4. Measure one real response time and save a screenshot showing model source `ollama:gemma3:1b`.
5. Fallback behavior is valid for basic user journey, but **does not qualify as proof of Gemma integration**. Never label a deterministic fallback as a Gemma result.

**Pass:** a real Ollama/Gemma response is shown at least once, with source label and verified structured evidence, OR the optional partner-category claim is removed.

### M6. Publish, demonstrate, submit (Oct 31 — highest judging leverage)

1. Host lightweight frontend + archive API on Render if feasible. Do **not** assume a CPU-only service can serve live TabPFN or Gemma. It can serve **genuinely saved predictions**, correctly labeled as precomputed offline results.
2. IMPORTANT: `backend/data/processed/*` and `backend/artifacts/*` are gitignored. A hosted app will otherwise return **503**. Build a small, licensed, reproducible **demo artifact bundle** for selected held-out cycles, or make an automated deploy/build step generate it. Ensure backend paths match actual deployed files. Never upload TabPFN weights or credentials.
3. Save screenshots of correct **and** incorrect model predictions; compare baseline and TabPFN with actual confusion matrices.
4. Record a short real demo (no fabricated outcomes) and include captions.
5. Write a **high-quality English DEV post** with: hook, problem, why open models, architecture, dataset provenance, evaluation, 3-step demo, honest failures/limitations, links, model licenses, credits, prompt/theme interpretation, selected eligible prize categories.
6. Use official submission template and verify the published entry before the internal target of **Oct 31 8:00 PM IST**.

**Pass:** valid public post, valid GitHub repo, reproducible README, verifiable screenshot/video + a real result table, working link if claiming Render category.

---

## 6. Suggested timetable (IST)

| When | P0 deliverable | Optional after P0 |
|---|---|---|
| Oct 29 evening | confirm submission access; new GitHub repo; baseline from UCI; backend tests | review UI |
| Oct 30 morning | Colab TabPFN run; exported prediction artifacts | class-balance analysis |
| Oct 30 afternoon/evening | backend ↔ frontend end-to-end walkthrough; fix issues | replay polish |
| Oct 31 morning | UI reliability, one genuine Gemma call if possible | robustness split |
| Oct 31 afternoon | Render if practical; demo recording; draft detailed English post | extras only if stable |
| Oct 31 before 20:00 IST | submit and verify all links, tags, categories | no feature creep |

**Fallback hierarchy:** If GPU or TabPFN access fails, deliver reproducible Random Forest + legitimate open-source AI where available; never fabricate TabPFN results. If deployment fails, a local demo video + clear reproducibility steps is preferable to broken public links. If Gemma cannot run, keep an explicit deterministic fallback but do not claim Best Use of Gemma.

---

## 7. Definition of done / judging quality gate

**Functional:**
- [ ] Selecting archived cycle returns real data; chart labels reflect the correct sensor and units.
- [ ] Prediction is from actual model output; label reveal happens only after user action.
- [ ] Actual held-out metrics saved with version, split seed and class distribution.
- [ ] No class target, other target or stability leakage in X; tests check this.
- [ ] At least 1 correct and 1 incorrect case documented **if the actual model yields errors**. If perfect on current split, disclose and use robust secondary test instead of inventing a mistake.
- [ ] UI builds, backend tests pass, sensible failures when artifacts are unavailable.

**Competition:**
- [ ] Challenge form can accept the submission (check `Live Ended` discrepancy).
- [ ] Repo first created during the eligible window; first commit dated in challenge window.
- [ ] Final English article includes reproducible source links, real numbers and theme story.
- [ ] Actual model/hosting integration for every claimed partner category.
- [ ] README accurately lists what's live and what is precomputed.
- [ ] Submit before deadline; confirm published post renders.

---

## 8. Codex + ChatGPT + Colab collaboration protocol

**Codex on Windows:** reads `AGENTS.md`, implements one milestone at a time, runs `pytest` and `npm run build`, reports exact changed filenames/commands/output/errors. Never claims a run succeeded without executing it.

**ChatGPT here:** explains design choices, reviews algorithms and exceptions, makes additional files/notebooks when requested, drafts and reviews the English article, checks technical claims. Can create downloadable artifacts here, but **cannot directly run commands on the user's Windows laptop or their private Colab runtime from this chat**.

**Colab:** executes Python model experiments with runtime GPU if available, saves actual measured artifacts. Not a permanent API server; preserve outputs via download/Drive.

**Human builder:** owns DEV sign-in and submission, Github push, model license acceptance, Colab runtime and Render account/deployment. Secrets stay in private env variables.

### Codex execution contract

1. Read `AGENTS.md` + this document + `docs/TASK_CHECKLIST.md`.
2. Follow tasks in order; do not replace existing working code with a fresh scaffold.
3. Before editing, state files that will change. After editing, report exact commands executed and actual results.
4. Stop only for missing credentials/license approval or genuinely blocked external access; otherwise keep moving to next P0 task after tests pass.
5. Make small Git commits after verified milestones, with clear messages and dates.
6. Never write fake labels, phantom data, hardcoded metrics or unverified model scores.

---

## 9. Exact startup commands for Windows

From extracted `echo-17` root:

**Terminal A (backend):**

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

**Terminal B (frontend):**

```powershell
cd frontend
npm install
npm run build
npm run dev
```

Visit `http://127.0.0.1:8000/docs` and `http://localhost:5173`.

**TabPFN notebook:** Upload `echo-17-starter.zip` to Colab when notebook asks, allow extraction to `/content/echo-17`, then run `notebooks/tabpfn_colab.ipynb` in a GPU runtime. This notebook itself must be opened/uploaded to Colab first. Model access may require accepting the non-commercial license.

**Git (only after creating the new GitHub repository):**

```powershell
git init
git add .
git commit -m "Initial ECHO-17 forensic research prototype"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/YOUR_NEW_REPO.git
git push -u origin main
```

Replace placeholders; do not paste a made-up remote into a real terminal. Commit only code/docs—not `.venv`, data, secrets or checkpoints.

---

## 10. Evidence for the DEV story

### Suggested article title

**I Taught Open-Source AI to Listen to the Ghosts of Broken Machines**

### DEV article outline (English)

1. **Cold open / story:** a 60-second archived machine recording; the model must make a prediction before the recorded answer is revealed.
2. **Why this theme:** "ghost" is the evidence left by historical equipment, not a fictional AI spirit.
3. **Why open matters:** transparent/reproducible preprocessing, local model execution, substitutable classifiers, offline review, clear licensing limits.
4. **How it works:** UCI rig → 36 features → Random Forest & TabPFN → saved predictions → FastAPI → React → Gemma when actually enabled.
5. **Results:** exact real accuracy/macro-F1, confusion matrix, fixed split, failure cases; if blocked, explain instead of inventing numbers.
6. **Technical lessons and limitations:** random-vs-blocked split, experimental not industrial production conditions, model probabilities are not calibrated risk.
7. **Demo:** genuine video and screenshots; accurate notes about precomputed vs live computation.
8. **Reproduce it:** GitHub link, commands, licensing.
9. **Partner prize categories:** only ones actually demonstrated.
10. **Credits:** UCI dataset, model authors, libraries; commit history and AI tools assistance if appropriate.

### Judge's 60-second demo script

0–10 s: "Here's cycle #N from a real historic test rig." Show sensor selection and authentic data source.  
10–25 s: Scrub/replay waveform; choose a sensor; show real units.  
25–35 s: Run diagnosis (from held-out saved model outputs); show Random Forest vs TabPFN.  
35–45 s: Generate/retrieve evidence-constrained investigation; show source.  
45–55 s: Reveal actual condition (correct OR incorrect — whichever the example truly is).  
55–60 s: Show confusion matrix, model comparison, repo link.

---

## 11. Real source references (checked 29 Oct 2026)

- Official Week 4 rules and category definitions: https://dev.to/challenges/hacktoberfest-week4-2026-10-26
- UCI 447 experimental dataset: https://archive.ics.uci.edu/dataset/447/condition+monitoring+of+hydraulic+systems
- TabPFN official repository, Colab demo and setup: https://github.com/PriorLabs/TabPFN
- TabPFN 3.5 model card and separate license: https://huggingface.co/Prior-Labs/tabpfn_3_5

**Final philosophy:** Ship one verifiable machine investigation, polish it deeply, and write a great story. A polished honest 80% implementation can beat a 100-feature roadmap that does not run.
