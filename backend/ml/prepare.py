"""Feature extraction over 2,205 real recorded cycles; also builds replay previews."""
import numpy as np
import pandas as pd
from .config import RAW, PROCESSED, SENSORS

STAT_NAMES = ("mean", "std", "min", "max", "p05", "p95")


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
    profile = np.loadtxt(file, dtype=np.int32, delimiter="\t")
    if profile.ndim != 2 or profile.shape[1] != 5:
        raise ValueError(f"Expected 5 profile columns, got {profile.shape}")
    n = len(profile)
    feature_columns = {"cycle_id": np.arange(1, n + 1, dtype=np.int32)}
    previews = {}
    for sensor in SENSORS:
        print(f"Processing {sensor}...")
        rawfile = RAW / f"{sensor}.txt"
        if not rawfile.exists():
            raise FileNotFoundError(f"Missing {rawfile}; run downloader")
        values = np.loadtxt(rawfile, dtype=np.float32, delimiter="\t")
        if values.shape[0] != n:
            raise ValueError(f"{sensor}: expected {n} cycles but found {values.shape[0]}")
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
    print(f"Saved features and measured replay signals for {n} cycles.")


if __name__ == "__main__":
    main()
