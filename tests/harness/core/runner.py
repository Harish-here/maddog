"""Run one case: repeats, VOID reruns, and the ladder climb. Names no runtime."""
import queue
from concurrent.futures import ThreadPoolExecutor, as_completed
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


def _run_at_tier(case, adapter, version, plugin_path, tier, runs, make, remove, records, slot=0, main_cache=None):
    """One version, run sequentially, one attempt at a time, all in `slot`
    (the case's own job slot for its whole life -- see `run_cases`), so a
    run's workdir path and commit hashes match the version's own previous
    attempt and the runtime's prompt cache can hit."""
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
        workdir = make(case.fixture, slot)
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


def run_case(case: Case, adapter, plugins: dict[str, Path], runs: int = MIN_RUNS,
             make=None, remove=None, max_tier: str = "high",
             only_tier: str | None = None, main_cache=None, slot: int = 0) -> CaseResult:
    """Runs one case start to finish -- every tier it needs, branch then
    main, VOID reruns and the ladder climb -- entirely in `slot` (see
    `run_cases` for how a case's slot is chosen and held for its whole
    life)."""
    if runs < MIN_RUNS:
        raise ValueError(f"runs must be at least {MIN_RUNS}, got {runs}")
    if max_tier not in TIERS:
        raise ValueError(f"max_tier must be one of {TIERS}, got {max_tier!r}")
    if only_tier is not None and only_tier not in TIERS:
        raise ValueError(f"only_tier must be one of {TIERS}, got {only_tier!r}")

    result = CaseResult(case, max_tier=max_tier, only_tier=only_tier)

    if only_tier is not None:
        # Run at exactly the specified tier, no climbing
        tiers_to_run = [only_tier]
    else:
        # Normal behavior: start at low, climb to max_tier
        tiers_to_run = TIERS[: TIERS.index(max_tier) + 1]

    for tier in tiers_to_run:
        try:
            for version, plugin_path in plugins.items():
                _run_at_tier(case, adapter, version, plugin_path, tier, runs, make, remove,
                            result.records, slot=slot, main_cache=main_cache)
        except VoidLimit:
            result.void_limited = True
            return result
        branch_passes = passes(result.records, "branch", tier)
        valid = sum(1 for r in result.records if r.version == "branch" and r.tier == tier and r.verdict.result != "VOID")
        if not tier_failed(branch_passes, valid):
            result.lowest_tier = tier
            return result
    return result


def run_cases(cases: list[Case], adapter, plugins: dict[str, Path], jobs: int,
              make=None, remove=None, runs: int = MIN_RUNS, max_tier: str = "high",
              only_tiers: list[str | None] | None = None, main_cache=None,
              on_start=None, on_end=None) -> list[CaseResult]:
    """Runs `cases` up to `jobs` at a time. Each case claims one job slot the
    moment it starts and keeps it for its whole life -- every tier, branch
    then main, in `run_case`'s normal sequential order -- so that case's own
    later runs reuse the workdir path and commit hashes its earlier runs
    left behind, and the runtime's prompt cache can hit. The slot is
    released the moment the case finishes, so whichever case is queued
    behind it can start. `only_tiers[i]` (default `None` for every case) is
    `cases[i]`'s `only_tier`. `on_start(case)` and `on_end(case, result)`,
    when given, fire once per case, on whichever thread ran it. Results come
    back in `cases` order, regardless of which case finishes first."""
    if jobs < 1:
        raise ValueError(f"jobs must be at least 1, got {jobs}")
    if only_tiers is None:
        only_tiers = [None] * len(cases)

    results: list[CaseResult | None] = [None] * len(cases)

    def run_one(case, only_tier, slot):
        if on_start is not None:
            on_start(case)
        result = run_case(case, adapter, plugins, runs=runs, make=make, remove=remove,
                          max_tier=max_tier, only_tier=only_tier, main_cache=main_cache, slot=slot)
        if on_end is not None:
            on_end(case, result)
        return result

    if jobs == 1:
        # No thread pool at all: cases run one after another on this thread,
        # exactly as before `--jobs` existed at the case level.
        for i, case in enumerate(cases):
            results[i] = run_one(case, only_tiers[i], 0)
        return results

    slots: queue.Queue = queue.Queue()
    for s in range(jobs):
        slots.put(s)

    def worker(case, only_tier):
        slot = slots.get()
        try:
            return run_one(case, only_tier, slot)
        finally:
            slots.put(slot)

    with ThreadPoolExecutor(max_workers=jobs) as executor:
        futures = {executor.submit(worker, case, only_tiers[i]): i for i, case in enumerate(cases)}
        try:
            for fut in as_completed(futures):
                results[futures[fut]] = fut.result()
        finally:
            # Drop any case not yet started (its slot never claimed) rather
            # than let the `with` block's own shutdown wait for every
            # submitted case to run to completion.
            executor.shutdown(wait=True, cancel_futures=True)
    return results
