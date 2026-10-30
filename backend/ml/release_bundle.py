"""Allowlisted compact deployment data, preserving original experiment bytes."""
import argparse
import hashlib
import json
from pathlib import Path
from tempfile import TemporaryDirectory
from zipfile import ZIP_DEFLATED, ZipFile

import numpy as np

from .config import ROOT, SENSORS
from .experiment import INPUT_FILES, load_inputs, sha256

FILES = (*INPUT_FILES, "data/processed/signals.npz", "artifacts/gemma_reports.json")
MAX_ZIP_BYTES = 16 * 1024 * 1024
MAX_EXPANDED_BYTES = 24 * 1024 * 1024


def validate_data(root):
    inputs = load_inputs(root)
    if {p.relative_to(root).as_posix() for p in root.rglob("*") if p.is_file()} != set(FILES):
        raise ValueError("Public data must contain only RF inputs, measured signals and RF-grounded Gemma reports")
    metric = json.loads((root / "artifacts/baseline_metrics.json").read_text(encoding="utf-8"))
    with np.load(root / "data/processed/signals.npz", allow_pickle=False) as archive:
        for sensor, (rate, _) in SENSORS.items():
            count = 60 if rate == 1 else 240
            values, times = archive[sensor], archive[f"{sensor}_time"]
            if values.shape != (2205, count) or times.shape != (count,) or not np.isfinite(values).all() or not np.isfinite(times).all() or not (np.diff(times) > 0).all() or times[0] != 0 or times[-1] >= 60:
                raise ValueError("Measured replay archive has invalid shapes/timestamps")
    registry = json.loads((root / "artifacts/gemma_reports.json").read_text(encoding="utf-8"))
    required = {(cycle, "Random Forest") for cycle in (5, 735, 2, 1467)}
    if {(row["cycle_id"], row["selected_model"]) for row in registry["reports"]} != required or len(registry["reports"]) != 4:
        raise ValueError("Exactly four genuine RF-grounded Gemma reports are required")
    # Validate in an isolated process so runtime data bindings/caches cannot use the original tree.
    import os
    import subprocess
    import sys
    code = """import json
from app.services.investigator import build_evidence
from app.services.precomputed_reports import read_registry, validate_generated_report
for report in read_registry()['reports']:
 validate_generated_report(report, build_evidence(report['cycle_id'], report['selected_model']))
print('4 genuine RF reports match current measured evidence')
"""
    result = subprocess.run([sys.executable, "-c", code], cwd=ROOT, env={**os.environ, "ECHO_DATA_ROOT": str(root.resolve()), "ECHO_PUBLIC_MODEL_POLICY": "rf_only"}, capture_output=True, text=True)
    if result.returncode:
        raise ValueError("Saved Gemma reports failed isolated evidence validation")
    return {"model_policy": "rf_only", "test_count": len(inputs.test_ids), "feature_count": 36,
            "rf_accuracy": metric["accuracy"], "rf_macro_f1": metric["macro_f1"], "gemma_reports": 4}


def export_bundle(path, root=ROOT):
    path.parent.mkdir(parents=True, exist_ok=True)
    contents = {name: (root / name).read_bytes() for name in FILES}
    registry = json.loads(contents["artifacts/gemma_reports.json"])
    registry["reports"] = [row for row in registry["reports"] if row["selected_model"] == "Random Forest"]
    registry["note"] = "Genuine local Gemma reports grounded exclusively in Random Forest predictions and measured UCI evidence."
    contents["artifacts/gemma_reports.json"] = json.dumps(registry, indent=2).encode()
    with TemporaryDirectory(dir=path.parent) as temporary:
        prepared = Path(temporary)
        for name, value in contents.items():
            target = prepared / name; target.parent.mkdir(parents=True, exist_ok=True); target.write_bytes(value)
        result = validate_data(prepared)
    hashes = {name: hashlib.sha256(value).hexdigest() for name, value in contents.items()}
    manifest = {"schema_version": 2, "model_policy": "rf_only", "files": hashes, "data_credit": "Helwig, Pignanelli & Schuetze (2015), UCI 447, DOI 10.24432/C5CW21, CC BY 4.0; measured previews and derived summaries",
                "source_url": "https://doi.org/10.24432/C5CW21", "data_license_url": "https://creativecommons.org/licenses/by/4.0/",
                "changes": "Six recorded channels summarized and measured samples downsampled for replay; no synthetic waveforms.",
                "model_note": "Actual Random Forest predictions and genuine RF-grounded Gemma reports; no TabPFN outputs or any model weights. Gemma output terms remain separate from application MIT license."}
    path.parent.mkdir(parents=True, exist_ok=True)
    with ZipFile(path, "x", compression=ZIP_DEFLATED) as archive:
        for name, value in contents.items():
            archive.writestr(name, value)
        archive.writestr("manifest.json", json.dumps(manifest, indent=2))
    return {**result, "bytes": path.stat().st_size, "sha256": sha256(path), "members": len(FILES) + 1}


def unpack_bundle(path, destination, expected_sha256):
    if path.stat().st_size > MAX_ZIP_BYTES or sha256(path) != expected_sha256:
        raise ValueError("Bundle checksum or size rejected")
    with ZipFile(path) as archive:
        expected = set(FILES) | {"manifest.json"}
        if set(archive.namelist()) != expected or len(archive.namelist()) != len(expected):
            raise ValueError("Bundle must contain only the exact deployment allowlist")
        if sum(item.file_size for item in archive.infolist()) > MAX_EXPANDED_BYTES:
            raise ValueError("Expanded bundle is too large")
        manifest = json.loads(archive.read("manifest.json"))
        if manifest.get("schema_version") != 2 or manifest.get("model_policy") != "rf_only" or set(manifest.get("files", {})) != set(FILES):
            raise ValueError("Bundle manifest rejected")
        for name in FILES:
            if hashlib.sha256(archive.read(name)).hexdigest() != manifest["files"][name]:
                raise ValueError("Bundle member checksum rejected")
        if destination.exists():
            raise ValueError("Destination already exists; preserving previous data")
        # Exact names above exclude traversal, symlinks and weight/credential paths.
        with TemporaryDirectory(dir=destination.parent) as temporary:
            prepared = Path(temporary)
            for name in FILES:
                target = prepared / name
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(archive.read(name))
            result = validate_data(prepared)
            destination.mkdir()
            import shutil
            for folder in ("data", "artifacts"):
                shutil.copytree(prepared / folder, destination / folder)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=["export", "install"])
    parser.add_argument("path", type=Path)
    parser.add_argument("--destination", type=Path)
    parser.add_argument("--sha256")
    args = parser.parse_args()
    if args.action == "export":
        result = export_bundle(args.path)
    else:
        if not args.destination or not args.sha256:
            parser.error("install requires a new --destination and trusted --sha256")
        args.destination.parent.mkdir(parents=True, exist_ok=True)
        result = unpack_bundle(args.path, args.destination, args.sha256)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
