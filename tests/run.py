#!/usr/bin/env python3
"""Run model-driven tests.

    tests/.venv/bin/python tests/run.py skills/advisor-mode --runtime <name>
    tests/.venv/bin/python tests/run.py skills/advisor-mode --runtime <name> --case ci-flake
    tests/.venv/bin/python tests/run.py skills/advisor-mode --runtime <name> --tier mid --pressure decision
    tests/.venv/bin/python tests/run.py skills/advisor-mode --runtime <name> --tier low --case rename-add-item --case list-flags
"""
import argparse
import sys
from datetime import datetime
from pathlib import Path

from harness.core.baseline import plugin_versions, remove_baseline
from harness.core.cases import TESTS_DIR, TIERS, PRESSURES, load_cases, load_ladders
from harness.core.report import render, write_results
from harness.core.runner import MIN_RUNS, run_case
from harness.runtimes import get_adapter


def select_cases(cases, case_ids, pressure):
    """Filter cases by id list and pressure; validate ids exist."""
    if case_ids:
        unknown = [cid for cid in case_ids if cid not in {c.id for c in cases}]
        if unknown:
            raise ValueError(f"unknown case ids: {', '.join(unknown)}")
        cases = [c for c in cases if c.id in case_ids]
    if pressure:
        cases = [c for c in cases if c.pressure == pressure]
    return cases


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("target", help="folder under tests/ holding handoff.yaml, e.g. skills/advisor-mode")
    parser.add_argument("--runtime", required=True, help="a runtime listed in harness/runtimes/ladders.yaml")
    parser.add_argument("--case", action="append", help="run only cases with these ids (repeatable)")
    parser.add_argument("--tier", choices=TIERS, help="run each case at this tier only, never climbing")
    parser.add_argument("--pressure", choices=PRESSURES, help="run only cases with this pressure")
    parser.add_argument("--runs", type=int, default=MIN_RUNS)
    args = parser.parse_args(argv)

    case_file = TESTS_DIR / args.target / "handoff.yaml"
    cases = load_cases(case_file)

    try:
        cases = select_cases(cases, args.case, args.pressure)
    except ValueError as e:
        parser.error(str(e))

    if not cases:
        parser.error(f"no cases match the filters in {case_file}")

    ladders = load_ladders()
    adapter = get_adapter(args.runtime, ladders)
    plugins = plugin_versions("main")
    results = []
    try:
        for case in cases:
            print(f"running {case.id} (expect {case.expect})", flush=True)
            results.append(run_case(case, adapter, plugins, runs=args.runs,
                                   max_tier=ladders.get("max_tier", "high"),
                                   only_tier=args.tier))
    finally:
        remove_baseline(plugins)

    report = render(results, ladders, args.runtime)
    out_dir = TESTS_DIR / "results" / datetime.now().strftime("%Y-%m-%dT%H%M%S")
    write_results(out_dir, results, report)
    print(report)
    print(f"results: {out_dir}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
