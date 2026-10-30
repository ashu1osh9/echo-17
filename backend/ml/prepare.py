"""Feature extraction over 2,205 real recorded cycles; also builds replay previews."""
import numpy as np
import pandas as pd
import hashlib
import json
from datetime import datetime, timezone
from .config import RAW, PROCESSED, SENSORS, ARCHIVE_URL

STAT_NAMES = ("mean", "std", "min", "max", "p05", "p95")
FEATURE_COLUMNS = tuple(f"{sensor}_{stat}" for sensor in SENSORS for stat in STAT_NAMES)
EXPECTED_CYCLES = 2205


def validate_profile(profile):
    if profile.shape != (EXPECTED_CYCLES, 5):
        raise ValueError(f"Expected profile shape (2205, 5), got {profile.shape}")
    if not np.isfinite(profile).all() or not np.equal(profile, np.floor(profile)).all():
        raise ValueError("Profile must contain finite integer labels")
    for column, allowed in enumerate(({3, 20, 100}, {73, 80, 90, 100}, {0, 1, 2},
                                      {90, 100, 115, 130}, {0, 1})):
        if not set(profile[:, column]).issubset(allowed):
            raise ValueError(f"Invalid profile labels in column {column + 1}")


def validate_sensor(sensor, values, cycles):
    expected = (cycles, SENSORS[sensor][0] * 60)
    if values.shape != expected:
        raise ValueError(f"{sensor}: expected shape {expected}, got {values.shape}")
    if not np.isfinite(values).all():
        raise ValueError(f"{sensor}: non-finite measurements")


def model_features(frame):
    """Allow only the 36 measured sensor summaries, never metadata or targets."""
    selected = frame.loc[:, list(FEATURE_COLUMNS)]
    if not np.isfinite(selected.to_numpy(dtype=float)).all():
        raise ValueError("Non-finite sensor features")
    return selected


def stats(arr):
    """Input shape: (cycles, samples). Returns (cycles, 6)."""
    return np.column_stack([
        arr.mean(axis=1), arr.std(axis=1), arr.min(axis=1), arr.max(axis=1),
        np.percentile(arr, 5, axis=1), np.percentile(arr, 95, axis=1)
    ]).astype(np.float32)


def main():
    PROCESSED.mkdir(parents=True, exist_ok=True)
    file = RAW / "profile.txt"
    if not file.exists():
        raise FileNotFoundError("Dataset missing: run python -m ml.download_data first")
    profile = np.loadtxt(file, delimiter="\t")
    validate_profile(profile)
    profile = profile.astype(np.int32)
    n = len(profile)
    feature_columns = {"cycle_id": np.arange(1, n + 1, dtype=np.int32)}
    previews = {}
    provenance = {"source": ARCHIVE_URL, "timestamp_utc": datetime.now(timezone.utc).isoformat(),
                  "cycles": n, "feature_columns": list(FEATURE_COLUMNS), "sensors": {}}
    provenance["profile_sha256"] = hashlib.sha256(file.read_bytes()).hexdigest()
    for sensor in SENSORS:
        print(f"Processing {sensor}...")
        rawfile = RAW / f"{sensor}.txt"
        if not rawfile.exists():
            raise FileNotFoundError(f"Missing {rawfile}; run downloader")
        values = np.loadtxt(rawfile, dtype=np.float32, delimiter="\t")
        validate_sensor(sensor, values, n)
        with rawfile.open("rb") as source:
            digest = hashlib.file_digest(source, "sha256").hexdigest()
        provenance["sensors"][sensor] = {"shape": list(values.shape), "sha256": digest}
        z = stats(values)
        for index, name in enumerate(STAT_NAMES):
            feature_columns[f"{sensor}_{name}"] = z[:, index]
        # Only display samples recorded in the UCI sensor file, never interpolate new values.
        sample_indices = np.linspace(0, values.shape[1] - 1, min(240, values.shape[1]), dtype=int)
        previews[sensor] = values[:, sample_indices].copy()
        previews[f"{sensor}_time"] = (sample_indices / SENSORS[sensor][0]).astype(np.float32)
        del values
    feature_columns["cooler_condition"] = profile[:, 0]
    feature_columns["stable"] = profile[:, 4]
    pd.DataFrame(feature_columns).to_csv(PROCESSED / "features.csv", index=False)
    np.savez_compressed(PROCESSED / "signals.npz", **previews)
    (PROCESSED / "preparation_metadata.json").write_text(json.dumps(provenance, indent=2))
    print(f"Saved features and measured replay signals for {n} cycles.")


if __name__ == "__main__":
    main()
