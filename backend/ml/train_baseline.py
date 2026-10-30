import json
import platform
from datetime import datetime, timezone
from importlib.metadata import version
import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, f1_score, confusion_matrix, classification_report
from sklearn.model_selection import train_test_split
from .config import PROCESSED, ARTIFACTS
from .prepare import model_features, EXPECTED_CYCLES


def split_indices(df):
    return train_test_split(np.arange(len(df)), test_size=0.2, random_state=42,
                            stratify=df["cooler_condition"])


def main():
    ARTIFACTS.mkdir(parents=True, exist_ok=True)
    df = pd.read_csv(PROCESSED / "features.csv")
    cols = list(model_features(df).columns)
    if len(df) != EXPECTED_CYCLES or df["cycle_id"].tolist() != list(range(1, EXPECTED_CYCLES + 1)):
        raise ValueError("Expected all 2205 cycles in original row order")
    if set(df["cooler_condition"]) != {3, 20, 100}:
        raise ValueError("Expected cooler labels 3, 20, 100")
    tr, te = split_indices(df)
    for filename, indices in (("train_ids.csv", tr), ("test_ids.csv", te)):
        path = ARTIFACTS / filename
        if path.exists() and pd.read_csv(path)["cycle_id"].tolist() != df.iloc[indices]["cycle_id"].tolist():
            raise ValueError(f"Saved {filename} differs; refusing to overwrite the shared split")
    xtr, xte = df.iloc[tr][cols], df.iloc[te][cols]
    ytr, yte = df.iloc[tr]["cooler_condition"], df.iloc[te]["cooler_condition"]
    clf = RandomForestClassifier(n_estimators=250, random_state=42, n_jobs=-1, class_weight="balanced_subsample")
    clf.fit(xtr, ytr)
    prob = clf.predict_proba(xte)
    pred = clf.classes_[prob.argmax(axis=1)]
    labels = sorted(df["cooler_condition"].unique().tolist())
    metrics = {
        "model": "Random Forest (CPU)", "accuracy": float(accuracy_score(yte, pred)),
        "macro_f1": float(f1_score(yte, pred, average="macro")),
        "classes": labels, "confusion_matrix": confusion_matrix(yte, pred, labels=labels).tolist(),
        "classification_report": classification_report(yte, pred, labels=labels, output_dict=True, zero_division=0),
        "train_count": len(tr), "test_count": len(te), "split": "stratified 80/20 random, seed=42",
        "seed": 42, "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "versions": {"python": platform.python_version(), **{p: version(p) for p in
                     ("numpy", "pandas", "scikit-learn", "joblib")}},
        "feature_columns": cols, "test_ids": df.iloc[te]["cycle_id"].tolist(),
        "class_counts": {name: {str(k): int(v) for k, v in values.value_counts().sort_index().items()}
                         for name, values in (("all", df["cooler_condition"]), ("train", ytr), ("test", yte))},
        "model_parameters": clf.get_params(),
        "wrong_cycle_ids": df.iloc[te].loc[yte.to_numpy() != pred, "cycle_id"].tolist(),
        "uncertainty_note": "Model probabilities are uncalibrated. A random split on one rig tests within-dataset interpolation, not unseen-machine performance.",
    }
    pd.DataFrame({"cycle_id": df.iloc[tr]["cycle_id"]}).to_csv(ARTIFACTS / "train_ids.csv", index=False)
    pd.DataFrame({"cycle_id": df.iloc[te]["cycle_id"]}).to_csv(ARTIFACTS / "test_ids.csv", index=False)
    out = pd.DataFrame({"cycle_id": df.iloc[te]["cycle_id"].to_numpy(), "actual": yte.to_numpy(),
                        "predicted": pred, "confidence": prob.max(axis=1).round(5)})
    for i, key in enumerate(clf.classes_):
        out[f"p_{key}"] = prob[:, i].round(5)
    out.sort_values("cycle_id").to_csv(ARTIFACTS / "baseline_predictions.csv", index=False)
    (ARTIFACTS / "baseline_metrics.json").write_text(json.dumps(metrics, indent=2))
    joblib.dump({"model": clf, "columns": cols}, ARTIFACTS / "baseline_model.joblib")
    print(json.dumps({k: v for k, v in metrics.items() if k in {"accuracy", "macro_f1", "train_count", "test_count"}}, indent=2))


if __name__ == "__main__":
    main()
