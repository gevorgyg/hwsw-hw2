"""colony_status: read-only snapshot of the whole colony state."""

import json
from pathlib import Path

STATE_DIR = Path(__file__).resolve().parent.parent / "state"

day = json.loads((STATE_DIR / "day.json").read_text())["day"]
food = json.loads((STATE_DIR / "food.json").read_text())["food"]
ants = json.loads((STATE_DIR / "ants.json").read_text())["items"]
larvae = json.loads((STATE_DIR / "larvae.json").read_text())["items"]
chambers = json.loads((STATE_DIR / "chambers.json").read_text())
trails = json.loads((STATE_DIR / "trails.json").read_text())
expeditions = json.loads((STATE_DIR / "expeditions.json").read_text())["items"]

by_caste = {caste: 0 for caste in ("worker", "forager", "soldier", "nurse")}
busy = 0
for ant in ants.values():
    by_caste[ant["caste"]] += 1
    if ant["status"] != "idle":
        busy += 1

print(json.dumps({
    "day": day,
    "food": food,
    "ants": by_caste,
    "busy_ants": busy,
    "larvae": len(larvae),
    "num_chambers": chambers["total"],
    "num_available_chambers": chambers["total"] - len(larvae),
    "pending_chambers": chambers["pending"],
    "trails": sorted(trails),
    "expeditions_out": [
        {"id": int(expedition_id), "source": e["source"],
         "days_out": day - e["departed_day"]}
        for expedition_id, e in sorted(expeditions.items(),
                                       key=lambda kv: int(kv[0]))
        if e["status"] == "out"],
}))
