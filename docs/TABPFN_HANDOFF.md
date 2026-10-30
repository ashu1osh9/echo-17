# TabPFN: offline reproducible research handoff

The genuine experiment was run and its artifacts validated locally. Quantitative results and the previous complete handoff are preserved in ignored `backend/artifacts/release-private/before-rf-gate/` and the original `backend/artifacts/` files. No weights, per-cycle outputs or numerical TabPFN evaluation are part of the public release.

The [official 3.5 terms](https://huggingface.co/Prior-Labs/tabpfn_3_5/blob/main/LICENSE) apply to weights and outputs. Review the participant agreement actually accepted; do not infer public permission from precomputation or model availability. The RF + Gemma public profile does not depend on that permission.

## Reproduce only in an authorized local environment

Preserve the same real 36 sensor features and ordered TRAIN/TEST IDs used by RF. Use `notebooks/tabpfn_colab.ipynb` with `backend/artifacts/echo17_mission3_ready.zip` if present. Verify the bundle before uploading; accept applicable terms/authenticate personally without embedding credentials. The notebook explicitly uses official V3_5, CUDA, fit/predict/predict_proba and seed 42. Only recorded CUDA OOM can trigger the official Fast fallback. No silent model substitution is permitted.

From `backend`, for a new genuine returned ZIP:

```powershell
& ./.venv/mission1/Scripts/python.exe -m ml.colab_bundle check-results artifacts/echo17_results.zip
& ./.venv/mission1/Scripts/python.exe -m ml.colab_bundle import artifacts/echo17_results.zip
& ./.venv/mission1/Scripts/python.exe -m ml.comparison
```

Reuse existing outputs; do not reimport different results or retrain RF. Checks validate input hashes, ordered split, sensor-only predictors, labels/probabilities, recomputed metrics, checkpoint/version, CUDA metadata and timing. Consistency validation does not independently attest execution; use only genuine run output. Keep artifacts private/ignored until their publication permission is confirmed.

The public installer accepts only its RF-only allowlist. The previous full research bundle is preserved locally and must not be uploaded for the hosted demo. Do not publish account screenshots or tokens. Source attribution remains UCI 447, Helwig, Pignanelli and Schuetze (2015), CC BY 4.0; model terms are separate from MIT application code.
