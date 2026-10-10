#!/usr/bin/env python3
"""Run model-driven tests.

    tests/.venv/bin/python tests/run.py skills/advisor-mode --runtime <name>
    tests/.venv/bin/python tests/run.py skills/advisor-mode --runtime <name> --case ci-flake-pressure
    tests/.venv/bin/python tests/run.py skills/advisor-mode --runtime <name> --tier mid --pressure decision
    tests/.venv/bin/python tests/run.py skills/advisor-mode --runtime <name> --tier low --case rename-add-item --case list-flags
    tests/.venv/bin/python tests/run.py skills/advisor-mode --runtime <name> --ladder
    tests/.venv/bin/python tests/run.py skills/advisor-mode --runtime <name> --fresh-main
    tests/.venv/bin/python tests/run.py skills/advisor-mode --runtime <name> --jobs 3

Without --tier or --ladder, each case runs once, at its own expected tier
(no climbing). --ladder opts into the old climb from low up to max_tier.

A folder's handoff.yaml runs in skill mode. With --patterns, the folder's
patterns.yaml runs instead, in agent mode: each case runs that agent file as
the main session, to completion.

    tests/.venv/bin/python tests/run.py agents/executor-fast --runtime <name> --patterns

--changed [BASE] replaces the target: it runs every test file whose `covers:`
globs match a file changed since BASE (default main) or uncommitted, each in
its own mode. --dry-run lists the selection and calls no model.

    tests/.venv/bin/python tests/run.py --changed --runtime <name> --dry-run
    tests/.venv/bin/python tests/run.py --changed origin/main --runtime <name>
"""
import argparse
import shutil
import signal
import sys
import threading
from datetime import datetime
from pathlib import Path

from harness.core.changed import changed_files, discover, select_tests
from harness.core.baseline import main_sha, plugin_versions, remove_baseline, branch_with_skill
from harness.core.cases import TESTS_DIR, TIERS, PRESSURES, AgentCase, expected_tier, load_agent_cases, load_cases, load_ladders
from harness.core.fixture import SlotPool, make_workdir, remove_workdir
from harness.core.maincache import CACHE_DIRNAME, MainCache, hash_file
from harness.core.report import render, write_results
from harness.core.runner import MIN_RUNS, run_cases
from harness.core.sweep import sweep
from harness.runtimes import adapter_source_path, get_adapter


# Overridable by tests: the root for result output and cache.
# Tests monkeypatch this to a temp folder to avoid cluttering tests/results/.
RESULTS_DIR = TESTS_DIR / "results"


class Stopped(Exception):
    """Raised by the SIGTERM/SIGINT handler below so a stop signal still
    unwinds through the run's `finally` blocks -- removing the baseline
    worktree and the job slot folders -- instead of killing the process
    mid-cleanup."""


def _stop_once():
    """Builds a signal handler that raises `Stopped` on the first stop
    signal it sees and silently ignores every one after that. Without this,
    a second SIGTERM/SIGINT landing while cleanup is already unwinding --
    e.g. mid `git worktree remove` or `shutil.rmtree` -- raises `Stopped`
    again right there and can abandon that cleanup call partway through,
    leaving a slot, baseline, or skillfile folder behind. That is no longer
    rare once `--jobs > 1` cases keep running (and, if self-signalling,
    keep re-signalling) in worker threads for as long as it takes
    `run_cases`' `ThreadPoolExecutor` to join them, which is longer than the
    near-instant unwind `--jobs 1` gets."""
    stopped = False

    def handler(signum, frame):
        nonlocal stopped
        if stopped:
            return
        stopped = True
        raise Stopped(f"stopped by signal {signum}")

    return handler


