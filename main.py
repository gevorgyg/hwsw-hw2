"""Entry point for both architectures.

    python main.py traditional workloads/demo.txt
    python main.py faas workloads/demo.txt
    python main.py traditional            # interactive, reads stdin

The workload file holds one command per line in the shared interpreter
protocol. Both approaches consume the exact same files, which keeps the
performance comparison fair.
"""

import argparse

from shared.interpreter import Interpreter


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("approach", choices=["traditional", "faas"],
                        help="which architecture serves the commands")
    parser.add_argument("workload", nargs="?",
                        help="file with one command per line; "
                             "omit to read commands from stdin")
    args = parser.parse_args()

    if args.approach == "traditional":
        from Traditional.app import build_commands
    else:
        from FaaS.gateway import build_commands

    interpreter = Interpreter(build_commands())
    if args.workload is None:
        interpreter.run()
        return
    with open(args.workload) as workload:
        for line in workload:
            if not interpreter.execute(line):
                break


if __name__ == "__main__":
    main()
