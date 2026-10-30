"""Run explicitly selected TabPFN-3.5 on the preserved real-data RF experiment."""
import argparse
import gc
import json
import platform
import random
from datetime import datetime, timezone
from importlib.metadata import version
from pathlib import Path
from time import perf_counter

import numpy as np
import pandas as pd

from .config import ARTIFACTS
from .experiment import load_inputs, score_predictions, sha256
from .prepare import FEATURE_COLUMNS

CHECKPOINT = "tabpfn-v3.5-20260909.safetensors"
VARIANTS = {"V3_5": ("TabPFN-3.5", CHECKPOINT),
            "V3_5_FAST": ("TabPFN-3.5-Fast", "tabpfn-v3.5-fast-20260909.safetensors")}
RESULT_FILES = ("tabpfn_predictions.csv", "tabpfn_metrics.json")


def run_inference(inputs, variant, device, torch, classifier, model_version):
    """Only saved TRAIN rows enter fit; TEST labels are never passed to the estimator."""
    random.seed(42)
    np.random.seed(42)
    torch.manual_seed(42)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(42)
    clf = classifier.create_default_for_version(getattr(model_version, variant), device=device, random_state=42)
    checkpoint = Path(clf.model_path)
    if checkpoint.name != VARIANTS[variant][1]:
        raise ValueError(f"Unexpected {variant} checkpoint: {checkpoint.name}; review upstream before running")
    columns = list(FEATURE_COLUMNS)
    xtrain = inputs.frame.loc[inputs.train_ids, columns]
    xtest = inputs.frame.loc[inputs.test_ids, columns]
    timings = {}
    def timed(name, operation):
        if torch.cuda.is_available():
            torch.cuda.synchronize()
        start = perf_counter()
        result = operation()
        if torch.cuda.is_available():
            torch.cuda.synchronize()
        timings[name] = perf_counter() - start
        return result
    timed("fit_seconds", lambda: clf.fit(xtrain, inputs.frame.loc[inputs.train_ids, "cooler_condition"]))
    predicted = timed("predict_seconds", lambda: clf.predict(xtest))
    probabilities = timed("predict_proba_seconds", lambda: clf.predict_proba(xtest))
    if sorted(clf.classes_.tolist()) != [3, 20, 100]:
        raise ValueError("TabPFN returned inconsistent cooler classes")
    if device == "cuda" and not all(str(d).startswith("cuda") for d in clf.devices_):
        raise ValueError("CUDA requested but estimator did not use CUDA")
    return clf, checkpoint, predicted, probabilities, timings


