"""hatch_ant: the oldest larva matures into an idle ant of the given caste."""

import json
import sys
from pathlib import Path

STATE_DIR = Path(__file__).resolve().parent.parent / "state"

event = json.loads(sys.argv[1])
if "caste" not in event:
    print("missing argument 'caste'", file=sys.stderr)
    raise SystemExit(2)
caste = event["caste"]
if caste not in ("worker", "forager", "soldier", "nurse"):
    print("caste must be one of worker, forager, soldier, nurse",
          file=sys.stderr)
    raise SystemExit(2)

larvae = json.loads((STATE_DIR / "larvae.json").read_text())
ants = json.loads((STATE_DIR / "ants.json").read_text())

if not larvae["items"]:
    print("no larvae to hatch", file=sys.stderr)
    raise SystemExit(2)
larva_id = min(larvae["items"])
larvae["items"].remove(larva_id)
ant_id = ants["next"]
ants["next"] += 1
ants["items"][str(ant_id)] = {"caste": caste, "status": "idle"}

tmp = STATE_DIR / "larvae.json.tmp"
tmp.write_text(json.dumps(larvae))
tmp.replace(STATE_DIR / "larvae.json")
tmp = STATE_DIR / "ants.json.tmp"
tmp.write_text(json.dumps(ants))
tmp.replace(STATE_DIR / "ants.json")

# commit first, then publish: the census subscriber will re-snapshot the day
with (STATE_DIR / "events.jsonl").open("a") as stream:
    stream.write(json.dumps({"type": "population_changed"}) + "\n")

print(json.dumps({"ant_id": ant_id, "caste": caste, "from_larva": larva_id}))
