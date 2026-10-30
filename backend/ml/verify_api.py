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
    args = parser.parse_args()
    predictions = pd.read_csv(ARTIFACTS / "baseline_predictions.csv").set_index("cycle_id")
    ids = predictions.reset_index().groupby("actual").first().cycle_id.astype(int).tolist()
    ids += predictions.loc[predictions.actual != predictions.predicted].index.astype(int).tolist()
    ids += predictions.loc[predictions.actual == predictions.predicted].index.astype(int).tolist()[:1]
    ids = list(dict.fromkeys(ids))
    checks = []
    session = requests.Session()

    def check(method, path, status=200):
        response = session.request(method, args.base_url.rstrip("/") + path, timeout=60)
        assert response.status_code == status, f"{method} {path}: {response.status_code} {response.text[:200]}"
        checks.append({"method": method, "path": path, "status": response.status_code})
        return response.json() if "application/json" in response.headers.get("content-type", "") else None

    health = check("GET", "/api/health")
    assert health["data_ready"] is True
    check("GET", "/api/meta")
    cycles = check("GET", "/api/cycles?limit=441")
    assert {c["id"] for c in cycles["cycles"]} == set(predictions.index)
    sources = {}
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
        report = check("POST", f"/api/investigate/{cycle_id}")
        sources[str(cycle_id)] = report["source"]
        actual = check("POST", f"/api/reveal/{cycle_id}")
        assert actual["actual"] == int(predictions.loc[cycle_id, "actual"])
    result = check("GET", "/api/evaluation")
    saved = json.loads((ARTIFACTS / "baseline_metrics.json").read_text())
    assert result["results"][0] == saved
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
                "health": health, "cycle_ids": ids, "investigator_sources": sources,
                "reference_cycle_ids": references, "checks": checks}
    output = ARTIFACTS / args.output
    if output.parent.resolve() != ARTIFACTS.resolve():
        parser.error("--output must name a file inside artifacts")
    output.write_text(json.dumps(evidence, indent=2))
    print(json.dumps({"checks_passed": len(checks), "health": health, "cycle_ids": ids,
                      "investigator_sources": sources}, indent=2))


if __name__ == "__main__":
    main()
