"""scout_new_trail: an idle forager marks a route to a new food source."""

import json
import sys
from pathlib import Path

STATE_DIR = Path(__file__).resolve().parent.parent / "state"

event = json.loads(sys.argv[1])
if "source" not in event:
    print("missing argument 'source'", file=sys.stderr)
    raise SystemExit(2)
source = event["source"]

trails = json.loads((STATE_DIR / "trails.json").read_text())
ants = json.loads((STATE_DIR / "ants.json").read_text())

if source in trails:
    print(f"trail to {source!r} already known", file=sys.stderr)
    raise SystemExit(2)
idle = sorted(int(ant_id) for ant_id, a in ants["items"].items()
              if a["caste"] == "forager" and a["status"] == "idle")
if not idle:
    print("no idle forager available to scout", file=sys.stderr)
    raise SystemExit(2)
trails.append(source)

tmp = STATE_DIR / "trails.json.tmp"
tmp.write_text(json.dumps(trails))
tmp.replace(STATE_DIR / "trails.json")

print(json.dumps({"source": source, "scouted_by": idle[0]}))
