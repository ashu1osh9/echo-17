# ECHO-17 — The Machine That Remembers

An evidence-first open-source AI forensic lab for historical hydraulic-machine sensor recordings. Real data only: no seeded fake predictions or invented signal recordings.

**Status: Missions 1–2 verified through automated local integration; focused browser QA complete; submission incomplete.** Real UCI data: 2,205 aligned cycles and 36 predictors. Preserved Random Forest accuracy **0.9931972789115646**, macro-F1 **0.9932124418669938**, on 441 held-out cycles (3 errors). Frontend production build, **11 frontend tests**, **12 backend tests**, **44 HTTP checks through the frontend proxy** and **9 production asset/proxy checks** passed. API predictions are **precomputed from model inference**. Archive, cycle 735 diagnosis/reveal, full replay with a training reference, evaluation and mobile/laptop layouts were inspected in Chrome. See [actual screenshots and focused QA results](docs/VISUAL_QA.md). TabPFN, actual Gemma generation and hosting remain unverified. See [observed model results](docs/MODEL_RESULTS.md) and [commands/run evidence](docs/RUN_LOG.md).

**HARD DEADLINE: complete and submit by 31 Oct 2026, 20:00 IST.** P0 end-to-end application must work by 30 Oct, 21:00 IST. The deadline sprint overrides optional later milestones.

## Get started tonight

- [Immediate Windows + Codex quick start](docs/START_HERE_29_OCT.md)

## Work from the implementation plan

- [Winning-focused build blueprint (START HERE)](docs/WINNING_BLUEPRINT_31_OCT.md)
- [31 Oct hard-deadline sprint](docs/31_OCT_DEADLINE_SPRINT.md)

- [Full implementation roadmap](docs/IMPLEMENTATION_PLAN.md)
- [Live task checklist](docs/TASK_CHECKLIST.md)
- [Codex master prompt](docs/CODEX_MASTER_PROMPT.md)
- [Coding agent guardrails](AGENTS.md)

## Architecture

UCI 447 archive → sensor-statistics features and 240-point replay previews → stratified hold-out → Random Forest (CPU) / TabPFN-3.5 (GPU recommended) → saved held-out predictions → FastAPI → React replay, evidence-only Ghost Signature overlay, reveal and evaluation. Optional Ollama/Gemma report.

## Setup: Windows PowerShell (Python 3.11/3.12 recommended)

```powershell
cd backend
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m ml.download_data
python -m ml.prepare
python -m ml.train_baseline
python -m uvicorn app.main:app --reload
```

