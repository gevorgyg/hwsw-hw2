"""_wipe_brood: subscriber to colony_overrun; the raiders take the larvae."""

import json
from pathlib import Path

STATE_DIR = Path(__file__).resolve().parent.parent / "state"

larvae = json.loads((STATE_DIR / "larvae.json").read_text())
lost = len(larvae["items"])
larvae["items"] = []

tmp = STATE_DIR / "larvae.json.tmp"
tmp.write_text(json.dumps(larvae))
tmp.replace(STATE_DIR / "larvae.json")

print(json.dumps({"larvae_lost": lost}))