def select_cases(cases, case_ids, pressure):
    """Filter cases by id list and pressure; validate ids exist."""
    if case_ids:
        unknown = [cid for cid in case_ids if cid not in {c.id for c in cases}]
        if unknown:
            raise ValueError(f"unknown case ids: {', '.join(unknown)}")
        cases = [c for c in cases if c.id in case_ids]
    if pressure:
        cases = [c for c in cases if getattr(c, "pressure", "none") == pressure]  # agent cases carry no pressure: they count as "none"
    return cases


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("target", nargs="?",
                        help="folder under tests/ holding handoff.yaml, e.g. skills/advisor-mode; not with --changed")
    parser.add_argument("--changed", nargs="?", const="main", default=None, metavar="BASE",
                        help="instead of a target, run every test whose covers: globs match a file changed "
                             "since BASE (default main) or uncommitted")
    parser.add_argument("--dry-run", action="store_true",
                        help="with --changed: print the changed files and the selected tests, then exit without calling a model")
    parser.add_argument("--runtime", required=True, help="a runtime listed in harness/runtimes/ladders.yaml")
    parser.add_argument("--case", action="append", help="run only cases with these ids (repeatable)")
    parser.add_argument("--tier", choices=TIERS, help="run each case at this tier only, never climbing")
    parser.add_argument("--ladder", action="store_true",
                        help="climb from low to max_tier, as the runner used to by default; not with --tier")
    parser.add_argument("--pressure", choices=PRESSURES, help="run only cases with this pressure")
    parser.add_argument("--runs", type=int, default=MIN_RUNS)
    parser.add_argument("--jobs", type=int, default=1,
                        help="run up to this many cases at once, each in its own slot (default 1: sequential)")
    parser.add_argument("--fresh-main", action="store_true",
                        help="ignore and overwrite any cached main run for the selected cases")
    parser.add_argument("--skill-file", type=Path, help="test this draft skill file instead of the branch's; agents and everything else come from this tree")
    parser.add_argument("--patterns", action="store_true",
                        help="run the folder's patterns.yaml in agent mode, not its handoff.yaml")
    args = parser.parse_args(argv)

    if args.changed is not None and args.target:
        parser.error("give a target or --changed, not both")
    if args.changed is None and not args.target:
        parser.error("give a target or --changed")
    if args.dry_run and args.changed is None:
        parser.error("--dry-run goes with --changed")
    if args.changed is not None and (args.case or args.skill_file or args.patterns):
        parser.error("--changed picks each file's cases and mode; it cannot be combined with --case, --skill-file or --patterns")
    if args.ladder and args.tier:
        parser.error("--ladder and --tier are mutually exclusive")
    if args.jobs < 1:
        parser.error("--jobs must be at least 1")
    if args.skill_file and not args.skill_file.exists():
        parser.error(f"skill file does not exist: {args.skill_file}")

    if args.changed is not None:
        return _run_changed(parser, args)

    for folder in sweep(TESTS_DIR.parent):
        print(f"swept leftover {folder}")

    if args.patterns and args.skill_file:
        parser.error("--skill-file is for skill targets; --patterns runs the agent files from this tree")
    case_file = TESTS_DIR / args.target / ("patterns.yaml" if args.patterns else "handoff.yaml")
    return _run_file(parser, args, case_file, args.patterns)


def _load_selected(parser, args, case_file, agent_mode, strict=True):
    cases = load_agent_cases(case_file) if agent_mode else load_cases(case_file)
    try:
        cases = select_cases(cases, args.case, args.pressure)
    except ValueError as e:
        parser.error(str(e))
    if not cases and strict:
        parser.error(f"no cases match the filters in {case_file}")
    return cases


