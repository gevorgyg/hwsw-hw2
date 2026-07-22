"""FaaS front end: a thin gateway in front of independent functions.

The gateway owns no business logic and no colony state. At startup it
provisions the state store (as a deployment would provision the database)
and builds its routing table by scanning functions/: every script there
is a command, so adding an operation to the system means dropping a file
next to the others; the gateway itself never changes. Scripts whose name
starts with an underscore are internal: they are never routed, they run
only when an event they subscribe to appears on the queue.

Every command becomes one invocation of the matching script in a fresh
Python process, argv carrying the JSON event and stdout carrying the JSON
result. Exit code 0 is success, exit code 2 is a domain refusal, and any
other exit is a crashed function, which the gateway reports through the
protocol without dying itself.

After each command the gateway drains the event queue: the SUBSCRIPTIONS
table (the platform configuration, like EventBridge rules) says which
internal function reacts to which event type.
"""

import json
import subprocess
import sys
from functools import partial
from pathlib import Path

from FaaS.functions.state_store import (EVENTS_PATH, STATE_DIR,
                                        initial_slices, save)
from shared.interpreter import CommandError

FUNCTIONS_DIR = Path(__file__).resolve().parent / "functions"

SUBSCRIPTIONS = {
    "day_advanced": ["_open_chambers"],
    "colony_overrun": ["_wipe_stores", "_wipe_brood"],
}


class FaaSGateway:
    def __init__(self, functions_dir: Path = FUNCTIONS_DIR):
        self.functions_dir = functions_dir
        STATE_DIR.mkdir(exist_ok=True)
        for name, data in initial_slices().items():
            save(name, data)
        EVENTS_PATH.write_text("")

    def invoke(self, script: Path, args: dict) -> dict:
        proc = subprocess.run([sys.executable, str(script), json.dumps(args)],
                              capture_output=True, text=True, check=False)
        if proc.returncode != 0:
            stderr = proc.stderr.strip()
            message = stderr.splitlines()[-1] if stderr else "no error output"
            if proc.returncode == 2:
                raise CommandError(message)
            raise CommandError(f"function crashed: {message}")
        try:
            return json.loads(proc.stdout)
        except json.JSONDecodeError as err:
            raise CommandError(
                f"function returned invalid JSON: {proc.stdout!r}") from err

    def pump_events(self) -> None:
        while raw := EVENTS_PATH.read_text():
            EVENTS_PATH.write_text("")
            for line in raw.splitlines():
                event = json.loads(line)
                for subscriber in SUBSCRIPTIONS.get(event["type"], []):
                    self.invoke(self.functions_dir / f"{subscriber}.py", event)

    def run_command(self, script: Path, args: dict) -> dict:
        result = self.invoke(script, args)
        self.pump_events()
        return result

    def build_commands(self) -> dict:
        return {script.stem: partial(self.run_command, script)
                for script in sorted(self.functions_dir.glob("*.py"))
                if not script.stem.startswith("_")
                and script.stem != "state_store"}


def build_commands():
    return FaaSGateway().build_commands()
