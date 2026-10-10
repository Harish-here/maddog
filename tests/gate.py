#!/usr/bin/env python3
"""Check that a release's covered changes were tested. Offline, no model.

    tests/.venv/bin/python tests/gate.py --base origin/main

Passes with "no covered changes" when no changed file selects a model test.
Otherwise fails unless the version was bumped and tests/releases/<version>/
holds a passing manifest whose fingerprints still match the files in this tree.
"""
import argparse
import sys

from harness.core.cases import TESTS_DIR
from harness.core.release import check_gate


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--base", required=True, help="the ref the branch is compared with, e.g. origin/main")
    args = parser.parse_args(argv)
    try:
        fails, message = check_gate(TESTS_DIR.parent, args.base)
    except ValueError as e:
        print(f"gate: {e}", file=sys.stderr)
        return 2
    if fails:
        print(f"gate FAILED against {args.base}:")
        for line in fails:
            print(f"  - {line}")
        return 1
    print(message)
    return 0


if __name__ == "__main__":
    sys.exit(main())
