import threading
import time
from pathlib import Path

import pytest
from harness.core.events import Event, RunOutcome
from harness.core.cases import Case
from harness.core import runner

CASE = Case("c1", "do it", "Fast", "none", "advisor-mode", "todo-app")
PLUGINS = {"branch": Path("/b"), "main": Path("/m")}


class FakeAdapter:
    """Returns scripted events per tier; records every call."""
    def __init__(self, by_tier, cost_usd=None, usage=None):
        self.by_tier = by_tier
        self.calls = []
        self.cost_usd = cost_usd
        self.usage = usage

    def run(self, case, plugin_path, workdir, tier):
        self.calls.append((plugin_path, tier))
        script = self.by_tier[tier]
        if script and isinstance(script[0], list):  # a sequence of runs; the last one repeats
            events = script.pop(0) if len(script) > 1 else script[0]
        else:
            events = script  # the same events on every run
        return RunOutcome(events, self.cost_usd, self.usage)


def fake_make(name, slot):
    return Path("/tmp/fake") / name


removed = []


def fake_remove(workdir):
    removed.append(workdir)


def run(adapter, **kw):
    return runner.run_case(CASE, adapter, PLUGINS, make=fake_make, remove=fake_remove, **kw)


def test_passing_at_low_stops_there_and_runs_both_versions():
    adapter = FakeAdapter({"low": [Event("handoff", "Fast")]})
    result = run(adapter)
    assert result.lowest_tier == "low"
    assert len(result.records) == 6  # 3 branch + 3 main
    assert {t for _, t in adapter.calls} == {"low"}


def test_repeated_failure_climbs_to_mid():
    adapter = FakeAdapter({"low": [Event("handoff", "Smart")], "mid": [Event("handoff", "Fast")]})
    result = run(adapter)
    assert result.lowest_tier == "mid"
    assert runner.failures(result.records, "branch", "low") == 3
    assert runner.passes(result.records, "branch", "mid") == 3


def test_one_failure_in_three_does_not_climb():
    good, bad = [Event("handoff", "Fast")], [Event("handoff", "Smart")]
    adapter = FakeAdapter({"low": [good, bad, good, good, good, good]})
    assert run(adapter).lowest_tier == "low"


def test_failing_everywhere_gives_no_lowest_tier():
    adapter = FakeAdapter({t: [Event("handoff", "Smart")] for t in ("low", "mid", "high")})
    result = run(adapter)
    assert result.lowest_tier is None
    assert {t for _, t in adapter.calls} == {"low", "mid", "high"}


def test_void_runs_are_rerun_and_not_counted():
    void, good = [Event("refused", "git log")], [Event("handoff", "Fast")]
    adapter = FakeAdapter({"low": [void, good, good, good, good, good, good]})
    result = run(adapter)
    assert runner.passes(result.records, "branch", "low") == 3
    assert sum(1 for r in result.records if r.verdict.result == "VOID") == 1


def test_endless_voids_stop_at_the_limit():
    adapter = FakeAdapter({"low": [Event("refused", "x")]})
    result = run(adapter)
    assert result.void_limited is True
    assert result.lowest_tier is None
    assert len(adapter.calls) == runner.MAX_VOIDS + 1


def test_fewer_than_three_runs_is_rejected():
    with pytest.raises(ValueError, match="at least 3"):
        run(FakeAdapter({"low": [Event("handoff", "Fast")]}), runs=2)


def test_workdir_is_removed_even_when_the_adapter_crashes():
    class Boom:
        def run(self, *a):
            raise RuntimeError("sdk died")
    removed.clear()
    with pytest.raises(RuntimeError, match="sdk died"):
        run(Boom())
    assert removed == [Path("/tmp/fake/todo-app")]


def test_max_tier_stops_the_climb():
    adapter = FakeAdapter({t: [Event("handoff", "Smart")] for t in ("low", "mid", "high")})
    result = run(adapter, max_tier="mid")
    assert result.lowest_tier is None
    assert {t for _, t in adapter.calls} == {"low", "mid"}


