"""Local serving-only memory smoke check. No live model inference or synthetic data."""
import ctypes
import json
import os
import sys
import time

from fastapi.testclient import TestClient
from app.main import app


def main():
    if os.environ.get("ECHO_REPORT_MODE") != "precomputed":
        raise SystemExit("Set ECHO_REPORT_MODE=precomputed and ECHO_DATA_ROOT to the isolated installed bundle")
    started = time.perf_counter()
    checks = 0
    with TestClient(app) as client:
        for path in ("/api/health", "/api/ready", "/api/meta", "/api/cycles?limit=441", "/api/evaluation", "/api/comparison"):
            assert client.get(path).status_code == 200; checks += 1
        for cycle in (5, 735, 2, 1467):
            diagnosis = client.post(f"/api/diagnose/{cycle}")
            assert diagnosis.status_code == 200; checks += 1
            for sensor in ("PS1", "FS1", "TS1", "TS2", "VS1", "EPS1"):
                for path in (f"/api/cycles/{cycle}/signals?sensor={sensor}", f"/api/ghost/{cycle}?sensor={sensor}"):
                    assert client.get(path).status_code == 200; checks += 1
            for model in [item["model"] for item in diagnosis.json()["predictions"]]:
                report = client.post(f"/api/investigate/{cycle}", params={"model": model}).json()
                assert report["inference_mode"] == "precomputed"; checks += 1
            assert client.post(f"/api/reveal/{cycle}").status_code == 200; checks += 1
    if sys.platform == "win32":
        class Counters(ctypes.Structure):
            _fields_ = [("cb", ctypes.c_ulong), ("faults", ctypes.c_ulong), ("peak", ctypes.c_size_t),
                        ("working", ctypes.c_size_t), ("other", ctypes.c_size_t * 6)]
        counters = Counters(); counters.cb = ctypes.sizeof(counters)
        get_handle = ctypes.windll.kernel32.GetCurrentProcess; get_handle.restype = ctypes.c_void_p
        get_memory = ctypes.windll.psapi.GetProcessMemoryInfo
        get_memory.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_ulong]
        if not get_memory(get_handle(), ctypes.byref(counters), counters.cb):
            raise OSError("Could not read current-process memory counters")
        peak_mib = counters.peak / 2**20
    else:
        import resource
        peak_mib = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / (2**20 if sys.platform == "darwin" else 1024)
    print(json.dumps({"checks": checks, "peak_working_set_mib": round(peak_mib, 2), "seconds_after_import": round(time.perf_counter() - started, 3),
                      "platform": sys.platform, "note": "Local Python/TestClient measurement, not Render/Linux capacity or latency verification. No weights loaded."}, indent=2))


if __name__ == "__main__":
    main()
