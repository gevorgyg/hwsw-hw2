"""predict_population days=N: forecast the head count for the next N days.

The daily growth is the average change per day across the recorded census
span (integer division, so it is a coarse trend, not real math). The
limiting factor names whichever resource runs out first at the current
size: food, free nurses, or free chambers, ties broken in that order.
"""

import json
import sys
from pathlib import Path

STATE_DIR = Path(__file__).resolve().parent.parent / "state"

event = json.loads(sys.argv[1])
if "days" not in event:
    print("missing argument 'days'", file=sys.stderr)
    raise SystemExit(2)
if not str(event["days"]).isdigit() or int(event["days"]) < 1:
    print("'days' must be a positive integer", file=sys.stderr)
    raise SystemExit(2)
days = int(event["days"])

census = json.loads((STATE_DIR / "census.json").read_text())
day = json.loads((STATE_DIR / "day.json").read_text())["day"]
food = json.loads((STATE_DIR / "food.json").read_text())["food"]
ants = json.loads((STATE_DIR / "ants.json").read_text())["items"]
larvae = json.loads((STATE_DIR / "larvae.json").read_text())["items"]
chambers = json.loads((STATE_DIR / "chambers.json").read_text())

entries = sorted((int(d), v) for d, v in census.items())
growth = 0
if len(entries) >= 2 and entries[-1][0] > entries[0][0]:
    first_day, first = entries[0]
    last_day, last = entries[-1]
    growth = (((last["ants"] + last["larvae"])
               - (first["ants"] + first["larvae"]))
              // (last_day - first_day))

current = len(ants) + len(larvae)
nurses = sum(1 for a in ants.values() if a["caste"] == "nurse")
caps = (("food", food),
        ("nurses", nurses - len(larvae)),
        ("chambers", chambers["total"] - len(larvae)))
limiting = min(caps, key=lambda item: item[1])[0]
forecast = [{"day": day + i, "population": current + growth * i}
            for i in range(1, days + 1)]

print(json.dumps({"based_on_days": len(entries), "daily_growth": growth,
                  "current_population": current, "limiting_factor": limiting,
                  "forecast": forecast}))
