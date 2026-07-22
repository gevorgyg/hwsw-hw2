#!/bin/bash
#
# script.sh -- run and measure the ant colony implementations.
#
# Modes:
#   ./script.sh --measure <approach> <workload>   perf stat -r 10 on
#                                                 python3 main.py <approach> <workload>
#   ./script.sh --demo                            run every approach on
#                                                 workloads/demo.txt in turn
#   ./script.sh --interactive <approach>          list the commands, then read
#                                                 them from the keyboard
#
# <approach> is one of: traditional, faas, traditional-part3, faas-part3.

set -e

ROOT="$(cd "$(dirname "$0")" && pwd)"
APPROACHES=(traditional faas traditional-part3 faas-part3)

EVENTS="cycles,instructions,task-clock,\
branch-instructions,branch-misses,\
cache-references,cache-misses,\
L1-dcache-loads,L1-dcache-load-misses,\
dTLB-loads,dTLB-load-misses,\
page-faults,context-switches"

usage() {
    echo "Usage: $0 --measure <approach> <workload> | --demo | --interactive <approach>" >&2
    exit 1
}

case "$1" in
    --measure)
        [ $# -eq 3 ] || usage
        perf stat -r 10 -e "$EVENTS" python3 "$ROOT/main.py" "$2" "$3"
        ;;
    --demo)
        [ $# -eq 1 ] || usage
        for approach in "${APPROACHES[@]}"; do
            echo "=== $approach ==="
            python3 "$ROOT/main.py" "$approach" "$ROOT/workloads/demo.txt"
        done
        ;;
    --interactive)
        [ $# -eq 2 ] || usage
        echo "Available commands:"
        echo help | python3 "$ROOT/main.py" "$2" \
            | sed -n 's/.*"commands": "\(.*\)".*/\1/p' | tr ',' '\n' | sed 's/^ */  /'
        echo
        python3 "$ROOT/main.py" "$2"
        ;;
    *)
        usage
        ;;
esac
