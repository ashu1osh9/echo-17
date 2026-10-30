"""Transfer an allowlisted real experiment to Colab and validate returned results."""
import argparse
import hashlib
import io
import json
import math
from datetime import datetime
from pathlib import Path
from zipfile import BadZipFile, ZIP_DEFLATED, ZipFile

import pandas as pd

from .config import ROOT
from .experiment import INPUT_FILES, load_inputs, score_predictions
from .prepare import FEATURE_COLUMNS
from .train_tabpfn import CHECKPOINT, RESULT_FILES, VARIANTS

SOURCE_FILES = (
    "LICENSE", "docs/TABPFN_HANDOFF.md", "notebooks/tabpfn_colab.ipynb",
    "backend/requirements.txt", "backend/ml/__init__.py", "backend/ml/config.py",
    "backend/ml/prepare.py", "backend/ml/experiment.py", "backend/ml/train_tabpfn.py",
    "backend/ml/colab_bundle.py",
    "backend/ml/comparison.py",
)
BUNDLE_FILES = SOURCE_FILES + tuple(f"backend/{name}" for name in INPUT_FILES)
MANIFEST = "echo-17/colab_manifest.json"


def export_inputs(output: Path, root: Path = ROOT) -> dict:
    inputs = load_inputs(root)
    contents = {f"echo-17/{name}": (root.parent / name).read_bytes() for name in BUNDLE_FILES}
    manifest = {"schema_version": 1, "files": {
        name: hashlib.sha256(value).hexdigest() for name, value in contents.items()},
        "input_sha256": inputs.hashes,
        "data_credit": "Helwig, Pignanelli and Schuetze (2015), UCI 447, DOI 10.24432/C5CW21, CC BY 4.0"}
    with ZipFile(output, "x", compression=ZIP_DEFLATED) as archive:
        for name, value in contents.items():
            archive.writestr(name, value)
        archive.writestr(MANIFEST, json.dumps(manifest, indent=2))
    return verify_bundle(output)


def verify_bundle(path: Path) -> dict:
    with ZipFile(path) as archive:
        expected = {f"echo-17/{name}" for name in BUNDLE_FILES}
        if set(archive.namelist()) != expected | {MANIFEST} or len(archive.namelist()) != len(expected) + 1:
            raise ValueError("Input bundle contains unexpected, missing or duplicate files")
        manifest = json.loads(archive.read(MANIFEST))
        if manifest["schema_version"] != 1 or set(manifest["files"]) != expected:
            raise ValueError("Input manifest does not describe the allowlisted experiment")
        for name, digest in manifest["files"].items():
            if hashlib.sha256(archive.read(name)).hexdigest() != digest:
                raise ValueError(f"Input bundle checksum mismatch: {name}")
        if manifest["input_sha256"] != {
                name: manifest["files"][f"echo-17/backend/{name}"] for name in INPUT_FILES}:
            raise ValueError("Input fingerprints disagree with the bundle manifest")
    return {"status": "input bundle verified; inference not run", "files": len(expected),
            "bytes": path.stat().st_size, "path": str(path.resolve())}


def validate_results(contents: dict[str, bytes], root: Path = ROOT) -> dict:
    inputs = load_inputs(root)
    metric = json.loads(contents["tabpfn_metrics.json"])
    if not isinstance(metric, dict):
        raise ValueError("Result metadata must be a JSON object")
    variant = metric.get("model_version")
    if variant not in VARIANTS or metric.get("model") != VARIANTS[variant][0]:
        raise ValueError("Returned results are not an explicitly selected TabPFN-3.5 run")
    expected = {"input_sha256": inputs.hashes, "train_ids": inputs.train_ids, "test_ids": inputs.test_ids,
                "feature_columns": list(FEATURE_COLUMNS), "seed": 42, "class_counts": inputs.class_counts,
                "train_count": len(inputs.train_ids), "test_count": len(inputs.test_ids), "checkpoint": VARIANTS[variant][1],
                "inference_mode": "precomputed from model inference"}
    for key, value in expected.items():
        if metric.get(key) != value:
            raise ValueError(f"Returned {key} differs from the local experiment")
    versions = metric.get("versions", {})
    if not isinstance(versions, dict) or not all(isinstance(versions.get(key), str) and versions[key] for key in
               ("python", "tabpfn", "torch", "numpy", "pandas", "scikit-learn")):
        raise ValueError("Returned results lack runtime versions")
    if datetime.fromisoformat(metric["timestamp_utc"]).utcoffset() is None:
        raise ValueError("Run timestamp must include a timezone")
    digest = metric.get("checkpoint_sha256", "")
    if len(digest) != 64 or any(char not in "0123456789abcdef" for char in digest):
        raise ValueError("Returned results lack a checkpoint SHA-256")
    if not metric.get("devices_used") or not metric.get("uncertainty_note") or not metric.get("model_license"):
        raise ValueError("Returned results lack device, uncertainty or license metadata")
    if (metric.get("device_requested") != "cuda" or not metric.get("gpu_name") or not metric.get("cuda_version")
            or not all(isinstance(d, str) and d.startswith("cuda") for d in metric["devices_used"])):
        raise ValueError("This handoff requires recorded CUDA execution; CPU output is not a GPU evaluation")
    if metric.get("dataset_sha256") != inputs.hashes["data/processed/features.csv"]:
        raise ValueError("Returned dataset_sha256 differs from the local experiment")
    from .config import LABELS
    if metric.get("class_mapping") != {str(k): v for k, v in LABELS.items()}:
        raise ValueError("Returned class_mapping differs from cooler labels")
    for key in ("fit_seconds", "predict_seconds", "predict_proba_seconds", "fit_predict_seconds"):
        value = metric.get(key)
        if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or value < 0:
            raise ValueError(f"Invalid or missing runtime measurement: {key}")
    attempts = metric.get("attempts", [])
    if (not isinstance(attempts, list) or not attempts or not all(isinstance(a, dict) for a in attempts)
            or attempts[-1].get("model_version") != variant or attempts[-1].get("status") != "completed"):
        raise ValueError("Returned results lack completed model attempt metadata")
    requested = metric.get("requested_model_version")
    if requested not in VARIANTS:
        raise ValueError("Missing requested model version")
    if requested != variant and (requested != "V3_5" or variant != "V3_5_FAST"
            or metric.get("fallback_reason") != "cuda_out_of_memory"
            or attempts[0].get("status") != "cuda_out_of_memory"):
        raise ValueError("Unsupported or undocumented model fallback")
    predictions = pd.read_csv(io.BytesIO(contents["tabpfn_predictions.csv"]))
    for key, value in score_predictions(predictions, inputs).items():
        if metric.get(key) != value:
            raise ValueError(f"Returned {key} disagrees with held-out predictions")
    return metric


