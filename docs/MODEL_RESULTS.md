# Mission 1: observed Random Forest results

Local run: 30 Oct 2026, 00:22 IST. Saved UTC timestamp: `2026-10-29T18:52:37.520677+00:00`.

Source: Helwig, Pignanelli and Schütze (2015), [UCI 447](https://archive.ics.uci.edu/dataset/447/condition+monitoring+of+hydraulic+systems), DOI 10.24432/C5CW21, CC BY 4.0. Downloaded using the existing downloader from the official archive. The five-column `profile.txt` defines cycle labels by original row order.

The preparation run validated 2,205 rows per sensor, 6,000 samples/cycle for PS1/EPS1, 600 for FS1 and 60 for TS1/TS2/VS1. All measurements are finite. Replay previews select actual recorded samples. SHA-256 hashes and matrix shapes are saved in `backend/data/processed/preparation_metadata.json`.

Six statistics (mean, standard deviation, minimum, maximum, 5th and 95th percentiles) for each of those six channels produce 36 predictors. An explicit allowlist excludes cycle ID, all condition labels and stability. Random Forest: 250 trees, balanced subsample class weights, seed 42, CPU. Stratified 80/20 split; original train/test ID order is saved and protected against accidental replacement.

| Metric | Observed value |
|---|---:|
| Accuracy | 0.9931972789115646 |
| Macro-F1 | 0.9932124418669938 |
| Train / test cycles | 1,764 / 441 |
| Correct / incorrect | 438 / 3 |

| Cooler class | Full dataset | Train | Test |
|---|---:|---:|---:|
| 3 | 732 | 585 | 147 |
| 20 | 732 | 586 | 146 |
| 100 | 741 | 593 | 148 |

Confusion matrix: rows are recorded conditions; columns are predictions.

| Actual / predicted | 3 | 20 | 100 |
|---|---:|---:|---:|
| 3 | 146 | 0 | 1 |
| 20 | 1 | 145 | 0 |
| 100 | 1 | 0 | 147 |

All observed errors:

| Cycle | Actual | Predicted | Model probability of predicted class |
|---|---:|---:|---:|
| 2 | 3 | 100 | 0.528 |
| 735 | 20 | 3 | 0.504 |
| 1467 | 100 | 3 | 0.528 |

Cycle 5 is a verified correct case: actual 3, predicted 3, probability 0.628. HTTP checks exercised these four cycles using PS1 and TS1; pytest additionally checked all six sensors. Ghost references are actual full-cooler-efficiency training recordings. Changing held-out condition/stability labels does not change reference selection.

These are uncalibrated model probabilities, not failure risks. The random split includes correlated cycles from one test rig; it measures within-dataset interpolation. No chronological experiment, unseen-machine evaluation or remaining-useful-life prediction was performed. The three errors have probabilities close to 0.5; accuracy alone does not describe uncertainty on individual cycles.

Run environment: Python 3.11.5, NumPy 2.4.6, pandas 2.3.3, scikit-learn 1.9.1, joblib 1.6.0. Saved `baseline_metrics.json` includes seed, timestamp, versions, class counts, feature columns, test IDs, parameters, class-wise metrics and wrong cycle IDs. `baseline_predictions.csv` saves actual/predicted conditions and class probabilities. Generated files and fitted model remain gitignored.

## Offline research boundary

The TabPFN experiment and paired comparison were executed and validated locally on the same saved split. Their numerical results, per-cycle predictions, probabilities and full historical narrative are retained in ignored research artifacts and `backend/artifacts/release-private/before-rf-gate/`. No result is being replaced or retrained.

The hosted release contains RF outputs and RF-grounded Gemma reports only. No TabPFN output is included in its bundle, evaluation API, comparison API or diagnosis selector. See the release handoff and official model terms before publishing any restricted research evidence.
