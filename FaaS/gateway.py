"""FaaS front end: a thin gateway in front of independent functions.

The gateway owns no business logic and no colony state. At startup it
provisions the state store (as a deployment would provision the database)
and builds its routing table by scanning functions/: every script there
is a command, so adding an operation to the system means dropping a file
next to the others; the gateway itself never changes.

Every command becomes one invocation of the matching script in a fresh
Python process, argv carrying the JSON event and stdout carrying the JSON
result. Exit code 0 is success, exit code 2 is a domain refusal, and any
other exit is a crashed function, which the gateway reports through the
protocol without dying itself. Compare the traditional build, where a
crashing handler takes down the whole colony.
"""

import json
import subprocess
import sys
from pathlib import Path

from FaaS.functions.state_store import initial_state, save_state
from shared.interpreter import CommandError

FUNCTIONS_DIR = Path(__file__).resolve().parent / "functions"
RUNTIME_MODULES = {"state_store"}


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


def build_commands():
    save_state(initial_state())
    commands = {}
    for script in sorted(FUNCTIONS_DIR.glob("*.py")):
        if script.stem in RUNTIME_MODULES:
            continue
        commands[script.stem] = (
            lambda args, script=script: _invoke(script, args))
    return commands
