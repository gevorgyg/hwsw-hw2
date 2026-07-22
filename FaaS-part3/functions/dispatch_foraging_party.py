"""dispatch_foraging_party: send N idle foragers down a known trail."""

import json
import sys
from pathlib import Path

STATE_DIR = Path(__file__).resolve().parent.parent / "state"

event = json.loads(sys.argv[1])
if "source" not in event:
    print("missing argument 'source'", file=sys.stderr)
    raise SystemExit(2)
source = event["source"]
if "count" not in event:
    print("missing argument 'count'", file=sys.stderr)
    raise SystemExit(2)
if not str(event["count"]).isdigit() or int(event["count"]) < 1:
    print("'count' must be a positive integer", file=sys.stderr)
    raise SystemExit(2)
count = int(event["count"])

trails = json.loads((STATE_DIR / "trails.json").read_text())
ants = json.loads((STATE_DIR / "ants.json").read_text())
day = json.loads((STATE_DIR / "day.json").read_text())["day"]
expeditions = json.loads((STATE_DIR / "expeditions.json").read_text())

if source not in trails:
    print(f"no known trail to {source!r}", file=sys.stderr)
    raise SystemExit(2)
idle = sorted(int(ant_id) for ant_id, a in ants["items"].items()
              if a["caste"] == "forager" and a["status"] == "idle")
if len(idle) < count:
    print(f"need {count} foragers, only {len(idle)} idle", file=sys.stderr)
    raise SystemExit(2)
party = idle[:count]
for ant_id in party:
    ants["items"][str(ant_id)]["status"] = "foraging"
expedition_id = expeditions["next"]
expeditions["next"] += 1
expeditions["items"][str(expedition_id)] = {
    "source": source,
    "foragers": party,
    "departed_day": day,
    "status": "out",
}

tmp = STATE_DIR / "ants.json.tmp"
tmp.write_text(json.dumps(ants))
tmp.replace(STATE_DIR / "ants.json")
tmp = STATE_DIR / "expeditions.json.tmp"
tmp.write_text(json.dumps(expeditions))
tmp.replace(STATE_DIR / "expeditions.json")

print(json.dumps({"expedition_id": expedition_id, "source": source,
                  "foragers": party, "departed_day": day}))
