"""State layout shared by the gateway and the functions.

Each entity lives in its own JSON slice under state/. save() writes to a
temp file and renames it over the slice, so the rename is the commit
point for that one slice. A function that writes several slices commits
them one rename at a time, so a crash can land between two renames; the
report discusses that gap.
"""

import json
from pathlib import Path

STATE_DIR = Path(__file__).resolve().parent.parent / "state"
EVENTS_PATH = STATE_DIR / "events.jsonl"


def initial_slices():
    ants = {}
    next_ant = 1
    for caste, count in (("worker", 4), ("forager", 3),
                         ("soldier", 2), ("nurse", 2)):
        for _ in range(count):
            ants[str(next_ant)] = {"caste": caste, "status": "idle"}
            next_ant += 1
    return {
        "day": {"day": 0},
        "food": {"food": 20},
        "chambers": {"total": 3, "pending": 0},
        "trails": ["oak", "bush"],
        "ants": {"next": next_ant, "items": ants},
        "larvae": {"next": 2, "items": [1]},
        "expeditions": {"next": 1, "items": {}},
        "census": {},
    }


def save(name, data):
    tmp = STATE_DIR / f"{name}.json.tmp"
    tmp.write_text(json.dumps(data))
    tmp.replace(STATE_DIR / f"{name}.json")
