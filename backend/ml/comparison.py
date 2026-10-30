"""Honest, complete comparison on the same held-out cycles. No actual labels in API cases."""
import argparse
import json
from .config import ROOT
from .experiment import load_inputs, score_predictions
import pandas as pd


def compare_predictions(baseline, candidate, inputs):
    rf_scores, tab_scores = score_predictions(baseline, inputs), score_predictions(candidate, inputs)
    rf = baseline.set_index("cycle_id").loc[inputs.test_ids]
    tab = candidate.set_index("cycle_id").loc[inputs.test_ids]
    rf_ok = rf.predicted == rf.actual
    tab_ok = tab.predicted == tab.actual
    groups = {"both_correct": rf_ok & tab_ok, "both_wrong": ~rf_ok & ~tab_ok,
              "tabpfn_improved": ~rf_ok & tab_ok, "tabpfn_worse": rf_ok & ~tab_ok,
              "disagreements": rf.predicted != tab.predicted}
    return {"test_count": len(inputs.test_ids), "test_ids": inputs.test_ids,
            "baseline": rf_scores, "tabpfn": tab_scores,
            "accuracy_delta": tab_scores["accuracy"] - rf_scores["accuracy"],
            "macro_f1_delta": tab_scores["macro_f1"] - rf_scores["macro_f1"],
            "counts": {name: int(mask.sum()) for name, mask in groups.items()},
            "cases": {name: [{"cycle_id": int(i), "random_forest_condition": int(rf.loc[i, "predicted"]),
                              "tabpfn_condition": int(tab.loc[i, "predicted"])}
                             for i in rf.index[mask]] for name, mask in groups.items()},
            "note": "All saved held-out cases included; actual labels require the deliberate reveal action. Predictions are precomputed."}


def main():
    from .colab_bundle import read_validated_results
    parser = argparse.ArgumentParser(description=__doc__)
    parser.parse_args()
    metric, predictions = read_validated_results()
    result = compare_predictions(pd.read_csv(ROOT / "artifacts/baseline_predictions.csv"), predictions, load_inputs())
    result["tabpfn_model"] = metric["model"]
    (ROOT / "artifacts/model_comparison.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps({"tabpfn_model": metric["model"], "counts": result["counts"],
                      "accuracy_delta": result["accuracy_delta"], "macro_f1_delta": result["macro_f1_delta"]}, indent=2))


if __name__ == "__main__":
    main()
