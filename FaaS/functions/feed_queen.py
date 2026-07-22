"""feed_queen: the queen eats N food and lays exactly N larvae.

All relations are 1:1, so the command is refused unless the stores hold
N food, N nurses are free of larvae, and N chambers are available.
"""

import json
import sys
from pathlib import Path

STATE_DIR = Path(__file__).resolve().parent.parent / "state"

event = json.loads(sys.argv[1])
if "amount" not in event:
    print("missing argument 'amount'", file=sys.stderr)
    raise SystemExit(2)
if not str(event["amount"]).isdigit() or int(event["amount"]) < 1:
    print("'amount' must be a positive integer", file=sys.stderr)
    raise SystemExit(2)
amount = int(event["amount"])

food = json.loads((STATE_DIR / "food.json").read_text())
ants = json.loads((STATE_DIR / "ants.json").read_text())
larvae = json.loads((STATE_DIR / "larvae.json").read_text())
chambers = json.loads((STATE_DIR / "chambers.json").read_text())

if amount > food["food"]:
    print(f"need {amount} food, only {food['food']} in stores",
          file=sys.stderr)
    raise SystemExit(2)
nurses = sum(1 for a in ants["items"].values() if a["caste"] == "nurse")
nurse_slots = nurses - len(larvae["items"])
if amount > nurse_slots:
    print(f"the queen lays one larva per food eaten, "
          f"but nurses can cover only {nurse_slots} more", file=sys.stderr)
    raise SystemExit(2)
available = chambers["total"] - len(larvae["items"])
if amount > available:
    print(f"the queen lays one larva per food eaten, "
          f"but only {available} chambers are available", file=sys.stderr)
    raise SystemExit(2)

food["food"] -= amount
for _ in range(amount):
    larvae["items"].append(larvae["next"])
    larvae["next"] += 1

tmp = STATE_DIR / "food.json.tmp"
tmp.write_text(json.dumps(food))
tmp.replace(STATE_DIR / "food.json")
tmp = STATE_DIR / "larvae.json.tmp"
tmp.write_text(json.dumps(larvae))
tmp.replace(STATE_DIR / "larvae.json")

print(json.dumps({"consumed": amount, "larvae_laid": amount,
                  "food_left": food["food"]}))
