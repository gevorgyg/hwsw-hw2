"""Runtime layer shared by every function: state access and event parsing.

This module is the FaaS equivalent of a database client library plus the
platform's event parsing, not business logic. Every function stays
independently invokable; they all just talk to the same state store,
where state.json stands in for the cloud database.

A function reports a domain refusal by calling fail(), which prints the
message to stderr and exits with code 2. The gateway maps that to an
'error' protocol line. Any other nonzero exit is treated as a crash.

save_state() writes to a temp file and renames it over the store, so the
rename is the commit point: a function that dies mid-run leaves the store
untouched. What this does not give us is isolation between two functions
that read the same snapshot concurrently; the report discusses that gap.
"""

import json
import sys
from pathlib import Path
from typing import NoReturn

STATE_PATH = Path(__file__).resolve().parent.parent / "state.json"
CASTES = ("worker", "forager", "soldier", "nurse")


def initial_state():
    ants = {}
    next_ant = 1
    for caste, count in (("worker", 4), ("forager", 3),
                         ("soldier", 2), ("nurse", 2)):
        for _ in range(count):
            ants[str(next_ant)] = {"caste": caste, "status": "idle"}
            next_ant += 1
    return {
        "day": 0,
        "food": 20,
        "num_chambers": 3,
        "pending_chambers": 0,
        "trails": ["oak", "bush"],
        "ants": ants,
        "larvae": [1],
        "expeditions": {},
        "next_ant": next_ant,
        "next_larva": 2,
        "next_expedition": 1,
    }


def load_state():
    return json.loads(STATE_PATH.read_text())


def save_state(state):
    tmp = STATE_PATH.with_name("state.json.tmp")
    tmp.write_text(json.dumps(state))
    tmp.replace(STATE_PATH)


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


def count_ants(state, caste):
    return sum(1 for a in state["ants"].values() if a["caste"] == caste)


def idle_ants(state, caste):
    return sorted(int(ant_id) for ant_id, a in state["ants"].items()
                  if a["caste"] == caste and a["status"] == "idle")


def available_chambers(state):
    return state["num_chambers"] - len(state["larvae"])
