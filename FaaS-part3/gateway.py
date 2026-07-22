import json
import subprocess
import sys
from pathlib import Path

from functions.state_store import (DEAD_LETTER_PATH, EVENTS_PATH,
                                   STATE_DIR, initial_slices, save)
from shared.interpreter import CommandError

FUNCTIONS_DIR = Path(__file__).resolve().parent / "functions"
RUNTIME_MODULES = {"state_store"}

# platform configuration, like EventBridge rules: which internal function
# runs when an event of a given type appears on the queue
SUBSCRIPTIONS = {"population_changed": ["_record_census"]}


def _invoke(script, args):
    proc = subprocess.run([sys.executable, str(script), json.dumps(args)],
                          capture_output=True, text=True)
    if proc.returncode == 0:
        try:
            return json.loads(proc.stdout)
        except json.JSONDecodeError:
            raise CommandError(
                f"function returned invalid JSON: {proc.stdout!r}")
    stderr = proc.stderr.strip()
    message = stderr.splitlines()[-1] if stderr else "no error output"
    if proc.returncode == 2:
        raise CommandError(message)
    raise CommandError(f"function crashed: {message}")


def _pump_events():
    # drain the queue until it stays empty; subscribers may emit new events
    while True:
        raw = EVENTS_PATH.read_text() if EVENTS_PATH.exists() else ""
        if not raw.strip():
            return
        EVENTS_PATH.write_text("")
        for line in raw.strip().splitlines():
            event = json.loads(line)
            for name in SUBSCRIPTIONS.get(event["type"], []):
                try:
                    _invoke(FUNCTIONS_DIR / f"{name}.py", event)
                except CommandError as err:
                    with DEAD_LETTER_PATH.open("a") as stream:
                        stream.write(json.dumps(
                            {"event": event, "error": str(err)}) + "\n")


def build_commands():
    STATE_DIR.mkdir(exist_ok=True)
    for name, data in initial_slices().items():
        save(name, data)
    EVENTS_PATH.write_text("")
    DEAD_LETTER_PATH.write_text("")
    commands = {}
    for script in sorted(FUNCTIONS_DIR.glob("*.py")):
        if script.stem in RUNTIME_MODULES or script.stem.startswith("_"):
            continue

        def run(args, script=script):
            result = _invoke(script, args)
            _pump_events()
            return result

        commands[script.stem] = run
    return commands
