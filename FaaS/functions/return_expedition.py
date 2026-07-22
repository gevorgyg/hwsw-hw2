"""return_expedition: the party reports back with |foragers| + |days| food.

A party is away at least one night, so returning on the departure day is
refused.
"""

import json
import sys
from pathlib import Path

STATE_DIR = Path(__file__).resolve().parent.parent / "state"

event = json.loads(sys.argv[1])
if "id" not in event:
    print("missing argument 'id'", file=sys.stderr)
    raise SystemExit(2)
if not str(event["id"]).isdigit() or int(event["id"]) < 1:
    print("'id' must be a positive integer", file=sys.stderr)
    raise SystemExit(2)
expedition_id = int(event["id"])

expeditions = json.loads((STATE_DIR / "expeditions.json").read_text())
day = json.loads((STATE_DIR / "day.json").read_text())["day"]

expedition = expeditions["items"].get(str(expedition_id))
if expedition is None:
    print(f"no expedition with id {expedition_id}", file=sys.stderr)
    raise SystemExit(2)
if expedition["status"] != "out":
    print(f"expedition {expedition_id} already {expedition['status']}",
          file=sys.stderr)
    raise SystemExit(2)
if day <= expedition["departed_day"]:
    print(f"expedition {expedition_id} left today, "
          "it can return tomorrow at the earliest", file=sys.stderr)
    raise SystemExit(2)

food = json.loads((STATE_DIR / "food.json").read_text())
ants = json.loads((STATE_DIR / "ants.json").read_text())
days_out = day - expedition["departed_day"]
gained = len(expedition["foragers"]) + days_out
food["food"] += gained
for ant_id in expedition["foragers"]:
    ant = ants["items"].get(str(ant_id))
    if ant is not None:
        ant["status"] = "idle"
expedition["status"] = "returned"

tmp = STATE_DIR / "food.json.tmp"
tmp.write_text(json.dumps(food))
tmp.replace(STATE_DIR / "food.json")
tmp = STATE_DIR / "ants.json.tmp"
tmp.write_text(json.dumps(ants))
tmp.replace(STATE_DIR / "ants.json")
tmp = STATE_DIR / "expeditions.json.tmp"
tmp.write_text(json.dumps(expeditions))
tmp.replace(STATE_DIR / "expeditions.json")

print(json.dumps({"expedition_id": expedition_id, "days_out": days_out,
                  "food_gained": gained, "food_total": food["food"]}))
