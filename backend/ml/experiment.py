"""Validate real experiment inputs and predictions without loading model weights."""
import hashlib
import json
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix, f1_score

from .config import ROOT
from .prepare import EXPECTED_CYCLES, FEATURE_COLUMNS, model_features

CLASSES = [3, 20, 100]
INPUT_FILES = (
    "data/processed/features.csv", "data/processed/preparation_metadata.json",
    "artifacts/train_ids.csv", "artifacts/test_ids.csv",
    "artifacts/baseline_predictions.csv", "artifacts/baseline_metrics.json",
)


def sha256(path: Path) -> str:
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


@dataclass
class ExperimentInputs:
    frame: pd.DataFrame
    train_ids: list[int]
    test_ids: list[int]
    hashes: dict[str, str]

    @property
    def class_counts(self) -> dict[str, dict[str, int]]:
        return {name: {str(k): int(v) for k, v in self.frame.loc[ids, "cooler_condition"]
                       .value_counts().sort_index().items()}
                for name, ids in (("all", self.frame.index), ("train", self.train_ids),
                                  ("test", self.test_ids))}


def score_predictions(predictions: pd.DataFrame, inputs: ExperimentInputs) -> dict:
    required = ["cycle_id", "actual", "predicted", "confidence", "p_3", "p_20", "p_100"]
    if set(predictions.columns) != set(required) or not predictions.columns.is_unique:
        raise ValueError("Prediction columns must be cycle_id, actual, predicted, confidence, p_3, p_20, p_100")
    if not np.isfinite(predictions[required].to_numpy(dtype=float)).all():
        raise ValueError("Predictions contain non-finite values")
    if predictions.cycle_id.duplicated().any() or set(predictions.cycle_id) != set(inputs.test_ids):
        raise ValueError("Predictions must cover exactly the saved held-out IDs once")
    ordered = predictions.set_index("cycle_id").loc[inputs.test_ids]
    actual = inputs.frame.loc[inputs.test_ids, "cooler_condition"].to_numpy()
    if not np.array_equal(ordered.actual, actual):
        raise ValueError("Prediction actual labels differ from the measured feature table")
    if not set(ordered.predicted).issubset(CLASSES):
        raise ValueError("Predictions must use cooler labels 3, 20, 100")
    probabilities = ordered[[f"p_{label}" for label in CLASSES]].to_numpy()
    if (probabilities < 0).any() or (probabilities > 1).any() or not np.allclose(
            probabilities.sum(axis=1), 1, atol=2e-5, rtol=0):
        raise ValueError("Class probabilities must be in [0, 1] and sum to one")
    chosen = probabilities[np.arange(len(ordered)), [CLASSES.index(p) for p in ordered.predicted]]
    # RF's existing export rounds probabilities to five decimal places.
    if not np.allclose(chosen, probabilities.max(axis=1), atol=1e-5, rtol=0) or not np.allclose(
            ordered.confidence, chosen, atol=1e-5, rtol=0):
        raise ValueError("Predicted labels/confidence disagree with class probabilities")
    return {
        "accuracy": float(accuracy_score(actual, ordered.predicted)),
        "macro_f1": float(f1_score(actual, ordered.predicted, labels=CLASSES, average="macro")),
        "classes": CLASSES,
        "confusion_matrix": confusion_matrix(actual, ordered.predicted, labels=CLASSES).tolist(),
        "classification_report": classification_report(
            actual, ordered.predicted, labels=CLASSES, output_dict=True, zero_division=0),
        "wrong_cycle_ids": ordered.index[actual != ordered.predicted.to_numpy()].tolist(),
    }


def load_inputs(root: Path = ROOT) -> ExperimentInputs:
    for filename in INPUT_FILES:
        if not (root / filename).is_file():
            raise ValueError(f"Missing {filename}; export the existing real-data experiment first")
    frame = pd.read_csv(root / INPUT_FILES[0])
    if len(frame) != EXPECTED_CYCLES or frame.cycle_id.tolist() != list(range(1, EXPECTED_CYCLES + 1)):
        raise ValueError("Expected all 2205 cycles in original row order")
    model_features(frame)
    if set(frame.cooler_condition) != set(CLASSES):
        raise ValueError("Expected cooler labels 3, 20, 100")
    provenance = json.loads((root / INPUT_FILES[1]).read_text())
    if provenance["cycles"] != EXPECTED_CYCLES or provenance["feature_columns"] != list(FEATURE_COLUMNS):
        raise ValueError("Preparation metadata does not match the 36 measured predictors")
    train = pd.read_csv(root / "artifacts/train_ids.csv").cycle_id.tolist()
    test = pd.read_csv(root / "artifacts/test_ids.csv").cycle_id.tolist()
    if (len(train) != 1764 or len(test) != 441 or len(set(train + test)) != EXPECTED_CYCLES
            or set(train + test) != set(frame.cycle_id)):
        raise ValueError("Saved train/test IDs must be disjoint, unique and cover all 2205 cycles")
    baseline = json.loads((root / "artifacts/baseline_metrics.json").read_text())
    if baseline["test_ids"] != test or baseline["seed"] != 42 or baseline["feature_columns"] != list(FEATURE_COLUMNS):
        raise ValueError("Saved split/features differ from baseline run metadata")
    inputs = ExperimentInputs(frame.set_index("cycle_id"), train, test,
                              {name: sha256(root / name) for name in INPUT_FILES})
    if baseline["class_counts"] != inputs.class_counts:
        raise ValueError("Class counts differ from baseline run metadata")
    scores = score_predictions(pd.read_csv(root / "artifacts/baseline_predictions.csv"), inputs)
    for key in ("accuracy", "macro_f1", "confusion_matrix"):
        if scores[key] != baseline[key]:
            raise ValueError(f"Baseline {key} disagrees with saved predictions")
    return inputs
