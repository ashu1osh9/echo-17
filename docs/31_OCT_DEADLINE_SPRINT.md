# ECHO-17 — HARD DEADLINE: 31 OCTOBER 2026 (IST)

**Non-negotiable:** Everything needed for an eligible Hacktoberfest entry must be built, tested, documented, and **submitted by 31 Oct 2026, 20:00 IST**. The evening of Oct 31 is emergency buffer only. Do **not** defer submission to Nov 1 even if an external deadline appears later.

**Current state (starter, 29 Oct):** FastAPI + React starter, data scripts, Colab notebook and tests exist; five backend tests passed in this working session. **Real UCI ingestion, model training, Colab GPU results, frontend build, hosted app and DEV submission are NOT yet verified.** No fabricated results.

## 29 October — prove the data and baseline (P0)

1. **Eligibility gate:** Sign in to the DEV challenge. Verify the entry flow is open and that a new project and GitHub repository dated Oct 26–31 are allowed. If the form says ended, investigate immediately; don't assume submission access.
2. Create new repository for `echo-17`; commit this starter (do not commit raw data, weights or credentials).
3. In `backend/`, install requirements, run `python -m pytest -q` and `python -m ml.download_data`.
4. Run `python -m ml.prepare`; verify precisely 2,205 actual cycle rows and predictor/label separation (no leakage).
5. Run `python -m ml.train_baseline`; save *observed* baseline metrics, held-out predictions and split IDs.
6. Open `http://localhost:8000/docs`; confirm `/api/health`, `/api/cycles` and one real `diagnose` work.

**29 Oct gate:** One real saved Random Forest result, working local API, and a clean new repository. If unsuccessful, fix this before any UI animations.

## 30 October — complete the end-to-end product (P0)

**Morning:**
- Run `notebooks/tabpfn_colab.ipynb` with Google Colab GPU, using the **same train/test IDs** as Random Forest. Accept model license if prompted. Save real outputs. If Colab GPU unavailable, try Kaggle; cap troubleshooting to avoid blocking the baseline demo.
- Record actual accuracy, macro-F1, confusion matrix, model version and limitations. Do not invent scores or label a failed run as successful.

**Afternoon/evening:**
- Place actual saved artifacts in `backend/artifacts/` and processed data in `backend/data/processed/`.
- `npm install && npm run build` in `frontend/`; run API + UI together.
- Make **one single investigation** work: choose a real held-out cycle → view measured waveform → diagnose → reveal actual cooler label → show evaluation.
- Play/pause/scrub is secondary to a working static waveform. Clear missing-data/error states are mandatory.

**30 Oct, 21:00 IST gate:** Demonstrable local flow, built frontend, real held-out metrics and a screen-recordable outcome. If this is missing, **STOP all optional additions**.

## 31 October — finish and submit; NO major features

| Time (IST) | Must-have outcome |
|---|---|
| **09:00–11:00** | Fix critical UX/data/API bugs; re-run tests and frontend build |
| **11:00–13:00** | If feasible, record one real Gemma response using Ollama; otherwise keep clearly labeled deterministic fallback and **do not** claim Gemma prize integration |
| **13:00–15:00** | Deployment attempt only if it will not jeopardize entry; publicly deployed demo may serve **actual precomputed** inference and must say so |
| **15:00** | **Code freeze** — no new features or framework migrations |
| **15:00–17:00** | Record 45–75 sec demo, capture real screenshots, write technical README and English DEV article with actual numbers |
| **17:00–19:00** | Check GitHub links, article tags, challenge category eligibility and submission form; publish and submit |
| **20:00** | **Hard internal deadline: verify submission successful** |

## Minimum winning-focused product (P0)

- Real UCI hydraulic sensor cycles, properly attributed.
- Reproducible Random Forest held-out classification, *actual* accuracy/macro-F1/confusion matrix and no leakage.
- Usable React/FastAPI demo, one real investigation and truth reveal.
- Real (not fabricated) screenshots, GitHub link, short demo and polished English article.
- Genuine TabPFN evaluation **if GPU/license enables it before the 30 Oct gate**. This strengthens the project significantly and is higher priority than Gemma/deployment polish.

## Cut list (do NOT let these block submission)

Additional components or classes, elaborate animations, audio, agent framework/LangGraph, authentication, database, generic chat, automated PDF reports, dashboards with dozens of graphs, elaborate monitoring, complex CI/CD. Render and Gemma are P1; only claim their prize categories when actually implemented and verified.

## Stop-loss decisions

- **UCI download blocked:** use official manual download or Colab CPU, but never use fake signals.
- **GPU/TabPFN blocked:** ship working RF application, transparently state TabPFN not completed, do not claim its prize category.
- **Gemma blocked:** show deterministic labeled fallback, do not make Gemma partner claim.
- **Hosting blocked:** ship polished video + reproducible localhost instructions, don't publish broken links or claim Render category.
- **DEV form closed:** capture the actual issue, check official announcements, and avoid claiming a successfully submitted entry without confirmation.

## Codex: first message to paste

```
Read AGENTS.md, README.md, docs/31_OCT_DEADLINE_SPRINT.md,
docs/TASK_CHECKLIST.md and docs/IMPLEMENTATION_PLAN.md.
Our HARD finish-and-submit target is October 31, 2026 at 20:00 IST.
Do not regenerate the project: this starter already has backend, frontend,
ML scripts, tests, and a Colab notebook.

Start now with P0: verify environment -> download real UCI -> prepare
real 2,205 aligned cycles -> run Random Forest baseline -> report exact
metrics -> test API. Then proceed to TabPFN on Colab and one full UI flow.
Do not prioritize extras, animations, Gemma or hosting before the P0
investigation actually works. Never fabricate sensor data or model results.
After every milestone, report exactly which files changed, commands run,
outputs, test results and remaining blockers; update TASK_CHECKLIST.md
only after verifying a task. Continue to the next P0 task automatically.
```

## Quick local commands (Windows PowerShell)

```powershell
# terminal 1, from repository root
cd backend
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m pytest -q
python -m ml.download_data
python -m ml.prepare
python -m ml.train_baseline
python -m uvicorn app.main:app --reload

# terminal 2, from repository root
cd frontend
npm install
npm run build
npm run dev
```

**Acceptance:** by Oct 31 20:00 IST, the user can show a reproducible real-data investigation and a published, submitted DEV article; all claimed partner integrations must have actual evidence.