def read_validated_results(root: Path = ROOT):
    """All serving/export paths share the exact same provenance and score validation."""
    contents = {name: (root / "artifacts" / name).read_bytes() for name in RESULT_FILES}
    metric = validate_results(contents, root)
    return metric, pd.read_csv(io.BytesIO(contents["tabpfn_predictions.csv"]))


def export_results(output: Path, root: Path = ROOT) -> dict:
    contents = {name: (root / "artifacts" / name).read_bytes() for name in RESULT_FILES}
    metric = validate_results(contents, root)
    with ZipFile(output, "x", compression=ZIP_DEFLATED) as archive:
        for name, value in contents.items():
            archive.writestr(f"artifacts/{name}", value)
    return {"status": "actual TabPFN results exported", "accuracy": metric["accuracy"], "path": str(output.resolve())}


def result_contents(path: Path):
    with ZipFile(path) as archive:
        expected = {f"artifacts/{name}" for name in RESULT_FILES}
        if set(archive.namelist()) != expected or len(archive.namelist()) != len(expected):
            raise ValueError("Results ZIP must contain only the two TabPFN output files")
        contents = {name: archive.read(f"artifacts/{name}") for name in RESULT_FILES}
    return contents


def check_results(path: Path, root: Path = ROOT):
    metric = validate_results(result_contents(path), root)
    return {"status": "GPU artifacts validated; no files imported", "model": metric["model"],
            "accuracy": metric["accuracy"], "macro_f1": metric["macro_f1"], "test_count": metric["test_count"]}


def import_results(path: Path, root: Path = ROOT) -> dict:
    contents = result_contents(path)
    metric = validate_results(contents, root)
    # Validate everything and preserve any existing inference outputs before writing.
    for name, value in contents.items():
        target = root / "artifacts" / name
        if target.exists() and target.read_bytes() != value:
            raise ValueError(f"Existing {name} differs; refusing to overwrite prior results")
    for name, value in contents.items():
        (root / "artifacts" / name).write_bytes(value)
    from .comparison import compare_predictions
    comparison = compare_predictions(pd.read_csv(root / "artifacts/baseline_predictions.csv"),
                                     pd.read_csv(io.BytesIO(contents["tabpfn_predictions.csv"])), load_inputs(root))
    (root / "artifacts/model_comparison.json").write_text(json.dumps(comparison, indent=2), encoding="utf-8")
    return {"status": "TabPFN results validated and imported; comparison saved; API revalidates on access",
            "accuracy": metric["accuracy"], "macro_f1": metric["macro_f1"], "wrong_cycle_ids": metric["wrong_cycle_ids"]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("export", "verify", "results", "check-results", "import"))
    parser.add_argument("path", type=Path, help="ZIP path; exports refuse to overwrite an existing file")
    args = parser.parse_args()
    actions = {"export": export_inputs, "verify": verify_bundle, "results": export_results,
               "check-results": check_results, "import": import_results}
    try:
        print(json.dumps(actions[args.action](args.path), indent=2))
    except (ValueError, KeyError, TypeError, OSError, BadZipFile) as exc:
        parser.exit(2, f"Colab handoff stopped: {exc}\n")


if __name__ == "__main__":
    main()
