# ECHO-17 final release checklist

Hard target: **31 Oct 2026, 20:00 IST**; code freeze 15:00 IST. A checked item means observed evidence, not a submitted entry.

## Preserved verified work

- [x] Genuine UCI data: 2,205 aligned cycles, six measured channels and 36 sensor-only features.
- [x] RF fixed-split baseline executed; actual metrics and every mistake preserved in MODEL_RESULTS.md.
- [x] Existing archive, replay, TRAIN-only Ghost, diagnosis, explicit Reveal and evaluation preserved.
- [x] Genuine local Gemma evidence planning and validated RF-grounded reports.
- [x] Offline TabPFN experiment completed and validated. Original outputs and full research narrative remain in ignored local artifacts/private snapshot; no retraining or deletion.
- [x] Public RF-only bundle excludes TabPFN weights, metrics, predictions, probabilities and dependent reports; runtime also blocks those outputs.
- [x] Public article rewritten around real RF + Gemma; complete earlier comparison/article preserved privately.

## Release gate

- [ ] Owner confirms revocation/rotation of the previously exposed Prior Labs key. No credential is required for the public app.
- [ ] Owner verifies signed-in DEV submission flow; public challenge page says Live Ended.
- [x] Repository creation verified inside Oct 26-31 window; public, not a fork.
- [x] Source/history/generated-assets/screenshot audit and exact publication manifest recorded; one intentional invalid-URL test fixture, no generated secret finding.
- [x] Final backend/frontend/build/public-mode checks recorded in RUN_LOG.md: 85 backend tests, 14 frontend tests, production build, 52 RF-only HTTP checks and 9 asset checks passed.
- [x] Exact 51-file staged candidate reviewed for the local release commit. Git HEAD and the final report identify the resulting commit; no push is authorized.
- [ ] Current desktop/mobile visual QA, genuine report screenshot and 60-90 second video captured. Existing RF screenshots remain genuine historical evidence.
- [ ] Owner authorizes source push and RF-bundle publication.
- [ ] Owner authorizes Render deployment; no paid resources allowed without separate approval.
- [ ] Actual public URL, readiness, replay, reports and mobile usability verified after deployment.
- [ ] Owner reviews and authorizes DEV publishing with working links and required tags.
- [ ] Owner supplies published entry URL; actual submission verified before the deadline.

TabPFN public-use permission remains unconfirmed. It is not required for this RF-only payload; no restricted outputs will be shipped while unresolved. Full prior checklists/run evidence are preserved in `backend/artifacts/release-private/before-rf-gate/`. See RELEASE_HANDOFF.md for exact actions and PUBLICATION_MANIFEST.md for the reviewed file list.