def _run_changed(parser, args) -> int:
    """--changed: pick test files by their covers:, then run (or, with
    --dry-run, only list) each in its own mode."""
    try:
        changed = changed_files(TESTS_DIR.parent, args.changed)
    except ValueError as e:
        parser.error(str(e))
    selected = select_tests(discover(TESTS_DIR), changed)
    root = TESTS_DIR.parent
    print(f"changed files vs {args.changed}: {len(changed)}")
    for f in changed:
        print(f"  {f}")
    if not selected:
        print("no model tests selected: no changed file matches any test's covers:")
        return 0
    print(f"selected test files: {len(selected)}")
    plan = []
    for path, agent_mode in selected:
        cases = _load_selected(parser, args, path, agent_mode, strict=False)
        plan.append((path, agent_mode, cases))
        mode = "agent" if agent_mode else "skill"
        print(f"  {path.relative_to(root)} ({mode} mode): {len(cases)} cases x {args.runs} runs x 2 sides (branch, main) "
              f"= {len(cases) * args.runs * 2} runs, fewer if main is cached")
    if args.dry_run:
        return 0

    for folder in sweep(TESTS_DIR.parent):
        print(f"swept leftover {folder}")
    for path, agent_mode, cases in plan:
        if not cases:
            print(f"skipping {path.relative_to(root)}: no cases match the filters")
            continue
        rc = _run_file(parser, args, path, agent_mode)
        if rc != 0:
            return rc
    return 0


def _run_file(parser, args, case_file, agent_mode) -> int:
    """Run one case file: skill mode for handoff.yaml, agent mode for patterns.yaml."""
    cases = _load_selected(parser, args, case_file, agent_mode)

    # If --skill-file is provided, validate that all cases use the same skill.
    if args.skill_file:
        skills = {c.skill for c in cases}
        if len(skills) > 1:
            parser.error(f"--skill-file requires all cases to use the same skill, but got: {', '.join(sorted(skills))}")
        skill_id = cases[0].skill

    ladders = load_ladders()
    adapter = get_adapter(args.runtime, ladders)
    plugins = plugin_versions("main")

    # If --skill-file is given, replace the branch entry with a temp folder
    # containing the skill file. skillfile_root tracks it for cleanup.
    skillfile_root = None
    if args.skill_file:
        skillfile_plugin = branch_with_skill(args.skill_file, skill_id)
        skillfile_root = skillfile_plugin.parent
        plugins["branch"] = skillfile_plugin

    main_cache = MainCache(
        cache_dir=RESULTS_DIR / CACHE_DIRNAME,
        sha=main_sha("main"),
        runtime=args.runtime,
        model_ladder=ladders[args.runtime],
        adapter_hash=hash_file(adapter_source_path(args.runtime)),
        fresh=args.fresh_main,
    )
    slot_pool = SlotPool(args.jobs)

    def make(fixture_name, slot):
        return make_workdir(fixture_name, slot_pool.path(slot))

    only_tiers = [None if args.ladder else (args.tier or expected_tier(case, ladders)) for case in cases]

    print_lock = threading.Lock()

    def on_start(case):
        with print_lock:
            print(f"running {case.id} (expect {case.expect})", flush=True)

    def on_end(case, result):
        with print_lock:
            print(f"finished {case.id}", flush=True)

    stop_handler = _stop_once()
    previous_term = signal.signal(signal.SIGTERM, stop_handler)
    previous_int = signal.signal(signal.SIGINT, stop_handler)
    results = []
    try:
        try:
            results = run_cases(cases, adapter, plugins, jobs=args.jobs, make=make, remove=remove_workdir,
                                runs=args.runs, max_tier=ladders.get("max_tier", "high"),
                                only_tiers=only_tiers, main_cache=main_cache,
                                on_start=on_start, on_end=on_end)
        finally:
            remove_baseline(plugins)
            slot_pool.close()
            if skillfile_root is not None:
                shutil.rmtree(skillfile_root, ignore_errors=True)
    except Stopped as e:
        print(f"{e}; cleaned up and exiting", file=sys.stderr)
        if skillfile_root is not None:
            shutil.rmtree(skillfile_root, ignore_errors=True)
        return 1
    finally:
        signal.signal(signal.SIGTERM, previous_term)
        signal.signal(signal.SIGINT, previous_int)

    report = render(results, ladders, args.runtime, ladder=args.ladder)
    if args.skill_file:
        lines = report.split("\n")
        lines.insert(2, f"Branch skill text: {args.skill_file}")
        report = "\n".join(lines)
    out_dir = RESULTS_DIR / datetime.now().strftime("%Y-%m-%dT%H%M%S")
    write_results(out_dir, results, report)
    print(report)
    print(f"results: {out_dir}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