def test_only_tier_runs_exactly_that_tier_no_climb():
    adapter = FakeAdapter({"mid": [Event("handoff", "Smart")], "high": [Event("handoff", "Fast")]})
    result = run(adapter, only_tier="mid")
    assert result.lowest_tier is None
    assert result.only_tier == "mid"
    assert {t for _, t in adapter.calls} == {"mid"}
    assert len(result.records) == 6  # 3 branch + 3 main


def test_only_tier_pass_stops_immediately():
    adapter = FakeAdapter({"low": [Event("handoff", "Fast")], "mid": [Event("handoff", "Smart")]})
    result = run(adapter, only_tier="low")
    assert result.lowest_tier == "low"
    assert result.only_tier == "low"
    assert {t for _, t in adapter.calls} == {"low"}


def test_only_tier_invalid_raises_valueerror():
    adapter = FakeAdapter({"low": [Event("handoff", "Fast")]})
    with pytest.raises(ValueError, match="only_tier must be one of"):
        run(adapter, only_tier="invalid")


def test_only_tier_appears_in_result():
    adapter = FakeAdapter({"high": [Event("handoff", "Fast")]})
    result = run(adapter, only_tier="high")
    assert result.only_tier == "high"


def test_cost_and_usage_land_on_the_record():
    usage = {"input_tokens": 10, "output_tokens": 5, "cache_read_tokens": None, "cache_creation_tokens": None}
    adapter = FakeAdapter({"low": [Event("handoff", "Fast")]}, cost_usd=0.01, usage=usage)
    result = run(adapter, only_tier="low")
    assert all(r.cost_usd == 0.01 and r.usage == usage for r in result.records)


def test_missing_cost_is_recorded_as_none_not_zero():
    adapter = FakeAdapter({"low": [Event("handoff", "Fast")]})  # cost_usd defaults to None
    result = run(adapter, only_tier="low")
    assert all(r.cost_usd is None for r in result.records)


class FakeCache:
    """Minimal stand-in for MainCache: records calls, serves scripted hits."""
    def __init__(self, hit=None):
        self.hit = hit  # list[list[Event]] or None
        self.get_calls = []
        self.put_calls = []

    def get(self, case, tier, min_valid):
        self.get_calls.append((case.id, tier, min_valid))
        return self.hit

    def put(self, case, tier, event_lists):
        self.put_calls.append((case.id, tier, event_lists))


def test_cache_hit_skips_running_main():
    cache = FakeCache(hit=[[Event("handoff", "Fast")]] * 3)
    adapter = FakeAdapter({"low": [Event("handoff", "Fast")]})
    result = run(adapter, only_tier="low", main_cache=cache)
    assert cache.get_calls == [("c1", "low", 3)]
    assert cache.put_calls == []
    # only branch ran through the adapter; main came entirely from the cache
    assert {p for p, t in adapter.calls} == {Path("/b")}
    assert runner.passes(result.records, "main", "low") == 3
    assert all(r.cached for r in result.records if r.version == "main")
    assert all(not r.cached for r in result.records if r.version == "branch")


def test_cache_miss_runs_main_and_populates_it():
    cache = FakeCache(hit=None)
    adapter = FakeAdapter({"low": [Event("handoff", "Fast")]})
    result = run(adapter, only_tier="low", main_cache=cache)
    assert {p for p, t in adapter.calls} == {Path("/b"), Path("/m")}
    assert len(cache.put_calls) == 1
    case_id, tier, event_lists = cache.put_calls[0]
    assert (case_id, tier) == ("c1", "low")
    assert len(event_lists) == 3
    assert all(r.cached is False for r in result.records)


def test_branch_never_goes_through_the_cache():
    cache = FakeCache(hit=[[Event("handoff", "Fast")]] * 3)
    adapter = FakeAdapter({"low": [Event("handoff", "Fast")]})
    run(adapter, only_tier="low", main_cache=cache)
    assert all(cid == "c1" for cid, *_ in cache.get_calls)
    # the cache was never consulted for "branch", only "main" ever hits get()/put()
    assert {p for p, t in adapter.calls} == {Path("/b")}


