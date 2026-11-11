"""Only the registry folder, the guard tests and two docs may name a runtime, a model or a tool.

The rule is CLAUDE.md, Invariants, "Adapter set": within tests/, only code under
tests/harness/runtimes/ names runtime identifiers, plus tests/guard/, tests/README.md
and tests/requirements.txt. This test is the check. It builds its word list from the
registry (harness/runtimes/__init__.py and ladders.yaml), so it names none itself, and
it reads every tracked file under tests/.

Words flagged, anywhere in a file's text or path:
  - each registered runtime name, and the module name of its adapter file
  - each model id in the runtime's ladder, and the letters-only parts of those ids
    (the vendor and the model family), case-insensitively
  - each tool identifier the registry lists, only as a quoted string such as "Name".
    Ordinary words that are also tool names (Read, Write, Edit ...) are not flagged in prose.

Exceptions, stated here and nowhere else:
  - tests/releases/ holds recorded manifests: file lists and hashes as they were written.
  - A repository path is not a runtime identifier. A top-level tracked name that contains a
    flagged word (the plugin manifest folder, the repo-internal folder, the project
    instruction file) is blanked out before the scan, wherever it appears in tests/.
"""
import re
import subprocess

import pytest
from harness.core.cases import TESTS_DIR, load_ladders
from harness.runtimes import ADAPTER_SOURCE, TOOL_IDENTIFIERS

REPO_ROOT = TESTS_DIR.parent
ALLOWED = ("tests/harness/runtimes/", "tests/guard/", "tests/README.md", "tests/requirements.txt")
RECORDED = "tests/releases/"


def tracked(pathspec):
    out = subprocess.run(["git", "-C", str(REPO_ROOT), "ls-files", "-z", "--", pathspec],
                         capture_output=True, text=True, check=True).stdout
    return [name for name in out.split("\0") if name]


def runtime_words():
    """(words matched case-insensitively anywhere, tool identifiers matched when quoted)."""
    ladders = load_ladders()
    models = {model for runtime in ADAPTER_SOURCE for model in ladders[runtime].values()}
    words = set(ADAPTER_SOURCE) | {path.stem for path in ADAPTER_SOURCE.values()} | models
    words |= {part for model in models for part in re.split(r"[^A-Za-z]+", model) if len(part) > 2}
    tools = {tool for names in TOOL_IDENTIFIERS.values() for tool in names}
    return words, tools


def repository_paths(words, top_level_names):
    return sorted((name for name in top_level_names if any(w.lower() in name.lower() for w in words)),
                  key=len, reverse=True)


def violations(files, words, tools, repo_paths):
    """The names of the files under tests/ that break the rule. files maps a repo-relative path to its text."""
    word = re.compile("|".join(re.escape(w) for w in sorted(words, key=len, reverse=True)), re.IGNORECASE)
    tool = re.compile("[\"'](" + "|".join(re.escape(t) for t in tools) + ")[\"']")
    repo_path = re.compile(r"(?<![\w.])(" + "|".join(re.escape(p) for p in repo_paths) + r")(?![\w-])") if repo_paths else None
    bad = []
    for path, text in files.items():
        if path.startswith(ALLOWED) or path.startswith(RECORDED):
            continue
        for scanned in (path, text):
            if repo_path:
                scanned = repo_path.sub(" ", scanned)
            if word.search(scanned) or tool.search(scanned):
                bad.append(path)
                break
    return bad


def read_all(names):
    return {n: (REPO_ROOT / n).read_text(errors="replace") for n in names if (REPO_ROOT / n).is_file()}


def test_no_file_in_tests_names_a_runtime_model_or_tool_outside_the_allowed_paths():
    words, tools = runtime_words()
    top_level = {name.split("/")[0] for name in tracked(".")}
    bad = violations(read_all(tracked("tests")), words, tools, repository_paths(words, top_level))
    assert not bad, "outside tests/harness/runtimes/, tests/guard/, tests/README.md, tests/requirements.txt: " + ", ".join(bad)


def test_the_scan_has_files_to_scan_and_words_to_look_for():
    # Guards the guard: an empty tracked list or word list would let the real check pass on nothing.
    words, tools = runtime_words()
    assert len(read_all(tracked("tests"))) > 20
    assert set(ADAPTER_SOURCE) <= words and tools
    assert any(p.startswith(ALLOWED) for p in tracked("tests"))


# --- the check can fail: the same function on synthetic files built from the registry's own words ---

@pytest.fixture
def words():
    return runtime_words()


def runtime_name():
    return next(iter(ADAPTER_SOURCE))  # any registered runtime serves; the check builds its words from all of them


def model_id():
    return next(iter(load_ladders()[runtime_name()].values()))


def tool_id():
    return next(iter(TOOL_IDENTIFIERS[runtime_name()]))


@pytest.mark.parametrize("make_text", [
    lambda: f"--runtime {runtime_name()}",
    lambda: f"ladder = '{model_id()}'",
    lambda: f"the {re.findall('[A-Za-z]{3,}', model_id())[-1].upper()} tier",   # a model family, upper-cased
    lambda: f'to_event("{tool_id()}", {{}})',
    lambda: f"module {ADAPTER_SOURCE[runtime_name()].stem}",
], ids=["runtime", "model", "family", "tool", "adapter-module"])
def test_a_forbidden_word_in_a_file_outside_the_allowed_paths_is_flagged(words, make_text):
    files = {"tests/harness/tests/test_x.py": make_text(), "tests/run.py": "clean"}
    assert violations(files, *words, []) == ["tests/harness/tests/test_x.py"]


def test_a_forbidden_word_in_a_file_name_is_flagged(words):
    assert violations({f"tests/harness/core/{runtime_name()}_x.py": "clean"}, *words, []) != []


@pytest.mark.parametrize("path", [
    "tests/harness/runtimes/test_a.py", "tests/guard/test_a.py", "tests/README.md",
    "tests/requirements.txt", "tests/releases/1.0.0/manifest.json",
])
def test_the_allowed_paths_and_recorded_manifests_are_not_flagged(words, path):
    assert violations({path: f"{runtime_name()} {model_id()} \"{tool_id()}\""}, *words, []) == []


def test_a_repository_path_is_not_flagged_but_the_same_word_elsewhere_is(words):
    word = runtime_name().split("-")[0]
    repo_paths = [f".{word}", f".{word}-plugin"]
    ok = {"tests/a.py": f'x = ".{word}-plugin/plugin.json"; y = ".{word}/plans/p.md"'}
    assert violations(ok, *words, repo_paths) == []
    assert violations({"tests/a.py": f'x = ".{word}/p"; y = "a_{word}_b"'}, *words, repo_paths) == ["tests/a.py"]


def test_the_repository_paths_are_the_tracked_top_level_names_that_hold_a_word(words):
    found = repository_paths(words[0], {name.split("/")[0] for name in tracked(".")})
    assert found and all(not n.startswith("tests") for n in found)


def test_a_tool_name_in_prose_is_not_flagged(words):
    assert violations({"tests/a.py": f"{tool_id()} the file, then run it"}, *words, []) == []
