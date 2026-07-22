"""_record_census: subscriber that snapshots the day's head count.

Runs after any event that can change the population, and stores the ant
and larva counts under the current day. Later calls on the same day
overwrite the entry, so the census keeps one row per day.
"""

import json
from pathlib import Path

STATE_DIR = Path(__file__).resolve().parent.parent / "state"

day = json.loads((STATE_DIR / "day.json").read_text())["day"]
ants = json.loads((STATE_DIR / "ants.json").read_text())["items"]
larvae = json.loads((STATE_DIR / "larvae.json").read_text())["items"]
census = json.loads((STATE_DIR / "census.json").read_text())

census[str(day)] = {"ants": len(ants), "larvae": len(larvae)}

tmp = STATE_DIR / "census.json.tmp"
tmp.write_text(json.dumps(census))
tmp.replace(STATE_DIR / "census.json")

print(json.dumps({"recorded_day": day}))
