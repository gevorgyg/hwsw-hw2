"""Line-oriented command interpreter shared by both implementations.

The interpreter owns only the text protocol; it knows nothing about ants
and nothing about which architecture sits behind it. The caller hands it
a table mapping command names to callables. Each callable receives a dict
of string arguments and returns a JSON-serializable dict.

Protocol, one command per line on stdin:

    dispatch_foraging_party source=oak count=4

Output, one line per command on stdout:

    ok dispatch_foraging_party {"expedition_id": 3}
    error dispatch_foraging_party no idle foragers

Blank lines and lines starting with '#' are skipped, so a workload file
can be piped straight in:

    python Traditional/main.py < workloads/day1.txt

The read loop uses input(), which blocks in the read(2) system call until
a line arrives; an idle interpreter consumes no CPU.

Error policy: ParseError and CommandError are protocol-level failures and
are reported as 'error' lines, after which the loop continues. Any other
exception escaping a handler propagates and kills the process on purpose.
The two front ends react differently to that, and the difference is part
of the architectural comparison: in the traditional build the handler runs
in the server process, so one buggy operation brings the whole colony down
with its in-memory state; in the FaaS build the handler runs in a spawned
function process, so the gateway survives and reports the failure.
"""

import json
import sys

EXIT_COMMANDS = ("exit", "quit")


class ParseError(Exception):
    """The line does not follow the command protocol."""


class CommandError(Exception):
    """The command is well formed but cannot be honored (domain error)."""


def parse_line(line):
    """Split 'name key=value key=value' into (name, args dict)."""
    parts = line.split()
    name = parts[0]
    args = {}
    for token in parts[1:]:
        if "=" not in token:
            raise ParseError(f"expected key=value, got {token!r}")
        key, _, value = token.partition("=")
        if not key or not value:
            raise ParseError(f"empty key or value in {token!r}")
        args[key] = value
    return name, args


class Interpreter:
    def __init__(self, commands, out=None):
        self.commands = dict(commands)
        self.out = out if out is not None else sys.stdout

    def execute(self, line):
        """Run one command line and write the result line. Returns False
        when the line asks to stop the loop, True otherwise."""
        line = line.strip()
        if not line or line.startswith("#"):
            return True
        if line in EXIT_COMMANDS:
            return False
        if line == "help":
            names = ", ".join(sorted(self.commands))
            self._emit(f"ok help {json.dumps({'commands': names})}")
            return True

        try:
            name, args = parse_line(line)
        except ParseError as err:
            self._emit(f"error - {err}")
            return True

        handler = self.commands.get(name)
        if handler is None:
            self._emit(f"error {name} unknown command")
            return True

        try:
            result = handler(args)
        except CommandError as err:
            self._emit(f"error {name} {err}")
            return True

        self._emit(f"ok {name} {json.dumps(result)}")
        return True

    def run(self):
        """Read commands until EOF or an exit command."""
        prompt = "> " if sys.stdin.isatty() else ""
        while True:
            try:
                line = input(prompt)
            except EOFError:
                break
            except KeyboardInterrupt:
                break
            if not self.execute(line):
                break

    def _emit(self, text):
        print(text, file=self.out, flush=True)
