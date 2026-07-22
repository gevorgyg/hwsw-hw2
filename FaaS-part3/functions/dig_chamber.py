"""dig_chamber: every idle worker digs one chamber for one food.

The crew is capped by what the stores can provision. The new chambers go
into the pending count, which nothing may move into the open total until
the day ticks; _open_chambers does that on the day_advanced event.
"""

import json
import sys
from pathlib import Path

STATE_DIR = Path(__file__).resolve().parent.parent / "state"

ants = json.loads((STATE_DIR / "ants.json").read_text())
food = json.loads((STATE_DIR / "food.json").read_text())
chambers = json.loads((STATE_DIR / "chambers.json").read_text())

idle = sum(1 for a in ants["items"].values()
           if a["caste"] == "worker" and a["status"] == "idle")
if idle == 0:
    print("no idle workers to dig", file=sys.stderr)
    raise SystemExit(2)
crew = min(idle, food["food"])
if crew == 0:
    print(f"cannot provision any digger, only {food['food']} food in stores",
          file=sys.stderr)
    raise SystemExit(2)
food["food"] -= crew
chambers["pending"] += crew

tmp = STATE_DIR / "food.json.tmp"
tmp.write_text(json.dumps(food))
tmp.replace(STATE_DIR / "food.json")
tmp = STATE_DIR / "chambers.json.tmp"
tmp.write_text(json.dumps(chambers))
tmp.replace(STATE_DIR / "chambers.json")

print(json.dumps({"chambers_started": crew, "workers_digging": crew,
                  "food_spent": crew}))
