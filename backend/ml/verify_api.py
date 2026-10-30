"""Verify a running API against real local artifacts; save observed HTTP evidence."""
import argparse
import json
from datetime import datetime, timezone

import pandas as pd
import requests

from .config import ARTIFACTS


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-url", default="http://127.0.0.1:8000")
    parser.add_argument("--output", default="api_verification.json", help="Evidence filename inside artifacts")
    parser.add_argument("--rf-only", action="store_true", help="Require that public mode serves no TabPFN output")
    args = parser.parse_args()
    predictions = pd.read_csv(ARTIFACTS / "baseline_predictions.csv").set_index("cycle_id")
    from .colab_bundle import read_validated_results
    from .comparison import compare_predictions
    from .experiment import load_inputs
    candidate = metric = None
    if not args.rf_only and any((ARTIFACTS / name).exists() for name in ("tabpfn_predictions.csv", "tabpfn_metrics.json")):
        metric, candidate = read_validated_results()
    candidate_by_id = candidate.set_index("cycle_id") if candidate is not None else None
    ids = predictions.reset_index().groupby("actual").first().cycle_id.astype(int).tolist()
    ids += predictions.loc[predictions.actual != predictions.predicted].index.astype(int).tolist()
    ids += predictions.loc[predictions.actual == predictions.predicted].index.astype(int).tolist()[:1]
    ids = list(dict.fromkeys(ids))
    checks = []
    session = requests.Session()

    def check(method, path, status=200):
        response = session.request(method, args.base_url.rstrip("/") + path, timeout=190 if "/investigate/" in path else 60)
        assert response.status_code == status, f"{method} {path}: {response.status_code} {response.text[:200]}"
        checks.append({"method": method, "path": path, "status": response.status_code})
        return response.json() if "application/json" in response.headers.get("content-type", "") else None

    health = check("GET", "/api/health")
    assert health["data_ready"] is True
    check("GET", "/api/ready")
    check("GET", "/api/meta")
    investigator_status = check("GET", "/api/investigator/status")
    assert investigator_status["local_only"] is True
    cycles = check("GET", "/api/cycles?limit=441")
    assert {c["id"] for c in cycles["cycles"]} == set(predictions.index)
    sources = {}
    report_modes = {}
    references = {}
    for cycle_id in ids:
        for sensor in ("PS1", "TS1"):
            signal = check("GET", f"/api/cycles/{cycle_id}/signals?sensor={sensor}")
            assert len(signal["times"]) == len(signal["values"]) > 0
            overlay = check("GET", f"/api/ghost/{cycle_id}?sensor={sensor}")
            references[str(cycle_id)] = overlay["reference_cycle_id"]
        result = check("POST", f"/api/diagnose/{cycle_id}")
        assert result["predictions"][0]["condition"] == int(predictions.loc[cycle_id, "predicted"])
        assert "actual" not in result
        assert result["ground_truth_hidden"] is True
        assert result["inference_mode"] == "precomputed from model inference"
        assert all("actual" not in item for item in result["predictions"])
        if args.rf_only:
            assert [item["model"] for item in result["predictions"]] == ["Random Forest"]
            assert result["tabpfn_status"]["status"] == "restricted"
            check("POST", f"/api/investigate/{cycle_id}?model=TabPFN-3.5", 404)
        if candidate_by_id is not None:
            assert result["tabpfn_status"]["available"] is True
            assert len(result["predictions"]) == 2
            saved_row = candidate_by_id.loc[cycle_id]
            imported = result["predictions"][1]
            assert imported["model"] == metric["model"]
            assert imported["condition"] == int(saved_row.predicted)
            assert imported["probabilities"] == {str(c): float(saved_row[f"p_{c}"]) for c in metric["classes"]}
            for selected in result["predictions"]:
                selected_report = check("POST", f"/api/investigate/{cycle_id}?model=" + requests.utils.quote(selected["model"]))
                assert "actual" not in selected_report
                from app.report_schema import ForensicReport
                assert ForensicReport.model_validate(selected_report).selected_model == selected["model"]
                if selected_report["source"].startswith("deterministic"):
                    assert selected["model"] in selected_report["narrative"]
                    assert f"cooler condition {selected['condition']}%" in selected_report["narrative"]
        report = check("POST", f"/api/investigate/{cycle_id}")
        sources[str(cycle_id)] = report["source"]
        report_modes[str(cycle_id)] = report["inference_mode"]
        if investigator_status.get("inference_mode") == "precomputed":
            assert report["inference_mode"] in ("precomputed", "non_llm")
        actual = check("POST", f"/api/reveal/{cycle_id}")
        assert actual["actual"] == int(predictions.loc[cycle_id, "actual"])
    result = check("GET", "/api/evaluation")
    saved = json.loads((ARTIFACTS / "baseline_metrics.json").read_text())
    assert result["results"][0] == saved
    if metric is not None:
        assert result["results"][1] == metric
    if args.rf_only:
        assert len(result["results"]) == 1
    comparison = check("GET", "/api/comparison")
    if comparison["available"]:
        assert candidate is not None
        assert comparison["comparison"]["test_count"] == len(predictions)
        assert comparison["comparison"] == compare_predictions(predictions.reset_index(), candidate, load_inputs())
        assert all("actual" not in row for rows in comparison["comparison"]["cases"].values() for row in rows)
    else:
        assert comparison["comparison"] is None
        assert comparison["tabpfn_status"]["status"] in ("missing", "invalid", "restricted")
        if args.rf_only:
            assert comparison["tabpfn_status"]["status"] == "restricted"
    check("POST", f"/api/investigate/{ids[0]}?model=unavailable-model", 404)
    for path in ("/docs", "/redoc", "/openapi.json"):
        check("GET", path)
    for path in ("/api/cycles/0/signals", "/api/ghost/0"):
        check("GET", path, 404)
    for path in ("/api/diagnose/0", "/api/reveal/0", "/api/investigate/0"):
        check("POST", path, 404)
    check("GET", f"/api/cycles/{ids[0]}/signals?sensor=bad", 404)
    check("GET", f"/api/ghost/{ids[0]}?sensor=bad", 404)
    check("GET", "/api/cycles?limit=442", 422)
    check("POST", "/api/diagnose/not-an-id", 422)
    evidence = {"timestamp_utc": datetime.now(timezone.utc).isoformat(), "base_url": args.base_url,
                "health": health, "cycle_ids": ids, "investigator_sources": sources, "report_inference_modes": report_modes,
                "reference_cycle_ids": references, "investigator_status": investigator_status,
                "tabpfn_status": comparison["tabpfn_status"],
                "model_comparison_counts": comparison["comparison"]["counts"] if comparison["available"] else None,
                "checks": checks}
    output = ARTIFACTS / args.output
    if output.parent.resolve() != ARTIFACTS.resolve():
        parser.error("--output must name a file inside artifacts")
    output.write_text(json.dumps(evidence, indent=2))
    print(json.dumps({"checks_passed": len(checks), "health": health, "cycle_ids": ids,
                      "investigator_sources": sources}, indent=2))


if __name__ == "__main__":
    main()
