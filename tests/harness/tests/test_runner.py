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


# --- --jobs (concurrent cases, each pinned to one slot) ---------------------

class PerPluginAdapter:
    """Scripts a fixed sequence of outcomes per plugin_path (i.e. per
    version). Not safe for two cases to share concurrently (its script lists
    aren't locked), so the tests below that use it keep to a single case."""
    def __init__(self, scripts):
        self.scripts = {path: list(events) for path, events in scripts.items()}
        self.calls = []

    def run(self, case, plugin_path, workdir, tier):
        self.calls.append((plugin_path, tier))
        events = self.scripts[plugin_path].pop(0)
        return RunOutcome(events)


def make_cases(n):
    return [Case(f"c{i}", f"do it {i}", "Fast", "none", "advisor-mode", f"fixture{i}") for i in range(n)]


def slotted_make(name, slot):
    return Path(f"/tmp/fake/slot{slot}") / name


class CaseTimedAdapter:
    """Every call sleeps `delays[case.id]` and records, per case id: every
    workdir it was called with, and the peak number of *other* calls for the
    same case seen running at once. It also records the peak number of
    distinct case ids with a call in flight at once. That's enough to prove,
    for a `run_cases` call: how many cases actually overlapped, that no case
    ever overlapped with itself, and that every run of one case reused the
    same slot path."""
    def __init__(self, delays):
        self.delays = delays
        self.lock = threading.Lock()
        self.current_by_case: dict[str, int] = {}
        self.max_per_case = 0
        self.max_cases_at_once = 0
        self.workdirs: dict[str, set] = {}
        self.total_calls = 0

    def run(self, case, plugin_path, workdir, tier):
        with self.lock:
            self.current_by_case[case.id] = self.current_by_case.get(case.id, 0) + 1
            self.max_per_case = max(self.max_per_case, self.current_by_case[case.id])
            self.max_cases_at_once = max(self.max_cases_at_once, len(self.current_by_case))
            self.workdirs.setdefault(case.id, set()).add(workdir)
            self.total_calls += 1
        time.sleep(self.delays.get(case.id, 0.01))
        with self.lock:
            self.current_by_case[case.id] -= 1
            if self.current_by_case[case.id] == 0:
                del self.current_by_case[case.id]
        return RunOutcome([Event("handoff", case.expect)])


def test_run_cases_jobs_below_one_is_rejected():
    with pytest.raises(ValueError, match="jobs must be at least 1"):
        runner.run_cases([CASE], FakeAdapter({"low": [Event("handoff", "Fast")]}), PLUGINS, jobs=0,
                         make=fake_make, remove=fake_remove, only_tiers=["low"])


def test_run_cases_overlaps_up_to_jobs_cases_never_within_one_case():
    cases = make_cases(5)
    adapter = CaseTimedAdapter({c.id: 0.05 for c in cases})
    runner.run_cases(cases, adapter, PLUGINS, jobs=3, make=slotted_make, remove=fake_remove,
                     only_tiers=["low"] * 5)
    # 5 cases, 3 slots: at least 2 and at most 3 cases run at once.
    assert 2 <= adapter.max_cases_at_once <= 3
    # A case's own 6 attempts (3 branch + 3 main) always run one after another.
    assert adapter.max_per_case == 1


def test_run_cases_keeps_one_case_in_the_same_slot_for_every_run():
    cases = make_cases(5)
    adapter = CaseTimedAdapter({c.id: 0.02 for c in cases})
    runner.run_cases(cases, adapter, PLUGINS, jobs=3, make=slotted_make, remove=fake_remove,
                     only_tiers=["low"] * 5)
    assert all(len(paths) == 1 for paths in adapter.workdirs.values())


def test_run_cases_returns_results_in_handoff_order_regardless_of_finish_order():
    cases = make_cases(4)
    # c0 is slowest, c3 is fastest, so finish order is the reverse of handoff order.
    delays = {c.id: 0.08 - i * 0.02 for i, c in enumerate(cases)}
    adapter = CaseTimedAdapter(delays)
    results = runner.run_cases(cases, adapter, PLUGINS, jobs=4, make=slotted_make, remove=fake_remove,
                               only_tiers=["low"] * 4)
    assert [r.case.id for r in results] == [c.id for c in cases]