The downloader fetches the **public UCI dataset** (~73 MB compressed; extracted files much larger) on first run. It requires Internet access. If download fails, manually obtain [UCI 447](https://archive.ics.uci.edu/dataset/447/condition+monitoring+of+hydraulic+systems), extract the `.txt` files into `backend/data/raw`, and resume with `python -m ml.prepare`.

API available at `http://127.0.0.1:8000/docs`.

This machine's original `.venv` points to a missing Python 3.12 installation. The verified environment uses Python 3.11.5 from Anaconda in `backend/.venv/mission1`. From `backend`, run `.\.venv\mission1\Scripts\python.exe -m uvicorn app.main:app --reload`. With the API running, `.\.venv\mission1\Scripts\python.exe -m ml.verify_api` checks actual HTTP results and saves `artifacts/api_verification.json`.

Frontend in a second terminal:

```powershell
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173`. The UI displays **no sample data** before ML artifacts exist.

The configured local address is `http://127.0.0.1:5173`. Routes are `#/archive`, `#/investigation/{held_out_cycle_id}` and `#/evaluation`; browser refresh preserves the route. Search all 441 held-out recordings, filter by opened/unopened status for the current session, and paginate. The laboratory supports all six prepared channels, play/pause/reset, scrubbing and 0.25×–4× replay. Only measured preview points at supplied timestamps are revealed. Switching sensors resets replay/overlay; switching cycles clears predictions, reports and revealed labels. Ghost differences are computed on aligned displayed samples and are explicitly descriptive.

For production preview and checks (Node **22.17+** for the test runner), keep the existing backend running, then in `frontend`:

```powershell
npm ci
npm run build
npm run preview
# In another terminal, with the API and preview running:
npm test
npm run check:preview
```

`npm test` requires the real Mission 1 artifacts and the API on port 8000. React component tests use real HTTP data; only chart layout is stubbed. They do not replace browser layout/accessibility inspection. `check:preview` verifies served asset hashes and same-origin API responses on port 5173. The built frontend needs an API reverse proxy; local dev/preview configure it automatically. No deployment was performed.

## Ghost Signature: real training reference overlay

The backend endpoint `GET /api/ghost/{cycle_id}?sensor=PS1` selects a **real** training cycle with full cooler efficiency and overlays its measured signal against the held-out test cycle. Reference matching uses train-split-only standardization; no held-out target labels are used. Other components may not be healthy. Similarity is descriptive, not a fault probability or a causal diagnosis.

## TabPFN-3.5 (optional, run on Colab GPU)

Either open `notebooks/tabpfn_colab.ipynb` on a Colab GPU runtime, or run the following from `backend` in an environment with TabPFN installed:

```bash
pip install tabpfn
python -m ml.train_tabpfn
```

TabPFN checkpoints download on first use and may require acknowledging the model terms. Its weights have a **separate non-commercial license**; confirm its terms before public deployment. This project does not bundle TabPFN weights or any generated commercial inference service.

## Gemma (optional, CPU works but may be slow)

Install Ollama locally and run `ollama pull gemma3:1b`. Make sure Ollama is running. The API uses `OLLAMA_URL` (default: `http://127.0.0.1:11434`) and `OLLAMA_MODEL` (default: `gemma3:1b`). A deterministic evidence summary is returned if Ollama is unavailable; the UI labels its source accurately. For a live deployment, run an available authorized inference service or disable this optional enhancement.

## What is actually evaluated?

The prediction task is **cooler condition classification** (`3`, `20`, `100`) from actual sensor recordings. The fifth profile column (stability flag) and **all targets** are excluded from model features. Train/test separation is stratified and reproducible (`random_state=42`). Current random splitting tests interpolation within this experimental dataset—not performance on unseen machines, not remaining-useful-life prediction, and not safety-critical fault determination. For a stronger paper, compare with a chronological/block split.

The archive shown in the UI contains held-out evaluation cycles, so you can reveal their recorded labels and audit model predictions. Files in `backend/artifacts/` are only generated by actual model executions.

## Data and licenses

UCI Condition Monitoring of Hydraulic Systems — Helwig, Pignanelli, Schütze (2015), DOI [10.24432/C5CW21](https://doi.org/10.24432/C5CW21), [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Raw dataset is downloaded by the user, not redistributed in this ZIP.

TabPFN code and weights have distinct licenses; see [TabPFN](https://github.com/PriorLabs/TabPFN). Check the Gemma license for use of selected model. Project code: MIT license in `LICENSE`.

## Build status

- [x] Dataset downloader / parser
- [x] Feature engineering / reproducible baseline
- [x] Model prediction exports / TabPFN script
- [x] FastAPI endpoints / no fake data
- [x] Frontend investigation workflow
- [x] Optional Gemma integration with fallback
- [x] Real dataset download and local Random Forest run (see run log)
- [x] Real recorded baseline evaluation metrics (see model results)
- [x] Frontend production build and automated real-data investigation
- [x] Actual archive dashboard/search inspection and screenshots (see manual QA document)
- [x] Focused cycle 735 browser diagnosis/reveal, complete replay/Ghost, evaluation and 390-pixel/1366×768 layout checks ([evidence](docs/VISUAL_QA.md))
- [ ] Public deployment and full DEV.to submission
