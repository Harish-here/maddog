import pytest
import run
from harness.core.cases import AgentCase, load_agent_cases
from harness.core.events import Event
from harness.core.maincache import CacheKey, MainCache

GOOD = """
expect: Fast
fixture: fast-tier
cases:
  - id: X1
    prompt: "do it"
    patterns: [TRANSFORM, VERIFY]
    first_call: {kind: [read, command], target: 'add_item'}
    edits_include: [src/a.py]
    before: [['grep', '^write:']]
"""


def write(tmp_path, text):
    path = tmp_path / "patterns.yaml"
    path.write_text(text)
    return path


def test_a_good_file_loads_into_an_agent_case(tmp_path):
    (case,) = load_agent_cases(write(tmp_path, GOOD))
    assert isinstance(case, AgentCase)
    assert (case.id, case.expect, case.fixture) == ("X1", "Fast", "fast-tier")
    assert case.patterns == ("TRANSFORM", "VERIFY")
    assert case.first_call == {"kind": ["read", "command"], "target": "add_item"}
    assert case.checks == {"edits_include": ["src/a.py"], "before": [["grep", "^write:"]]}
    assert case.pressure == "none"


def test_a_single_kind_string_becomes_a_list(tmp_path):
    (case,) = load_agent_cases(write(tmp_path, GOOD.replace("[read, command]", "read")))
    assert case.first_call["kind"] == ["read"]


@pytest.mark.parametrize("old, new, message", [
    ("expect: Fast", "expect: executor-fast", "'expect' must be one of"),
    ("[TRANSFORM, VERIFY]", "[TRANSFORMING]", "patterns must be"),
    ("edits_include:", "edit_include:", "unknown check key"),
    ("[read, command]", "[search]", "first_call.kind"),
    ("'add_item'", "'add_item('", "bad regex"),
    ("[['grep', '^write:']]", "[['grep']]", "pair"),
    ("    prompt: \"do it\"\n", "", "missing 'prompt'"),
])
def test_a_bad_file_fails_loudly(tmp_path, old, new, message):
    with pytest.raises(ValueError, match=message):
        load_agent_cases(write(tmp_path, GOOD.replace(old, new)))


@pytest.mark.parametrize("extra", ["    return_quotes: ['q']\n", "    return_lacks: ['q']\n", "    label: CONTRADICTED\n"])
def test_checks_on_a_models_words_are_for_fast_read_only(tmp_path, extra):
    # The waiver (2026-10-08) reaches Fast-Read's quotes and labels and nothing else.
    with pytest.raises(ValueError, match="waiver"):
        load_agent_cases(write(tmp_path, GOOD + extra))
    (case,) = load_agent_cases(write(tmp_path, (GOOD + extra).replace("expect: Fast\n", "expect: Fast-Read\n")))
    assert case.expect == "Fast-Read"


def test_a_duplicate_id_is_an_error(tmp_path):
    two = GOOD + GOOD.split("cases:\n")[1]
    with pytest.raises(ValueError, match="duplicate case id"):
        load_agent_cases(write(tmp_path, two))


def test_the_cache_key_separates_roles_and_leaves_skill_digests_alone():
    base = dict(sha="s", runtime="r", model="m", prompt="p", fixture="f", adapter_hash="h")
    assert CacheKey(**base).digest() != CacheKey(**base, role="Fast").digest()
    assert CacheKey(**base, role="Fast").digest() != CacheKey(**base, role="Fast-Read").digest()
    # A skill-mode digest: same fields in the same order, nothing appended.
    assert CacheKey(**base).digest() == CacheKey(**base, role="").digest()


def test_main_cache_keeps_two_agents_with_one_prompt_apart(tmp_path):
    cache = MainCache(tmp_path, "sha", "claude-code", {"low": "haiku"}, "hash")
    a = AgentCase("A", "same prompt", "Fast", "fast-tier", ("VERIFY",), {"kind": ["read"], "target": "."}, {})
    b = AgentCase("B", "same prompt", "Fast-Read", "fast-tier", ("VERIFY",), {"kind": ["read"], "target": "."}, {})
    cache.put(a, "low", [[Event("say", "x")]] * 3)
    assert cache.get(a, "low", 3) is not None
    assert cache.get(b, "low", 3) is None


def test_run_py_loads_patterns_yaml_only_when_asked(monkeypatch, tmp_path):
    folder = tmp_path / "agents" / "executor-fast"
    folder.mkdir(parents=True)
    (folder / "patterns.yaml").write_text(GOOD)
    (folder / "handoff.yaml").write_text(
        "skill: advisor-mode\nfixture: todo-app\ncases:\n  - {id: H1, prompt: p, expect: Fast, pressure: none}\n")
    monkeypatch.setattr(run, "TESTS_DIR", tmp_path)
    seen = {}

    def stop(cases, *args, **kwargs):
        seen["cases"] = cases
        raise RuntimeError("stop here")

    monkeypatch.setattr(run, "get_adapter", lambda runtime, ladders: object())
    monkeypatch.setattr(run, "adapter_source_path", lambda runtime: __file__)
    monkeypatch.setattr(run, "sweep", lambda root: [])
    monkeypatch.setattr(run, "plugin_versions", lambda ref: {"branch": tmp_path, "main": tmp_path})
    monkeypatch.setattr(run, "remove_baseline", lambda plugins: None)
    monkeypatch.setattr(run, "main_sha", lambda ref: "sha")
    monkeypatch.setattr(run, "run_cases", stop)
    with pytest.raises(RuntimeError, match="stop here"):
        run.main(["agents/executor-fast", "--runtime", "claude-code", "--patterns", "--case", "X1"])
    assert [c.id for c in seen["cases"]] == ["X1"] and isinstance(seen["cases"][0], AgentCase)
    # Without the flag the same folder runs its handoff.yaml, as before: patterns.yaml is never preferred.
    with pytest.raises(RuntimeError, match="stop here"):
        run.main(["agents/executor-fast", "--runtime", "claude-code", "--case", "H1"])
    assert [c.id for c in seen["cases"]] == ["H1"] and not isinstance(seen["cases"][0], AgentCase)


def test_run_py_refuses_skill_file_for_an_agent_target(monkeypatch, tmp_path, capsys):
    folder = tmp_path / "agents" / "executor-fast"
    folder.mkdir(parents=True)
    (folder / "patterns.yaml").write_text(GOOD)
    draft = tmp_path / "draft.md"
    draft.write_text("x")
    monkeypatch.setattr(run, "TESTS_DIR", tmp_path)
    monkeypatch.setattr(run, "sweep", lambda root: [])
    with pytest.raises(SystemExit):
        run.main(["agents/executor-fast", "--runtime", "claude-code", "--patterns", "--skill-file", str(draft)])
    assert "--skill-file is for skill targets" in capsys.readouterr().err
