"""Entry point for all architectures.

    python main.py traditional workloads/demo.txt
    python main.py faas workloads/demo.txt
    python main.py traditional-part3 workloads/predict.txt
    python main.py faas-part3 workloads/predict.txt
    python main.py traditional            # interactive, reads stdin

The plain approaches are the Part 1/2 baseline. The -part3 approaches add
the partitioned state store, the event queue, and predict_population. The
workload file holds one command per line in the shared interpreter
protocol; all approaches consume the same files, which keeps the
comparisons fair.

The -part3 directories are not importable as packages (their names carry
a hyphen), so they are put on sys.path and imported by module name.
"""

import argparse
import sys
from pathlib import Path

from shared.interpreter import Interpreter

ROOT = Path(__file__).resolve().parent


def load_build_commands(approach):
    if approach == "traditional":
        from Traditional.app import build_commands
    elif approach == "faas":
        from FaaS.gateway import build_commands
    elif approach == "traditional-part3":
        sys.path.insert(0, str(ROOT / "Traditional-part3"))
        from app import build_commands
    else:
        sys.path.insert(0, str(ROOT / "FaaS-part3"))
        from gateway import build_commands
    return build_commands


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("approach",
                        choices=["traditional", "faas",
                                 "traditional-part3", "faas-part3"],
                        help="which architecture serves the commands")
    parser.add_argument("workload", nargs="?",
                        help="file with one command per line; "
                             "omit to read commands from stdin")
    args = parser.parse_args()

    interpreter = Interpreter(load_build_commands(args.approach)())
    if args.workload is None:
        interpreter.run()
        return
    with open(args.workload) as workload:
        for line in workload:
            if not interpreter.execute(line):
                break


if __name__ == "__main__":
    main()