def test_run_cases_void_replacement_still_works_under_jobs_greater_than_one():
    void, good = [Event("refused", "x")], [Event("handoff", "Fast")]
    adapter = PerPluginAdapter({
        Path("/b"): [void, good, good, good],  # attempt 1 void, replaced by attempt 4
        Path("/m"): [good, good, good],
    })
    results = runner.run_cases([CASE], adapter, PLUGINS, jobs=2, make=fake_make, remove=fake_remove,
                               only_tiers=["low"])
    result = results[0]
    branch = sorted((r for r in result.records if r.version == "branch"), key=lambda r: r.attempt)
    assert [r.verdict.result for r in branch] == ["VOID", "PASS", "PASS", "PASS"]
    assert runner.passes(result.records, "branch", "low") == 3
    assert runner.passes(result.records, "main", "low") == 3


def test_run_cases_endless_voids_stop_that_case_under_jobs_too():
    adapter = FakeAdapter({"low": [Event("refused", "x")]})
    results = runner.run_cases([CASE], adapter, PLUGINS, jobs=2, make=fake_make, remove=fake_remove,
                               only_tiers=["low"])
    assert results[0].void_limited is True
    assert results[0].lowest_tier is None


def test_run_cases_ladder_climb_still_works_under_jobs_greater_than_one():
    adapter = FakeAdapter({"low": [Event("handoff", "Smart")], "mid": [Event("handoff", "Fast")]})
    results = runner.run_cases([CASE], adapter, PLUGINS, jobs=2, make=fake_make, remove=fake_remove)
    assert results[0].lowest_tier == "mid"


def test_run_cases_cache_hit_skips_main_under_jobs():
    cache = FakeCache(hit=[[Event("handoff", "Fast")]] * 3)
    cases = make_cases(3)
    adapter = CaseTimedAdapter({c.id: 0.02 for c in cases})
    results = runner.run_cases(cases, adapter, PLUGINS, jobs=3, make=slotted_make, remove=fake_remove,
                               only_tiers=["low"] * 3, main_cache=cache)
    for result in results:
        assert runner.passes(result.records, "main", "low") == 3
        assert all(r.cached for r in result.records if r.version == "main")
    # only each case's 3 branch attempts ever reached the adapter (3 cases x 3); main came from the cache
    assert adapter.total_calls == 9


# --- tier_failed function -------------------------------------------------------

def test_tier_failed_returns_true_when_fewer_than_half_pass():
    assert runner.tier_failed(0, 3) is True   # 0/3
    assert runner.tier_failed(1, 3) is True   # 1/3
    assert runner.tier_failed(1, 10) is True  # 1/10
    assert runner.tier_failed(4, 10) is True  # 4/10


def test_tier_failed_returns_false_when_half_or_more_pass():
    assert runner.tier_failed(2, 3) is False   # 2/3
    assert runner.tier_failed(3, 3) is False   # 3/3
    assert runner.tier_failed(5, 10) is False  # 5/10 (exactly half)
    assert runner.tier_failed(7, 10) is False  # 7/10


# --- Ladder climb scales with run count -------------------------------------------------------

def test_ladder_climbs_on_1_of_3_failures():
    # 1 pass: 1 * 2 = 2 < 3, so failed, should climb
    good, bad = [Event("handoff", "Fast")], [Event("handoff", "Smart")]
    adapter = FakeAdapter({"low": [good, bad, bad], "mid": [Event("handoff", "Fast")]})
    result = run(adapter)
    assert runner.passes(result.records, "branch", "low") == 1
    assert result.lowest_tier == "mid"


def test_ladder_does_not_climb_on_2_of_3_passes():
    # 2 passes: 2 * 2 = 4 not < 3, so not failed, should not climb
    good, bad = [Event("handoff", "Fast")], [Event("handoff", "Smart")]
    adapter = FakeAdapter({"low": [good, good, bad], "mid": [Event("handoff", "Smart")]})
    result = run(adapter)
    assert runner.passes(result.records, "branch", "low") == 2
    assert result.lowest_tier == "low"