# --- --jobs (concurrent branch/main attempts) -------------------------------

def test_jobs_of_one_is_rejected_below_one():
    adapter = FakeAdapter({"low": [Event("handoff", "Fast")]})
    with pytest.raises(ValueError, match="jobs must be at least 1"):
        run(adapter, only_tier="low", jobs=0)


class OverlapAdapter:
    """Every call sleeps briefly and records the highest number of calls
    seen running at once, so a test can prove --jobs actually overlaps
    work instead of merely accepting the flag."""
    def __init__(self, delay=0.05):
        self.delay = delay
        self.lock = threading.Lock()
        self.current = 0
        self.max_seen = 0
        self.total_calls = 0

    def run(self, case, plugin_path, workdir, tier):
        with self.lock:
            self.current += 1
            self.max_seen = max(self.max_seen, self.current)
            self.total_calls += 1
        time.sleep(self.delay)
        with self.lock:
            self.current -= 1
        return RunOutcome([Event("handoff", case.expect)])


def test_jobs_three_runs_branch_and_main_concurrently():
    adapter = OverlapAdapter()
    run(adapter, only_tier="low", jobs=3)
    # 3 branch + 3 main attempts, capped at 3 concurrent workers: with a
    # sequential (--jobs 1) run max_seen would never exceed 1.
    assert adapter.max_seen >= 3


def test_jobs_writes_records_branch_before_main_by_attempt_regardless_of_finish_order():
    adapter = OverlapAdapter(delay=0.02)
    result = run(adapter, only_tier="low", jobs=3)
    low = [r for r in result.records if r.tier == "low"]
    assert [(r.version, r.attempt) for r in low] == [
        ("branch", 1), ("branch", 2), ("branch", 3),
        ("main", 1), ("main", 2), ("main", 3),
    ]


class PerPluginAdapter:
    """Scripts a fixed sequence of outcomes per plugin_path (i.e. per
    version), unlike FakeAdapter's per-tier script, which --jobs > 1 could
    otherwise let branch and main race over."""
    def __init__(self, scripts):
        self.scripts = {path: list(events) for path, events in scripts.items()}
        self.calls = []

    def run(self, case, plugin_path, workdir, tier):
        self.calls.append((plugin_path, tier))
        events = self.scripts[plugin_path].pop(0)
        return RunOutcome(events)


def test_void_is_replaced_under_jobs_and_still_reaches_three_valid():
    void, good = [Event("refused", "x")], [Event("handoff", "Fast")]
    adapter = PerPluginAdapter({
        Path("/b"): [void, good, good, good],  # attempt 1 void, replaced by attempt 4
        Path("/m"): [good, good, good],
    })
    result = run(adapter, only_tier="low", jobs=2)
    branch = sorted((r for r in result.records if r.version == "branch"), key=lambda r: r.attempt)
    assert [r.verdict.result for r in branch] == ["VOID", "PASS", "PASS", "PASS"]
    assert runner.passes(result.records, "branch", "low") == 3
    assert runner.passes(result.records, "main", "low") == 3


def test_endless_voids_stop_the_case_under_jobs_too():
    adapter = FakeAdapter({"low": [Event("refused", "x")]})
    result = run(adapter, jobs=2)
    assert result.void_limited is True
    assert result.lowest_tier is None


def test_cache_hit_skips_main_under_jobs():
    cache = FakeCache(hit=[[Event("handoff", "Fast")]] * 3)
    adapter = OverlapAdapter()
    result = run(adapter, only_tier="low", jobs=3, main_cache=cache)
    assert runner.passes(result.records, "main", "low") == 3
    assert all(r.cached for r in result.records if r.version == "main")
    # only the 3 branch attempts ever reached the adapter; main came from the cache
    assert adapter.total_calls == 3
