"""Optional TabPFN 3.5 inference; run on GPU Colab, export genuine held-out results."""
import json
import numpy as np
import pandas as pd
from sklearn.metrics import accuracy_score, f1_score, confusion_matrix
from .config import PROCESSED, ARTIFACTS
from .prepare import model_features


def main():
    from tabpfn import TabPFNClassifier  # Optional dependency with separately licensed weights
    df = pd.read_csv(PROCESSED / "features.csv").set_index("cycle_id")
    tr = pd.read_csv(ARTIFACTS / "train_ids.csv")["cycle_id"].to_numpy()
    te = pd.read_csv(ARTIFACTS / "test_ids.csv")["cycle_id"].to_numpy()
    cols = list(model_features(df).columns)
    clf = TabPFNClassifier()
    clf.fit(df.loc[tr, cols].to_numpy(), df.loc[tr, "cooler_condition"].to_numpy())
    proba = clf.predict_proba(df.loc[te, cols].to_numpy())
    pred = clf.classes_[np.argmax(proba, axis=1)]
    actual = df.loc[te, "cooler_condition"].to_numpy()
    labels = sorted(df["cooler_condition"].unique().tolist())
    result = pd.DataFrame({"cycle_id": te, "actual": actual, "predicted": pred, "confidence": proba.max(axis=1).round(5)})
    for i, label in enumerate(clf.classes_):
        result[f"p_{label}"] = proba[:, i].round(5)
    result.sort_values("cycle_id").to_csv(ARTIFACTS / "tabpfn_predictions.csv", index=False)
    metric = {"model": "TabPFN-3.5", "accuracy": float(accuracy_score(actual, pred)),
              "macro_f1": float(f1_score(actual, pred, average="macro")), "classes": labels,
              "confusion_matrix": confusion_matrix(actual, pred, labels=labels).tolist(),
              "train_count": len(tr), "test_count": len(te), "split": "same held-out set as baseline"}
    (ARTIFACTS / "tabpfn_metrics.json").write_text(json.dumps(metric, indent=2))
    print(json.dumps(metric, indent=2))


if __name__ == "__main__":
    main()
