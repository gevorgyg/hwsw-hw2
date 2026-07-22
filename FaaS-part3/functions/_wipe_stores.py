"""_wipe_stores: subscriber to colony_overrun; the raiders empty the stores."""

import json
from pathlib import Path

STATE_DIR = Path(__file__).resolve().parent.parent / "state"

food = json.loads((STATE_DIR / "food.json").read_text())
lost = food["food"]
food["food"] = 0

tmp = STATE_DIR / "food.json.tmp"
tmp.write_text(json.dumps(food))
tmp.replace(STATE_DIR / "food.json")

print(json.dumps({"food_lost": lost}))
