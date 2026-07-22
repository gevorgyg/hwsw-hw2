"""_open_chambers: subscriber to day_advanced; opens the pending chambers."""

import json
from pathlib import Path

STATE_DIR = Path(__file__).resolve().parent.parent / "state"

chambers = json.loads((STATE_DIR / "chambers.json").read_text())
opened = chambers["pending"]
chambers["total"] += opened
chambers["pending"] = 0

tmp = STATE_DIR / "chambers.json.tmp"
tmp.write_text(json.dumps(chambers))
tmp.replace(STATE_DIR / "chambers.json")

print(json.dumps({"chambers_opened": opened}))
