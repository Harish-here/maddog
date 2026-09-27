"""Run one case: repeats, VOID reruns, and the ladder climb. Names no runtime."""
import queue
from concurrent.futures import FIRST_COMPLETED, ThreadPoolExecutor, wait
from dataclasses import dataclass, field
from pathlib import Path

from harness.core.cases import Case, TIERS
from harness.core.events import Event
from harness.core.score import Verdict, score

MIN_RUNS = 3
MAX_VOIDS = 3  # per version per tier; past this the case is reported, not retried


def tier_failed(passes: int, valid: int) -> bool:
    """A tier counts as failed when fewer than half of its valid runs passed."""
    return passes * 2 < valid


@dataclass
class RunRecord:
    case_id: str
    version: str
    tier: str
    attempt: int
    events: list[Event]
    verdict: Verdict
    cost_usd: float | None = None
    usage: dict | None = None
    cached: bool = False  # True when this record came from the main-run cache, not a fresh run

    def to_dict(self) -> dict:
        return {
            "case": self.case_id, "version": self.version, "tier": self.tier,
            "attempt": self.attempt, "events": [e.to_dict() for e in self.events],
            "result": self.verdict.result, "reason": self.verdict.reason,
            "cost_usd": self.cost_usd, "usage": self.usage, "cached": self.cached,
        }


@dataclass
class CaseResult:
    case: Case
    records: list[RunRecord] = field(default_factory=list)
    lowest_tier: str | None = None
    void_limited: bool = False
    max_tier: str = "high"
    only_tier: str | None = None


class VoidLimit(Exception):
    pass


def _count(records, version, tier, result):
    return sum(1 for r in records if r.version == version and r.tier == tier and r.verdict.result == result)


def passes(records, version: str, tier: str) -> int:
    return _count(records, version, tier, "PASS")


def failures(records, version: str, tier: str) -> int:
    return _count(records, version, tier, "FAIL")


def _run_at_tier(case, adapter, version, plugin_path, tier, runs, make, remove, records, main_cache=None):
    """One version, run sequentially, one attempt at a time -- the `--jobs 1`
    path (also used as the building block `_run_tier_concurrent` schedules
    concurrently for `--jobs > 1`)."""
    if version == "main" and main_cache is not None:
        cached = main_cache.get(case, tier, runs)
        if cached is not None:
            for i, events in enumerate(cached, start=1):
                records.append(RunRecord(case.id, version, tier, i, events, score(events, case.expect), cached=True))
            return

    valid = 0
    voids = 0
    attempt = 0
    valid_events: list[list[Event]] = []
    while valid < runs:
        attempt += 1
        workdir = make(case.fixture, 0)  # only one slot exists when running sequentially
        try:
            outcome = adapter.run(case, plugin_path, workdir, tier)
        finally:
            remove(workdir)
        events = outcome.events
        verdict = score(events, case.expect)
        records.append(RunRecord(case.id, version, tier, attempt, events, verdict, outcome.cost_usd, outcome.usage))
        if verdict.result == "VOID":
            voids += 1
            if voids > MAX_VOIDS:
                raise VoidLimit(f"{case.id}: {voids} refused runs on {version} at {tier}")
        else:
            valid += 1
            valid_events.append(events)

    if version == "main" and main_cache is not None:
        main_cache.put(case, tier, valid_events)


def _one_attempt(case, adapter, version, plugin_path, tier, attempt, make, remove, slots) -> RunRecord:
    """Runs one attempt in whichever job slot is free, blocking until one is.
    Called from a worker thread; every read/write it does is either on its
    own local variables or on the thread-safe slot queue -- book-keeping
    (voids, attempt numbers, records) all happens back on the dispatching
    thread in `_run_tier_concurrent`."""
    slot = slots.get()
    try:
        workdir = make(case.fixture, slot)
        try:
            outcome = adapter.run(case, plugin_path, workdir, tier)
        finally:
            remove(workdir)
    finally:
        slots.put(slot)
    verdict = score(outcome.events, case.expect)
    return RunRecord(case.id, version, tier, attempt, outcome.events, verdict, outcome.cost_usd, outcome.usage)


