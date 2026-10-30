from pathlib import Path
import os

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
DATA_ROOT = Path(os.environ.get("ECHO_DATA_ROOT", str(ROOT))).resolve()
PROCESSED = DATA_ROOT / "data" / "processed"
ARTIFACTS = DATA_ROOT / "artifacts"
SENSORS = {
    "PS1": (100, "bar"),
    "FS1": (10, "l/min"),
    "TS1": (1, "°C"),
    "TS2": (1, "°C"),
    "VS1": (1, "mm/s"),
    "EPS1": (100, "W"),
}
LABELS = {3: "Near failure", 20: "Reduced efficiency", 100: "Full efficiency"}
ARCHIVE_URL = "https://archive.ics.uci.edu/static/public/447/condition+monitoring+of+hydraulic+systems.zip"
