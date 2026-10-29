# ECHO-17 — COPY/PASTE CODEX PROMPTS

## Prompt 1 — Main instruction (start here)

```text
You are the lead engineer for ECHO-17. First read AGENTS.md, README.md,
docs/IMPLEMENTATION_PLAN.md, docs/TASK_CHECKLIST.md, and docs/ARCHITECTURE.md.

This repo already contains a functional starter; do NOT generate a new scaffold
or rewrite existing code wholesale. Our hard deadline is October 31, 2026 at 20:00 IST; code freeze at 15:00 IST. Read docs/31_OCT_DEADLINE_SPRINT.md first.

Work on P0 tasks sequentially and verify them by actually running commands.
Start with verifying Windows environment and real UCI dataset ingestion (D01/D02),
then Random Forest baseline D03/D04. When complete, move to M01 preparation.

Never fabricate sensor recordings, prediction CSV, accuracy, confusion matrices,
API outputs, screenshots, or Gemma responses. No leaks: cycle_id, targets and
stability are not model predictors. Use saved split IDs for every model.

Before modifying code, briefly list files to change. After each milestone,
show precise terminal commands, actual outputs, failure details, and the
next checklist task. Update docs/TASK_CHECKLIST.md only after verification.
Proceed without unnecessary confirmation; pause only for login/license
approval, privileged access, or an irrecoverable external blocker.
```

## Prompt 2 — Colab/TabPFN milestone

```text
Task M01/M02: verify notebooks/tabpfn_colab.ipynb works from the exact ZIP
we provide. Ensure it extracts to /content/echo-17, produces real
baseline_predictions.csv and tabpfn_predictions.csv on the same held-out IDs,
and exports usable results. Do not claim Colab GPU results unless actually run
inside the runtime. Prepare a clear user action list for model license approval.
```

## Prompt 3 — React UX milestone

```text
Task U01/U02/U03: refine existing React UI without rewriting it. Keep real-data
only states. Build actual play/pause/scrub with recorded points, accurate timestamps,
loading/error behavior, model-comparison cards, evaluation panel, and responsive
layout. Add tests where practical. Run npm run build and report actual output.
```

## Prompt 4 — Gemma verification milestone

```text
Task G01/G02: make the report explicitly evidence-grounded. Provide a structured
sensor-evidence payload to Gemma, preserve its source/model ID, validate numerical
claims against measured fields, and clearly show deterministic fallback if unavailable.
Do not mark Best Use of Gemma as eligible until a real Gemma response is observed.
```

## Prompt 5 — Deployment and article milestone

```text
Task S01-S05: design a lightweight Render deployment using only legitimately
precomputed prediction artifacts and sampled real signals. Avoid GPU-runtime claims.
Do not let gitignored artifacts silently disappear at deploy time. Include a
reproducible build step or small duly-attributed demo bundle, run a smoke test,
and produce an English DEV submission draft with real metrics, license notes,
limitations, architecture, 60-second demo walkthrough and working links.
Never invent measurements, URLs or deployment successes.
```
