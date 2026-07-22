import json
import sys
from pathlib import Path
from typing import NoReturn

STATE_DIR = Path(__file__).resolve().parent.parent / "state"
EVENTS_PATH = STATE_DIR / "events.jsonl"
DEAD_LETTER_PATH = STATE_DIR / "dead_letter.jsonl"
CASTES = ("worker", "forager", "soldier", "nurse")


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


def slice_path(name):
    return STATE_DIR / f"{name}.json"


def load(name):
    return json.loads(slice_path(name).read_text())


def save(name, data):
    # atomic per slice; a function that writes several slices commits them
    # one rename at a time, so a crash can land between two renames
    tmp = STATE_DIR / f"{name}.json.tmp"
    tmp.write_text(json.dumps(data))
    tmp.replace(slice_path(name))


def emit(event_type):
    # published only after the slices are saved: commit first, then event
    with EVENTS_PATH.open("a") as stream:
        stream.write(json.dumps({"type": event_type}) + "\n")


def load_event():
    if len(sys.argv) != 2:
        fail("expected exactly one JSON event argument")
    try:
        event = json.loads(sys.argv[1])
    except json.JSONDecodeError:
        fail("event payload is not valid JSON")
    if not isinstance(event, dict):
        fail("event payload must be a JSON object")
    return event


def reply(result):
    print(json.dumps(result))


def fail(message) -> NoReturn:
    print(message, file=sys.stderr)
    raise SystemExit(2)


def require(event, key):
    if key not in event:
        fail(f"missing argument {key!r}")
    return event[key]


def to_int(event, key):
    value = require(event, key)
    if not str(value).isdigit() or int(value) < 1:
        fail(f"{key!r} must be a positive integer")
    return int(value)


def to_caste(event, key="caste"):
    caste = require(event, key)
    if caste not in CASTES:
        fail(f"{key} must be one of {', '.join(CASTES)}")
    return caste


def count_ants(ants, caste):
    return sum(1 for a in ants["items"].values() if a["caste"] == caste)


def idle_ants(ants, caste):
    return sorted(int(ant_id) for ant_id, a in ants["items"].items()
                  if a["caste"] == caste and a["status"] == "idle")
