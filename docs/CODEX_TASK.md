# Codex collaboration: ECHO-17

## Guardrails
- Do not modify the target labels or inject synthetic samples into the live demo.
- Respect existing dataset licenses; do not commit raw datasets, model weights or secrets.
- Preserve held-out train/test ids; never include cooler_condition/stable in input features.
- Do not claim validation success unless the exact command was run.
- Preserve public API schemas unless frontend and tests are updated together.
- Gemma output is generated text, not guaranteed technical proof; numbers must be checked against structured evidence.

## Next tasks in order
1. Run setup from README with real UCI data; debug any data parsing problems; commit small fixes.
2. Verify baseline split, class frequencies, confusion matrix, and test outputs; record actual results.
3. Run TabPFN notebook on a Colab GPU. Export `tabpfn_predictions.csv` and `tabpfn_metrics.json` into `backend/artifacts/`. Report honest comparative metrics.
4. Test React replay UI against real backend, capture actual screenshots.
5. Add chronological/block evaluation as a robust generalization check.
6. Dockerize the prediction-archive API with a build process that precomputes predictions; ensure files are available in a deployed service before starting it.
7. Create a 1-minute video of the real workflow, then draft truthful DEV.to article.

## Prompt for Codex
"Read README.md and docs/CODEX_TASK.md. Start at task 1 only. Use the existing architecture, real UCI sensor files and reproducible experiment split. Run tests and report exact failures. Never create dummy performance metrics or fake sensor signals. Do not rewrite the project from scratch."