def _run_tier_concurrent(case, adapter, plugins, tier, runs, make, remove, records, main_cache, jobs):
    """The `--jobs > 1` path: branch's and main's attempts for this tier run
    concurrently, up to `jobs` at a time (a plain `ThreadPoolExecutor` caps
    that regardless of how many attempts are submitted up front). A VOID
    schedules one replacement attempt, same as the sequential path; once any
    version's voids pass MAX_VOIDS, no further attempts are launched for
    either version, but ones already in flight are left to finish rather
    than cut off mid-session. Records are appended branch-before-main, each
    sorted by attempt number, regardless of finish order."""
    order = list(plugins.keys())  # ("branch", "main"), as built by plugin_versions()
    streams = {}
    for version in order:
        plugin_path = plugins[version]
        if version == "main" and main_cache is not None:
            cached = main_cache.get(case, tier, runs)
            if cached is not None:
                cached_records = [RunRecord(case.id, version, tier, i, events, score(events, case.expect), cached=True)
                                   for i, events in enumerate(cached, start=1)]
                streams[version] = {"active": False, "records": cached_records}
                continue
        streams[version] = {"active": True, "plugin_path": plugin_path, "next_attempt": 0,
                            "voids": 0, "records": {}}

    active_versions = [v for v in order if streams[v]["active"]]
    void_error = None
    if active_versions:
        slots: queue.Queue = queue.Queue()
        for slot in range(jobs):
            slots.put(slot)

        with ThreadPoolExecutor(max_workers=jobs) as executor:
            pending = {}

            def launch(version):
                s = streams[version]
                s["next_attempt"] += 1
                attempt = s["next_attempt"]
                fut = executor.submit(_one_attempt, case, adapter, version, s["plugin_path"],
                                      tier, attempt, make, remove, slots)
                pending[fut] = version

            for version in active_versions:
                for _ in range(runs):
                    launch(version)

            while pending:
                done, _ = wait(list(pending), return_when=FIRST_COMPLETED)
                for fut in done:
                    version = pending.pop(fut)
                    record = fut.result()
                    s = streams[version]
                    s["records"][record.attempt] = record
                    if record.verdict.result == "VOID":
                        s["voids"] += 1
                        if s["voids"] > MAX_VOIDS:
                            void_error = void_error or VoidLimit(
                                f"{case.id}: {s['voids']} refused runs on {version} at {tier}")
                        elif void_error is None:
                            launch(version)

    main_events = None
    for version in order:
        s = streams[version]
        ordered = [s["records"][n] for n in sorted(s["records"])] if s["active"] else s["records"]
        records.extend(ordered)
        if version == "main" and main_cache is not None and s["active"]:
            valid = [r.events for r in ordered if r.verdict.result != "VOID"]
            if len(valid) >= runs:
                main_events = valid

    if main_events is not None:
        main_cache.put(case, tier, main_events)

    if void_error is not None:
        raise void_error


def run_case(case: Case, adapter, plugins: dict[str, Path], runs: int = MIN_RUNS,
             make=None, remove=None, max_tier: str = "high",
             only_tier: str | None = None, main_cache=None, jobs: int = 1) -> CaseResult:
    if runs < MIN_RUNS:
        raise ValueError(f"runs must be at least {MIN_RUNS}, got {runs}")
    if max_tier not in TIERS:
        raise ValueError(f"max_tier must be one of {TIERS}, got {max_tier!r}")
    if only_tier is not None and only_tier not in TIERS:
        raise ValueError(f"only_tier must be one of {TIERS}, got {only_tier!r}")
    if jobs < 1:
        raise ValueError(f"jobs must be at least 1, got {jobs}")

    result = CaseResult(case, max_tier=max_tier, only_tier=only_tier)

    if only_tier is not None:
        # Run at exactly the specified tier, no climbing
        tiers_to_run = [only_tier]
    else:
        # Normal behavior: start at low, climb to max_tier
        tiers_to_run = TIERS[: TIERS.index(max_tier) + 1]

    for tier in tiers_to_run:
        try:
            if jobs > 1:
                _run_tier_concurrent(case, adapter, plugins, tier, runs, make, remove, result.records, main_cache, jobs)
            else:
                for version, plugin_path in plugins.items():
                    _run_at_tier(case, adapter, version, plugin_path, tier, runs, make, remove, result.records, main_cache)
        except VoidLimit:
            result.void_limited = True
            return result
        branch_passes = passes(result.records, "branch", tier)
        valid = sum(1 for r in result.records if r.version == "branch" and r.tier == tier and r.verdict.result != "VOID")
        if not tier_failed(branch_passes, valid):
            result.lowest_tier = tier
            return result
    return result
