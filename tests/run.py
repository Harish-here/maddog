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

--changed --record is the release run: after the offline tests pass, it runs
every selected test file in full (every case, expected tier, 3+ runs) and
writes tests/releases/<version>/ for tests/gate.py to check. It needs local
main equal to origin/main, a bumped version, and no uncommitted change to a
covered file.

    tests/.venv/bin/python tests/run.py --changed --record --runtime <name>
"""
import argparse
import shutil
import signal
import subprocess
import sys
import threading
from datetime import datetime, timezone
from pathlib import Path

from harness.core.changed import changed_files, select_for_base
from harness.core.release import (case_table, dirty_covered, entry_for, plugin_version, previous_attempt,
                                  rev_parse, slug_of, total_cost, write_release)
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
# Overridable by tests: the repo that --changed reads and --record writes into.
REPO_ROOT = TESTS_DIR.parent


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
    parser.add_argument("--record", action="store_true",
                        help="with --changed: run the offline tests, then every selected file in full, and write "
                             "tests/releases/<version>/ (needs local main == origin/main and a bumped version)")
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
    if args.record:
        if args.changed is None:
            parser.error("--record goes with --changed")
        refused = [flag for flag, on in (("--pressure", args.pressure), ("--tier", args.tier),
                                         ("--ladder", args.ladder), ("--dry-run", args.dry_run)) if on]
        if refused:
            parser.error(f"--record covers every case at its expected tier; it cannot be combined with {', '.join(refused)}")
        if args.runs < MIN_RUNS:
            parser.error(f"--record needs --runs of at least {MIN_RUNS}, got {args.runs}")
        if args.changed not in ("main", "origin/main"):
            parser.error("--record compares against main; give BASE as main or origin/main")
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


def check_main_synced(root):
    """Fetch origin, then require local main to equal origin/main. Raises ValueError otherwise."""
    fetch = subprocess.run(["git", "-C", str(root), "fetch", "origin"], capture_output=True, text=True)
    if fetch.returncode != 0:
        raise ValueError(f"git fetch origin failed: {fetch.stderr.strip()}")
    local, remote = rev_parse(root, "main"), rev_parse(root, "origin/main")
    if local != remote:
        raise ValueError(f"local main ({local[:8]}) is not origin/main ({remote[:8]}); update main first")


def run_offline_tests(root):
    """Run the harness and guard tests. Returns (exit code, pytest's summary line)."""
    r = subprocess.run([sys.executable, "-m", "pytest", "tests/harness", "tests/guard", "-q", "-p", "no:cacheprovider"],
                       cwd=root, capture_output=True, text=True)
    lines = [line for line in r.stdout.splitlines() if line.strip()]
    if r.returncode != 0:
        print(r.stdout[-3000:])
    return r.returncode, lines[-1].strip() if lines else ""


def _run_changed(parser, args) -> int:
    """--changed: pick test files by their covers:, then run (or, with
    --dry-run, only list) each in its own mode. With --record, also gate the
    run on the offline tests and write tests/releases/<version>/."""
    root = REPO_ROOT
    offline_line = ""
    if args.record:
        try:
            check_main_synced(root)
        except ValueError as e:
            print(f"refusing to record: {e}", file=sys.stderr)
            return 1
        rc, offline_line = run_offline_tests(root)
        if rc != 0:
            print("refusing to record: the offline tests failed", file=sys.stderr)
            return 1
        print(f"offline tests: {offline_line}")
    try:
        changed = changed_files(root, args.changed)
        selection = select_for_base(root, args.changed, changed)
    except ValueError as e:
        parser.error(str(e))
    print(f"changed files vs {args.changed}: {len(changed)}")
    for f in changed:
        print(f"  {f}")
    if not selection.selected:
        print("no model tests selected: no changed file matches any test's covers:")
        if args.record:
            print("no covered changes; nothing recorded")
        return 0
    for gone in selection.deleted:
        print(f"a selected test file was deleted: {gone}", file=sys.stderr)
    if args.record and selection.deleted:
        print("refusing to record: restore it, or drop it from every covers: list", file=sys.stderr)
        return 1
    selected = [t for t in selection.selected if t.in_head]
    print(f"selected test files: {len(selected)}")
    plan = []
    for t in selected:
        path = root / t.path
        cases = _load_selected(parser, args, path, t.agent_mode, strict=False)
        plan.append((path, t.agent_mode, cases))
        mode = "agent" if t.agent_mode else "skill"
        print(f"  {t.path} ({mode} mode): {len(cases)} cases x {args.runs} runs x 2 sides (branch, main) "
              f"= {len(cases) * args.runs * 2} runs, fewer if main is cached")
    if args.dry_run:
        return 0

    if args.record:
        version = plugin_version(root)
        if version == plugin_version(root, args.changed):
            print("refusing to record: covered files changed; bump the version first", file=sys.stderr)
            return 1
        dirty = dirty_covered(root, selected)
        if dirty:
            print("refusing to record: uncommitted changes to covered files (commit them so the fingerprints "
                  "match what ran): " + ", ".join(dirty), file=sys.stderr)
            return 1

    for folder in sweep(root):
        print(f"swept leftover {folder}")
    collected = []
    for path, agent_mode, cases in plan:
        if not cases:
            print(f"skipping {path.relative_to(root)}: no cases match the filters")
            continue
        rc = _run_file(parser, args, path, agent_mode, collected)
        if rc != 0:
            return rc
    return _record(root, args, version, selected, collected, changed, offline_line) if args.record else 0


def _record(root, args, version, selected, collected, changed, offline_line) -> int:
    """Write tests/releases/<version>/ from the finished runs; exit 1 when any file failed D1."""
    attempt = previous_attempt(root, version) + 1
    entries, tables = [], {}
    for test, run in zip(selected, collected):
        try:
            results_path = run["out_dir"].relative_to(root).as_posix()
        except ValueError:
            results_path = str(run["out_dir"])
        entry = entry_for(root, test, run["results"], args.runs, results_path)
        entries.append(entry)
        tables[slug_of(test.path)] = case_table(entry, run["results"])
    manifest = {
        "version": version,
        "tested_commit": rev_parse(root, "HEAD"),
        "base_commit": rev_parse(root, args.changed),
        "changed_files": changed,
        "attempt": attempt,
        "runs": args.runs,
        "tests": entries,
        "offline": offline_line,
        "total_cost_usd": round(total_cost([run["results"] for run in collected]), 4),
        "time": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }
    out = write_release(root, manifest, offline_line, tables)
    failed = [e["path"] for e in entries if e["verdict"] != "pass"]
    print(f"recorded {out.relative_to(root)}: attempt {attempt} for version {version}")
    for e in entries:
        print(f"  {e['path']}: {e['verdict']}")
    if failed:
        print("recording failed the pass rule; the gate will reject it", file=sys.stderr)
        return 1
    return 0


def _run_file(parser, args, case_file, agent_mode, collect=None) -> int:
    """Run one case file: skill mode for handoff.yaml, agent mode for patterns.yaml.
    `collect`, when given, receives {"results", "out_dir"} for the finished file."""
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
    if collect is not None:
        collect.append({"results": results, "out_dir": out_dir})
    return 0


if __name__ == "__main__":
    sys.exit(main())