def infer_with_fallback(inputs, variant, device, allow_fast, torch, classifier, model_version):
    attempts = []
    choices = [variant] + (["V3_5_FAST"] if variant == "V3_5" and allow_fast and device != "cpu" else [])
    for selected in choices:
        start = perf_counter()
        try:
            result = run_inference(inputs, selected, device, torch, classifier, model_version)
        except torch.cuda.OutOfMemoryError:
            attempts.append({"model_version": selected, "status": "cuda_out_of_memory",
                             "elapsed_seconds": perf_counter() - start})
            if selected == choices[-1]:
                raise
        else:
            attempts.append({"model_version": selected, "status": "completed",
                             "elapsed_seconds": perf_counter() - start})
            return selected, result, attempts
        # Leave the exception scope before releasing the failed estimator's GPU allocations.
        gc.collect()
        torch.cuda.empty_cache()
        print("CUDA memory exhausted; explicitly trying TabPFN-3.5-Fast on the SAME saved split.", flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check-inputs", action="store_true", help="Validate saved experiment without TabPFN or downloads")
    parser.add_argument("--device", choices=("auto", "cuda", "cpu"), default="auto")
    parser.add_argument("--model-version", choices=tuple(VARIANTS), default="V3_5")
    parser.add_argument("--allow-fast-fallback", action="store_true", help="Retry official 3.5-Fast ONLY after CUDA OOM")
    args = parser.parse_args()
    try:
        inputs = load_inputs()
        if args.check_inputs:
            print(json.dumps({"status": "inputs verified; inference not run", "train_count": len(inputs.train_ids),
                              "test_count": len(inputs.test_ids), "feature_count": len(FEATURE_COLUMNS),
                              "input_sha256": inputs.hashes}, indent=2))
            return
        if any((ARTIFACTS / name).exists() for name in RESULT_FILES):
            raise ValueError("TabPFN outputs already exist; preserve them before running a new experiment")
        try:
            import torch
            from tabpfn import TabPFNClassifier
            from tabpfn.constants import ModelVersion
        except ImportError as exc:
            raise ValueError("TabPFN/PyTorch unavailable. Use the Colab handoff in docs/TABPFN_HANDOFF.md") from exc
        if args.device == "cuda" and not torch.cuda.is_available():
            raise ValueError("CUDA requested but unavailable; select a GPU runtime or explicitly choose --device cpu")
        started = perf_counter()
        selected, result, attempts = infer_with_fallback(inputs, args.model_version, args.device,
            args.allow_fast_fallback, torch, TabPFNClassifier, ModelVersion)
        clf, checkpoint, predicted, probabilities, timings = result
        columns = list(FEATURE_COLUMNS)
        elapsed = perf_counter() - started
        predictions = pd.DataFrame({"cycle_id": inputs.test_ids,
                                    "actual": inputs.frame.loc[inputs.test_ids, "cooler_condition"].to_numpy(),
                                    "predicted": predicted,
                                    "confidence": probabilities.max(axis=1)})
        for index, label in enumerate(clf.classes_):
            predictions[f"p_{int(label)}"] = probabilities[:, index]
        metric = {
            **score_predictions(predictions, inputs), "model": VARIANTS[selected][0], "model_version": selected,
            "requested_model_version": args.model_version, "attempts": attempts,
            "fallback_reason": "cuda_out_of_memory" if selected != args.model_version else None,
            "checkpoint": checkpoint.name, "checkpoint_sha256": sha256(checkpoint),
            "seed": 42, "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            "versions": {"python": platform.python_version(), **{name: version(name) for name in
                         ("tabpfn", "torch", "numpy", "pandas", "scikit-learn")}},
            "train_count": len(inputs.train_ids), "test_count": len(inputs.test_ids),
            "train_ids": inputs.train_ids, "test_ids": inputs.test_ids,
            "class_counts": inputs.class_counts, "feature_columns": columns,
            "input_sha256": inputs.hashes,
            "dataset_sha256": inputs.hashes["data/processed/features.csv"],
            "class_mapping": {"3": "Near failure", "20": "Reduced efficiency", "100": "Full efficiency"},
            "split": "same saved stratified 80/20 IDs as Random Forest, seed=42",
            "device_requested": args.device, "devices_used": [str(device) for device in clf.devices_],
            "gpu_name": torch.cuda.get_device_name(0) if torch.cuda.is_available() else None,
            "cuda_version": torch.version.cuda, "fit_predict_seconds": elapsed, **timings,
            "timing_note": "CUDA synchronized; fit may include initial weight download/load. Total includes failed attempts if any.",
            "model_parameters": {"random_state": 42, "n_estimators": clf.n_estimators,
                                 "resolved_n_estimators": int(clf.n_estimators_)},
            "inference_mode": "precomputed from model inference",
            "uncertainty_note": "Model probabilities are uncalibrated. A random split on one rig tests within-dataset interpolation, not unseen-machine performance. A seed does not ensure identical results across hardware.",
            "model_license": "tabpfn-3-5-license-v1.0; separate non-commercial checkpoint terms",
        }
        if load_inputs().hashes != inputs.hashes:
            raise ValueError("Experiment inputs changed during inference; no outputs saved")
        predictions.sort_values("cycle_id").to_csv(ARTIFACTS / RESULT_FILES[0], index=False)
        (ARTIFACTS / RESULT_FILES[1]).write_text(json.dumps(metric, indent=2), encoding="utf-8")
        print(json.dumps({key: metric[key] for key in
                          ("model", "accuracy", "macro_f1", "train_count", "test_count", "wrong_cycle_ids", "devices_used")}, indent=2))
    except (ValueError, KeyError, FileNotFoundError) as exc:
        parser.exit(2, f"TabPFN experiment stopped: {exc}\n")


if __name__ == "__main__":
    main()
