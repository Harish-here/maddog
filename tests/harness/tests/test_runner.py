import pytest
from pathlib import Path
from harness.core.events import Event
from harness.core.cases import Case
from harness.core import runner

CASE = Case("c1", "do it", "Fast", "none", "advisor-mode", "todo-app")
PLUGINS = {"branch": Path("/b"), "main": Path("/m")}


class FakeAdapter:
    """Returns scripted events per tier; records every call."""
    def __init__(self, by_tier):
        self.by_tier = by_tier
        self.calls = []

    def run(self, case, plugin_path, workdir, tier):
        self.calls.append((plugin_path, tier))
        script = self.by_tier[tier]
        if script and isinstance(script[0], list):  # a sequence of runs; the last one repeats
            return script.pop(0) if len(script) > 1 else script[0]
        return script  # the same events on every run


def fake_make(name):
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
