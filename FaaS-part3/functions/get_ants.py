"""get_ants: read-only roster of every ant's id, job, and status."""

import json
from pathlib import Path

STATE_DIR = Path(__file__).resolve().parent.parent / "state"

ants = json.loads((STATE_DIR / "ants.json").read_text())

print(json.dumps({"ants": [{"id": int(ant_id), "job": a["caste"],
                            "status": a["status"]}
                           for ant_id, a in sorted(ants["items"].items(),
                                                   key=lambda kv: int(kv[0]))]}))
