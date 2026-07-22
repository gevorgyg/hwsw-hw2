"""new_day: advance the clock and report the chambers dug the day before.

The actual opening is done by the _open_chambers subscriber when the
day_advanced event reaches it.
"""

import json
from pathlib import Path

STATE_DIR = Path(__file__).resolve().parent.parent / "state"

day = json.loads((STATE_DIR / "day.json").read_text())
chambers = json.loads((STATE_DIR / "chambers.json").read_text())
day["day"] += 1
opened = chambers["pending"]

tmp = STATE_DIR / "day.json.tmp"
tmp.write_text(json.dumps(day))
tmp.replace(STATE_DIR / "day.json")

# commit first, then publish
with (STATE_DIR / "events.jsonl").open("a") as stream:
    stream.write(json.dumps({"type": "day_advanced"}) + "\n")

print(json.dumps({"day": day["day"], "chambers_opened": opened}))
