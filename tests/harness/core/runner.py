"""Run one case: repeats, VOID reruns, and the ladder climb. Names no runtime."""
from dataclasses import dataclass, field
from pathlib import Path

from harness.core.cases import Case, TIERS
from harness.core.events import Event
from harness.core.fixture import make_workdir, remove_workdir
from harness.core.score import Verdict, score

MIN_RUNS = 3
MAX_VOIDS = 3  # per version per tier; past this the case is reported, not retried
REPEATED = 2   # this many failures at a tier means "fails repeatedly"


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
        workdir = make(case.fixture)
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
             make=make_workdir, remove=remove_workdir, max_tier: str = "high",
             only_tier: str | None = None, main_cache=None) -> CaseResult:
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
                _run_at_tier(case, adapter, version, plugin_path, tier, runs, make, remove, result.records, main_cache)
        except VoidLimit:
            result.void_limited = True
            return result
        if failures(result.records, "branch", tier) < REPEATED:
            result.lowest_tier = tier
            return result
    return result
