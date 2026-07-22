"""requalify_ant: retrain an idle ant for another profession.

Refused for a busy ant, and refused for a nurse whose retraining would
leave more larvae than the remaining nurses can cover (one nurse per
larva).
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
ant_id = int(event["id"])
if "profession" not in event:
    print("missing argument 'profession'", file=sys.stderr)
    raise SystemExit(2)
profession = event["profession"]
if profession not in ("worker", "forager", "soldier", "nurse"):
    print("profession must be one of worker, forager, soldier, nurse",
          file=sys.stderr)
    raise SystemExit(2)

ants = json.loads((STATE_DIR / "ants.json").read_text())
larvae = json.loads((STATE_DIR / "larvae.json").read_text())

ant = ants["items"].get(str(ant_id))
if ant is None:
    print(f"no ant with id {ant_id}", file=sys.stderr)
    raise SystemExit(2)
if ant["status"] != "idle":
    print(f"ant {ant_id} is busy ({ant['status']})", file=sys.stderr)
    raise SystemExit(2)
if ant["caste"] == "nurse" and profession != "nurse":
    remaining = sum(1 for a in ants["items"].values()
                    if a["caste"] == "nurse") - 1
    if len(larvae["items"]) > remaining:
        print(f"cannot release nurse {ant_id}: {len(larvae['items'])} "
              f"larvae need care, remaining nurses cover only {remaining}",
              file=sys.stderr)
        raise SystemExit(2)
previous = ant["caste"]
ant["caste"] = profession

tmp = STATE_DIR / "ants.json.tmp"
tmp.write_text(json.dumps(ants))
tmp.replace(STATE_DIR / "ants.json")

print(json.dumps({"ant_id": ant_id, "from": previous, "to": profession}))
