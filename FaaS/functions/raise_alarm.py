"""raise_alarm: a threat attacks; more soldiers than threat repels it.

If the threat exceeds the soldier count the hive is overrun. This script
only decides and reports the outcome; the damage is applied by the
_wipe_stores and _wipe_brood subscribers reacting to the colony_overrun
event. Ants away on expedition are unaffected.
"""

import json
import sys
from pathlib import Path

STATE_DIR = Path(__file__).resolve().parent.parent / "state"

event = json.loads(sys.argv[1])
if "threat" not in event:
    print("missing argument 'threat'", file=sys.stderr)
    raise SystemExit(2)
if not str(event["threat"]).isdigit() or int(event["threat"]) < 1:
    print("'threat' must be a positive integer", file=sys.stderr)
    raise SystemExit(2)
threat = int(event["threat"])

ants = json.loads((STATE_DIR / "ants.json").read_text())
soldiers = sum(1 for a in ants["items"].values() if a["caste"] == "soldier")

if threat > soldiers:
    food_lost = json.loads((STATE_DIR / "food.json").read_text())["food"]
    larvae = json.loads((STATE_DIR / "larvae.json").read_text())
    larvae_lost = len(larvae["items"])
    with (STATE_DIR / "events.jsonl").open("a") as stream:
        stream.write(json.dumps({"type": "colony_overrun"}) + "\n")
    print(json.dumps({"outcome": "overrun", "threat": threat,
                      "soldiers": soldiers, "food_lost": food_lost,
                      "larvae_lost": larvae_lost}))
else:
    print(json.dumps({"outcome": "repelled", "threat": threat,
                      "soldiers": soldiers}))
