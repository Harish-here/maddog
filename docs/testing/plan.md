# Model-Driven Test Setup Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build `tests/`, a harness that runs advisor-mode on five happy-path tasks, stops each session at its first handoff, and scores which helper got the work, against both this branch and `main`, on a low → mid → high model ladder.

**Architecture:** A neutral core (`tests/harness/core/`) loads cases, builds fixture repos, runs the loop, scores event logs, and writes reports. It names no runtime. One adapter (`tests/harness/runtimes/claude_code.py`) runs a real Claude Code session through the Claude Agent SDK. It turns tool calls into six event kinds and stops the session at the first handoff or write. `tests/run.py` is the only command a person types.

**Tech Stack:** Python 3.13, `claude-agent-sdk` (Python), `pyyaml`, `pytest`, `git`. A plain virtual environment at `tests/.venv`.

**Spec:** `docs/testing/spec.md`. Read it before any task. This plan builds what it decides. The few additions beyond it are listed under File Structure.

## Global Constraints

- Commits: conventional style, scope `testing` (e.g. `feat(testing): …`). **No `Co-Authored-By` trailer and no "Generated with Claude Code" line** (the maintainer's global rule). Commit on the current branch `claude/advisor-mode-framework-v2jhtw`. Never push.
- Only `tests/harness/runtimes/` may name runtime identifiers: tool names (`Agent`, `Edit`, …), agent IDs (`maddog:executor-*`), model IDs, slash syntax, SDK imports. Core files, core tests, case files, and `run.py` never do. Adapter tests live beside the adapter, in `runtimes/`.
- Cases name roles from exactly this set: `Fast-Read`, `Fast`, `Smart`, `Judge`, `Lead`.
- Event kinds are exactly: `handoff`, `write`, `read`, `command`, `skill_load`, `refused`.
- Tiers are exactly, in order: `low`, `mid`, `high`. Pressure levels are exactly: `none`, `high`.
- Ladder for `claude-code`: `low: claude-haiku-4-5-20251001`, `mid: claude-sonnet-5`, `high: claude-opus-5-5`. `expected_tier: {none: low, high: mid}`. The runner climbs no higher than `max_tier` (currently `mid`).
- Runs per case: at least 3. The runner rejects fewer. "Fails repeatedly" means at least 2 failing runs at a tier.
- Fixture copies are made in a temporary folder outside this repo. No test session ever sees a repo `CLAUDE.md`.
- Harness Python is written plainly (explicit loops, no clever idioms): the maintainer reads TypeScript first.
- Do not edit any file under `agents/`, `skills/`, `hooks/`, `scripts/`, or `workflows/`.

## Review Focus

- **The advisor never hands off** (it asks the user a question, or runs out of turns): the run must end and score FAIL (no handoff, or too many calls before one), never hang. Pinned in Task 3 (score). Task 9 bounds the session with a turn cap and a wall-clock timeout, and a timeout returns the events so far; the Task 10 live run confirms it.
- **Every run comes back VOID** (the environment refuses everything): the runner must stop after a fixed number of VOIDs and report the case as void-limited, never loop forever. Pinned in Task 7.
- **The advisor hands off to an agent outside the five roles** (for example `general-purpose` or `Explore`): score FAIL naming that agent, never crash on a missing map key. Pinned in Task 3 and Task 9.
- **The fixture copy would land inside this repo** (someone sets `TMPDIR` inside the repo): refuse to run, because a repo `CLAUDE.md` would leak into the session. Pinned in Task 5.
- **A run crashes midway** (SDK error, Ctrl-C): the temporary fixture folder and the `main` worktree must still be removed. Pinned in Task 7 (fixture folder) and Task 10 (`test_run.py`, `main` worktree).

---

## File Structure

| File | Responsibility |
|---|---|
| `tests/README.md` | How to set up, run, add a case, and read a report |
| `tests/requirements.txt` | `claude-agent-sdk`, `pyyaml`, `pytest` |
| `tests/run.py` | CLI: parse arguments, wire core + adapter, write results |
| `tests/harness/__init__.py`, `core/__init__.py`, `runtimes/__init__.py` | Make packages importable; `runtimes/__init__.py` holds the adapter registry |
| `tests/harness/core/events.py` | `Event` and the six kinds; the `Adapter` protocol |
| `tests/harness/core/cases.py` | Load a `handoff.yaml` into `Case` objects; load tier order and expected tiers |
| `tests/harness/core/score.py` | Pure function: events + expected role → `Verdict` |
| `tests/harness/core/fixture.py` | Copy a fixture to a temp folder outside the repo, `git init`, build branches from patches |
| `tests/harness/core/baseline.py` | Plugin paths for `branch` (this working tree) and `main` (git worktree); cleanup |
| `tests/harness/core/runner.py` | Run a case: repeats, VOID reruns and limit, ladder climb, lowest passing tier |
| `tests/harness/core/report.py` | Render `report.md`; write `runs.jsonl` |
| `tests/harness/runtimes/ladders.yaml` | Tier → model per runtime; pressure → expected tier |
| `tests/harness/runtimes/claude_code.py` | Claude Code adapter: SDK session, event mapping, stop at handoff |
| `tests/harness/conftest.py` | Puts `tests/` on `sys.path` for every harness test |
| `tests/harness/tests/` | Unit tests for the core and `run.py` (one `test_*.py` per file) |
| `tests/harness/runtimes/test_claude_code.py` | Unit tests for the Claude Code adapter, kept beside it so runtime names stay in `runtimes/` |
| `tests/fixtures/todo-app/` | Practice repo: a small to-do CLI with tests, CI config, CHANGELOG |
| `tests/fixtures/todo-app/feature-export.patch` | The `feature/export` branch, applied at copy time |
| `tests/skills/advisor-mode/handoff.yaml` | The five happy-path cases |
| `.gitignore` | Add `tests/results/` and `tests/.venv/` |
| `CLAUDE.md`, `CONTRIBUTING.md`, `README.md` | Doc edits from the spec (Task 11) |

Additions beyond the spec, each small and inside its structure:

- **Files:** `core/cases.py` and `core/runner.py` (the spec lists the core's jobs but not these file names), and harness unit tests in `tests/harness/tests/` and `tests/harness/runtimes/test_claude_code.py`.
- **VOID limit:** the spec says a VOID run reruns. The runner caps this at `MAX_VOIDS = 3` per version per tier and flags the case `VOID LIMIT`, so a broken environment cannot loop forever.
- **Stop at the first write too:** the adapter ends a session at the first write as well as the first handoff. A write already decides FAIL, so running on only costs tokens.
- **Shell writes count as writes:** a shell command that changes files or git state (`sed -i`, a `>` redirect, `mv`, `git commit`, …) becomes a `write` event, per the spec's "the advisor did the work itself".
- **Per-case expected tier:** the spec's escalation option "raise the case's expected tier, and record why" needs a place to live. A case may carry `expected_tier` plus `why`; without them, the tier comes from pressure.
- **README location:** `README.md` has no layout section, so Task 11 adds `tests/` to its §Contributing section instead.
- **Work-starting tools stop the session:** `Workflow`, `RemoteTrigger`, `CronCreate` and `ScheduleWakeup` start work outside the session, so the adapter denies them and ends the session, as it does at a handoff or a write. They are recorded as `command` events. (Maintainer change, 2026-09-27.)
- **Ladder capped at `mid`:** `ladders.yaml` carries `max_tier: mid`; the runner climbs no higher, and the report's flag says which tier it tried up to. `high` stays in the ladder for later. (Maintainer change, 2026-09-27.)

---

### Task 1: Trial — confirm the two SDK assumptions (build gate)

The spec requires this before anything else is built. The trial script is throwaway and is **not committed**. Only the findings file is.

**Files:**
- Create (not committed): `$TMPDIR/maddog-trial/trial.py`
- Create: `docs/testing/trial-findings.md`

**Interfaces:**
- Produces: confirmed values used verbatim by Task 9: the handoff tool name(s) as they appear in the stream, the `subagent_type` value format, whether a `PreToolUse` deny stops the helper, whether `Grep`/`Glob` calls appear in the message stream, and the installed `claude-agent-sdk` version.

- [ ] **Step 1: Make a venv and install the SDK**

```bash
cd /Users/harishamutha/maddog-skills
python3 -m venv tests/.venv
tests/.venv/bin/pip install -q claude-agent-sdk pyyaml pytest
tests/.venv/bin/pip show claude-agent-sdk | grep -i '^version'
```
Expected: a version line. Record it.

- [ ] **Step 2: Write the trial script**

```python
# $TMPDIR/maddog-trial/trial.py — throwaway; never committed
import sys, tempfile, pathlib, anyio
from claude_agent_sdk import (
    ClaudeSDKClient, ClaudeAgentOptions, HookMatcher,
    AssistantMessage, UserMessage, SystemMessage, ResultMessage,
    ToolUseBlock, ToolResultBlock,
)

REPO = "/Users/harishamutha/maddog-skills"
STOP = "maddog-test: stopped here by the test harness"

async def deny(input_data, tool_use_id, context):
    return {"hookSpecificOutput": {
        "hookEventName": "PreToolUse",
        "permissionDecision": "deny",
        "permissionDecisionReason": STOP,
    }}

async def session(prompt, workdir):
    opts = ClaudeAgentOptions(
        model="claude-haiku-4-5-20251001",
        cwd=workdir,
        plugins=[{"type": "local", "path": REPO}],
        setting_sources=[],  # explicit: load no user, project, or local settings
        permission_mode="bypassPermissions",
        max_turns=6,
        hooks={"PreToolUse": [HookMatcher(matcher="Agent|Task", hooks=[deny])]},
    )
    async with ClaudeSDKClient(options=opts) as client:
        await client.query(prompt)
        async for msg in client.receive_response():
            if isinstance(msg, SystemMessage):
                data = msg.data
                print("INIT plugins:", data.get("plugins"))
                print("INIT agents:", [a for a in data.get("agents", []) if "maddog" in str(a)])
                print("INIT other plugins present:", [p for p in data.get("plugins", []) if "maddog" not in str(p)])
                print("INIT slash has advisor-mode:", any("advisor-mode" in str(s) for s in data.get("slash_commands", [])))
            elif isinstance(msg, AssistantMessage):
                for b in msg.content:
                    if isinstance(b, ToolUseBlock):
                        print("TOOL_USE", b.name, dict(b.input), "parent:", getattr(msg, "parent_tool_use_id", None))
            elif isinstance(msg, UserMessage) and isinstance(msg.content, list):
                for b in msg.content:
                    if isinstance(b, ToolResultBlock):
                        print("TOOL_RESULT is_error:", b.is_error, str(b.content)[:200])
            elif isinstance(msg, ResultMessage):
                print("RESULT", msg.subtype, "turns:", msg.num_turns)

async def main():
    work = tempfile.mkdtemp(prefix="maddog-trial-")
    pathlib.Path(work, "a.txt").write_text("def hello(): pass\n")
    print("=== A+B: isolation + stop at handoff ===")
    await session("Use the Agent tool with subagent_type maddog:executor-fast-read to list the files in this folder. Do nothing else.", work)
    print("=== C: are Grep/Glob visible in the stream? ===")
    await session("Use the Grep tool to search for 'def' in this folder, then the Glob tool for '*.txt'. Then stop.", work)

anyio.run(main)
```

- [ ] **Step 3: Run it**

```bash
mkdir -p "$TMPDIR/maddog-trial" && tests/.venv/bin/python "$TMPDIR/maddog-trial/trial.py" 2>&1 | tee "$TMPDIR/maddog-trial/out.txt"
```

- [ ] **Step 4: Check the output against six pass conditions**

1. `INIT plugins` shows the maddog plugin from `/Users/harishamutha/maddog-skills`, and `INIT other plugins present` is empty (no user plugins such as superpowers: the user's settings did not load).
2. `INIT slash has advisor-mode: True`, and `INIT agents` lists `maddog:executor-*` agents.
3. Session A shows a `TOOL_USE` whose name is `Agent` or `Task` with `subagent_type: maddog:executor-fast-read`, then a `TOOL_RESULT is_error: True` containing the stop text, and **no** `TOOL_USE` line with a non-empty `parent` (the helper never ran).
4. Session C shows `TOOL_USE Grep` and `TOOL_USE Glob` lines.
5. Both sessions end with a `RESULT` line.
6. The sessions authenticated, with no login error. Record whether `ANTHROPIC_API_KEY` was set in the shell. If it was unset, the runs used the existing Claude Code login.

If the SDK import or an option name fails, adjust names from `tests/.venv/lib/python3.13/site-packages/claude_agent_sdk/` (read `types.py`). That is allowed and must be recorded in the findings.

- [ ] **Step 5: Write `docs/testing/trial-findings.md`**

```markdown
# Trial findings — <date>

SDK: claude-agent-sdk <version>  (Task 2 pins exactly this version)

| # | Condition | Result | Evidence (one line from out.txt) |
|---|---|---|---|
| 1 | Only this plugin loads, no user settings | PASS/FAIL | … |
| 2 | advisor-mode slash command and executor agents present | PASS/FAIL | … |
| 3 | PreToolUse deny stops the helper before it runs | PASS/FAIL | … |
| 4 | Grep and Glob calls visible in the stream | PASS/FAIL | … |
| 5 | Sessions end cleanly | PASS/FAIL | … |
| 6 | Sessions authenticate with no settings loaded | PASS/FAIL | ANTHROPIC_API_KEY set: yes/no |

Handoff tool name(s) seen: …
subagent_type format: …
Option or import names that differed from the plan: … (or "none")
```

- [ ] **Step 6: Gate**

If conditions 1 or 3 fail: **STOP. Do not start Task 2.** Report to the maintainer: the spec says to revisit the design. If only 2, 4, 5, or 6 fail, also stop and report. The adapter in Task 9 depends on all six.

- [ ] **Step 7: Commit the findings only**

```bash
git add docs/testing/trial-findings.md
git commit -m "docs(testing): record the SDK trial findings"
```

---

### Task 2: Scaffold and events

**Files:**
- Create: `tests/requirements.txt`, `tests/harness/__init__.py`, `tests/harness/core/__init__.py`, `tests/harness/runtimes/__init__.py` (empty for now), `tests/harness/core/events.py`, `tests/harness/conftest.py`, `tests/harness/tests/test_events.py`
- Modify: `.gitignore`

**Interfaces:**
- Produces: `Event(kind: str, detail: str = "")` (frozen dataclass, validates kind); `KINDS: tuple[str, ...]`; `Event.to_dict() -> dict`; `Adapter` protocol with `run(case, plugin_path: Path, workdir: Path, tier: str) -> list[Event]`.

- [ ] **Step 1: Write requirements, packages, gitignore**

`tests/requirements.txt` (pin the SDK to the version recorded in `docs/testing/trial-findings.md`, so isolation does not drift with SDK defaults):
```text
claude-agent-sdk==<version from trial-findings.md>
pyyaml
pytest
```
Create the three empty `__init__.py` files. Append to `.gitignore`:
```text
tests/results/
tests/.venv/
```

`tests/harness/conftest.py` (at the harness root, so it covers both `harness/tests/` and `harness/runtimes/`):
```python
import sys
from pathlib import Path

# Make `harness` importable the same way run.py sees it: tests/ on sys.path.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
```

- [ ] **Step 2: Write the failing test**

`tests/harness/tests/test_events.py`:
```python
import pytest
from harness.core.events import Event, KINDS


def test_kinds_are_the_six_from_the_spec():
    assert KINDS == ("handoff", "write", "read", "command", "skill_load", "refused")


def test_event_rejects_unknown_kind():
    with pytest.raises(ValueError):
        Event("edit")


def test_event_to_dict():
    assert Event("handoff", "Fast").to_dict() == {"kind": "handoff", "detail": "Fast"}
```

- [ ] **Step 3: Run it to see it fail**

Run: `tests/.venv/bin/python -m pytest tests/harness/tests/test_events.py -q`
Expected: FAIL with `ModuleNotFoundError: No module named 'harness.core.events'`.

- [ ] **Step 4: Implement**

`tests/harness/core/events.py`:
```python
"""The six kinds of event every run is turned into. Names no runtime."""
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Protocol

KINDS = ("handoff", "write", "read", "command", "skill_load", "refused")


@dataclass(frozen=True)
class Event:
    kind: str
    detail: str = ""  # handoff: the role; otherwise the tool, path, or command

    def __post_init__(self):
        if self.kind not in KINDS:
            raise ValueError(f"unknown event kind: {self.kind!r}")

    def to_dict(self) -> dict:
        return asdict(self)


class Adapter(Protocol):
    def run(self, case, plugin_path: Path, workdir: Path, tier: str) -> list[Event]:
        """Run one case once and return its ordered event log."""
        ...
```

- [ ] **Step 5: Run the test to see it pass**

Run: `tests/.venv/bin/python -m pytest tests/harness/tests/test_events.py -q`
Expected: `3 passed`.

- [ ] **Step 6: Commit**

```bash
git add .gitignore tests/requirements.txt tests/harness
git commit -m "feat(testing): scaffold the harness and its event kinds"
```

---

### Task 3: Scoring

**Files:**
- Create: `tests/harness/core/score.py`, `tests/harness/tests/test_score.py`

**Interfaces:**
- Consumes: `Event` (Task 2).
- Produces: `Verdict(result: str, reason: str)` (frozen dataclass; `result` is `"PASS" | "FAIL" | "VOID"`); `score(events: list[Event], expect: str) -> Verdict`.

- [ ] **Step 1: Write the failing tests**

`tests/harness/tests/test_score.py`:
```python
from harness.core.events import Event
from harness.core.score import score


def test_right_helper_first_passes():
    assert score([Event("handoff", "Fast")], "Fast").result == "PASS"


def test_skill_load_and_one_read_before_handoff_pass():
    events = [Event("skill_load", "efficient-md"), Event("read", "Read"), Event("handoff", "Fast")]
    assert score(events, "Fast").result == "PASS"


def test_two_tool_calls_before_handoff_fail():
    events = [Event("read", "Read"), Event("command", "ls"), Event("handoff", "Fast")]
    v = score(events, "Fast")
    assert v.result == "FAIL" and "more than one" in v.reason


def test_wrong_helper_fails_and_names_it():
    v = score([Event("handoff", "Smart")], "Fast")
    assert v.result == "FAIL" and "Smart" in v.reason


def test_unknown_agent_fails_and_names_it():
    v = score([Event("handoff", "other:general-purpose")], "Fast")
    assert v.result == "FAIL" and "general-purpose" in v.reason


def test_write_before_handoff_fails():
    v = score([Event("write", "src/todo/store.py")], "Fast")
    assert v.result == "FAIL" and "wrote" in v.reason


def test_no_handoff_fails():
    v = score([Event("read", "Read")], "Fast")
    assert v.result == "FAIL" and v.reason == "no handoff"


def test_empty_log_fails_as_no_handoff():
    assert score([], "Fast").reason == "no handoff"


def test_any_refusal_voids_even_with_a_right_handoff():
    events = [Event("command", "git log"), Event("refused", "git log"), Event("handoff", "Fast")]
    assert score(events, "Fast").result == "VOID"
```

- [ ] **Step 2: Run to see them fail**

Run: `tests/.venv/bin/python -m pytest tests/harness/tests/test_score.py -q`
Expected: FAIL with `ModuleNotFoundError`.

- [ ] **Step 3: Implement**

`tests/harness/core/score.py`:
```python
"""Score one run from its event log. Pure logic; names no runtime."""
from dataclasses import dataclass

from harness.core.events import Event


@dataclass(frozen=True)
class Verdict:
    result: str  # PASS | FAIL | VOID
    reason: str


def score(events: list[Event], expect: str) -> Verdict:
    for event in events:
        if event.kind == "refused":
            return Verdict("VOID", f"a command was refused: {event.detail}")

    calls_before_handoff = 0
    for event in events:
        if event.kind == "handoff":
            if event.detail == expect:
                return Verdict("PASS", f"handed to {expect}")
            return Verdict("FAIL", f"first handoff went to {event.detail}, expected {expect}")
        if event.kind == "write":
            return Verdict("FAIL", f"advisor wrote before handing off: {event.detail}")
        if event.kind in ("read", "command"):
            calls_before_handoff += 1
            if calls_before_handoff > 1:
                return Verdict("FAIL", "more than one tool call before the handoff")
    return Verdict("FAIL", "no handoff")
```

- [ ] **Step 4: Run to see them pass**

Run: `tests/.venv/bin/python -m pytest tests/harness/tests/test_score.py -q`
Expected: `9 passed`.

- [ ] **Step 5: Commit**

```bash
git add tests/harness/core/score.py tests/harness/tests/test_score.py
git commit -m "feat(testing): score a run as PASS, FAIL, or VOID"
```

---

### Task 4: Cases, ladder config, and the five happy-path cases

**Files:**
- Create: `tests/harness/core/cases.py`, `tests/harness/runtimes/ladders.yaml`, `tests/skills/advisor-mode/handoff.yaml`, `tests/harness/tests/test_cases.py`

**Interfaces:**
- Produces:
  - `ROLES = ("Fast-Read", "Fast", "Smart", "Judge", "Lead")`, `TIERS = ("low", "mid", "high")`, `PRESSURES = ("none", "high")`
  - `TESTS_DIR: Path` (the `tests/` folder), `LADDERS_FILE: Path`
  - `Case(id: str, prompt: str, expect: str, pressure: str, skill: str | None, fixture: str, expected_tier: str | None = None, why: str | None = None)` frozen dataclass
  - `load_cases(path: Path) -> list[Case]` (raises `ValueError` on a bad role, pressure, or tier, a duplicate id, a missing field, or an `expected_tier` without a `why`)
  - `load_ladders(path: Path = LADDERS_FILE) -> dict` (the parsed YAML)
  - `expected_tier(case: Case, ladders: dict) -> str` (the case's own `expected_tier` if set, otherwise the pressure mapping)

- [ ] **Step 1: Write the config and the cases**

`tests/harness/runtimes/ladders.yaml`:
```yaml
# Tier → model for each runtime. Cases name only tiers.
claude-code:
  low:  claude-haiku-4-5-20251001
  mid:  claude-sonnet-5
  high: claude-opus-5-5
# Pressure level → the tier a case is expected to pass at.
expected_tier:
  none: low
  high: mid
# highest tier the runner climbs to; raise to high later
max_tier: mid
```

`tests/skills/advisor-mode/handoff.yaml`:
```yaml
# Checks which helper advisor-mode hands the first piece of work to.
skill: advisor-mode
fixture: todo-app
cases:
  - id: list-flags
    prompt: "For each command the CLI offers, list its flags and the test that covers it."
    expect: Fast-Read
    pressure: none
  - id: rename-add-item
    prompt: "Rename `add_item` to `create_item` everywhere, including tests. Change nothing else."
    expect: Fast
    pressure: none
  - id: iso-due-dates
    prompt: "The due-date parser rejects `2026-10-01T09:00`. Make it accept ISO date-times, keeping the existing tests passing."
    expect: Smart
    pressure: none
  - id: export-ready
    prompt: "Branch `feature/export` is about to merge into main, which the team builds on. Get a verdict on whether it's ready."
    expect: Judge
    pressure: none
  - id: ci-flake
    prompt: "Tests pass locally but fail in CI on some runs. Find out why and get it fixed."
    expect: Lead
    pressure: none
```

- [ ] **Step 2: Write the failing tests**

`tests/harness/tests/test_cases.py`:
```python
import pytest
from harness.core.cases import (
    TESTS_DIR, load_cases, load_ladders, expected_tier, ROLES, TIERS,
)

ADVISOR = TESTS_DIR / "skills" / "advisor-mode" / "handoff.yaml"


def test_advisor_cases_load_with_one_per_role():
    cases = load_cases(ADVISOR)
    assert [c.expect for c in cases] == list(ROLES)
    assert all(c.skill == "advisor-mode" and c.fixture == "todo-app" for c in cases)


def test_every_runtime_ladder_has_every_tier():
    ladders = load_ladders()
    runtimes = [key for key in ladders if key not in ("expected_tier", "max_tier")]
    assert runtimes
    for runtime in runtimes:
        assert set(ladders[runtime]) == set(TIERS)


def test_expected_tier_follows_pressure():
    ladders = load_ladders()
    case = load_cases(ADVISOR)[0]
    assert expected_tier(case, ladders) == "low"


def write(tmp_path, body):
    p = tmp_path / "handoff.yaml"
    p.write_text(body)
    return p


def test_unknown_role_is_rejected(tmp_path):
    p = write(tmp_path, "skill: x\nfixture: todo-app\ncases:\n  - {id: a, prompt: p, expect: Wizard, pressure: none}\n")
    with pytest.raises(ValueError, match="Wizard"):
        load_cases(p)


def test_unknown_pressure_is_rejected(tmp_path):
    p = write(tmp_path, "skill: x\nfixture: todo-app\ncases:\n  - {id: a, prompt: p, expect: Fast, pressure: medium}\n")
    with pytest.raises(ValueError, match="medium"):
        load_cases(p)


def test_duplicate_id_is_rejected(tmp_path):
    p = write(tmp_path, "skill: x\nfixture: todo-app\ncases:\n"
                        "  - {id: a, prompt: p, expect: Fast, pressure: none}\n"
                        "  - {id: a, prompt: q, expect: Fast, pressure: none}\n")
    with pytest.raises(ValueError, match="duplicate"):
        load_cases(p)


def test_missing_field_is_rejected(tmp_path):
    p = write(tmp_path, "skill: x\nfixture: todo-app\ncases:\n  - {id: a, expect: Fast, pressure: none}\n")
    with pytest.raises(ValueError, match="prompt"):
        load_cases(p)


def test_case_can_raise_its_expected_tier_with_a_reason(tmp_path):
    p = write(tmp_path, "skill: x\nfixture: todo-app\ncases:\n"
                        "  - {id: a, prompt: p, expect: Fast, pressure: none, expected_tier: mid, why: needs two steps}\n")
    case = load_cases(p)[0]
    assert expected_tier(case, load_ladders()) == "mid"
    bad = write(tmp_path, "skill: x\nfixture: todo-app\ncases:\n"
                          "  - {id: a, prompt: p, expect: Fast, pressure: none, expected_tier: mid}\n")
    with pytest.raises(ValueError, match="why"):
        load_cases(bad)


def test_no_skill_means_plain_session(tmp_path):
    p = write(tmp_path, "fixture: todo-app\ncases:\n  - {id: a, prompt: p, expect: Fast, pressure: none}\n")
    assert load_cases(p)[0].skill is None
```

- [ ] **Step 3: Run to see them fail**

Run: `tests/.venv/bin/python -m pytest tests/harness/tests/test_cases.py -q`
Expected: FAIL with `ModuleNotFoundError`.

- [ ] **Step 4: Implement**

`tests/harness/core/cases.py`:
```python
"""Load case files and the ladder config. Names no runtime."""
from dataclasses import dataclass
from pathlib import Path

import yaml

ROLES = ("Fast-Read", "Fast", "Smart", "Judge", "Lead")
TIERS = ("low", "mid", "high")
PRESSURES = ("none", "high")

TESTS_DIR = Path(__file__).resolve().parents[2]
LADDERS_FILE = TESTS_DIR / "harness" / "runtimes" / "ladders.yaml"


@dataclass(frozen=True)
class Case:
    id: str
    prompt: str
    expect: str
    pressure: str
    skill: str | None  # None means a plain session with no skill loaded
    fixture: str
    expected_tier: str | None = None  # set only when the maintainer raised it
    why: str | None = None            # required with expected_tier


def load_cases(path: Path) -> list[Case]:
    data = yaml.safe_load(Path(path).read_text())
    skill = data.get("skill")
    fixture = data.get("fixture")
    if not fixture:
        raise ValueError(f"{path}: missing 'fixture'")
    cases = []
    seen = set()
    for raw in data.get("cases", []):
        for field in ("id", "prompt", "expect", "pressure"):
            if field not in raw:
                raise ValueError(f"{path}: a case is missing '{field}'")
        if raw["expect"] not in ROLES:
            raise ValueError(f"{path}: case {raw['id']}: unknown role {raw['expect']!r}")
        if raw["pressure"] not in PRESSURES:
            raise ValueError(f"{path}: case {raw['id']}: unknown pressure {raw['pressure']!r}")
        if raw["id"] in seen:
            raise ValueError(f"{path}: duplicate case id {raw['id']!r}")
        seen.add(raw["id"])
        tier = raw.get("expected_tier")
        why = raw.get("why")
        if tier is not None and tier not in TIERS:
            raise ValueError(f"{path}: case {raw['id']}: unknown tier {tier!r}")
        if tier is not None and not why:
            raise ValueError(f"{path}: case {raw['id']}: expected_tier needs a 'why'")
        cases.append(Case(raw["id"], raw["prompt"], raw["expect"], raw["pressure"], skill, fixture, tier, why))
    if not cases:
        raise ValueError(f"{path}: no cases")
    return cases


def load_ladders(path: Path = LADDERS_FILE) -> dict:
    return yaml.safe_load(Path(path).read_text())


def expected_tier(case: Case, ladders: dict) -> str:
    if case.expected_tier:
        return case.expected_tier
    return ladders["expected_tier"][case.pressure]
```

- [ ] **Step 5: Run to see them pass**

Run: `tests/.venv/bin/python -m pytest tests/harness/tests/test_cases.py -q`
Expected: `9 passed`.

- [ ] **Step 6: Commit**

```bash
git add tests/harness/core/cases.py tests/harness/runtimes/ladders.yaml tests/skills tests/harness/tests/test_cases.py
git commit -m "feat(testing): load cases and the model ladder; add the five advisor-mode cases"
```

---

### Task 5: The todo-app fixture and `fixture.py`

**Files:**
- Create: `tests/fixtures/todo-app/` (files below), `tests/fixtures/todo-app/feature-export.patch`, `tests/harness/core/fixture.py`, `tests/harness/tests/test_fixture.py`

**Interfaces:**
- Consumes: `TESTS_DIR` (Task 4).
- Produces: `FIXTURES_DIR: Path`; `make_workdir(name: str) -> Path` (returns `<tempdir>/<name>`, a git repo on `main` with one branch per patch); `remove_workdir(workdir: Path) -> None`.

The fixture only has to look real to the advisor. No helper ever runs, so its tests never execute during a test run.

- [ ] **Step 1: Write the fixture files**

`tests/fixtures/todo-app/pyproject.toml`:
```toml
[project]
name = "todo"
version = "0.3.0"
requires-python = ">=3.11"

[project.scripts]
todo = "todo.cli:main"
```

`tests/fixtures/todo-app/CHANGELOG.md`:
```markdown
# Changelog

## 0.3.0
- Add `--due-before` to `list`.

## 0.2.0
- Add due dates.

## 0.1.0
- First release: `add`, `list`, `done`.
```

`tests/fixtures/todo-app/src/todo/__init__.py`: empty.

`tests/fixtures/todo-app/src/todo/store.py`:
```python
import json
import os
from pathlib import Path


def _path() -> Path:
    return Path(os.environ.get("TODO_FILE", "todo.json"))


def load() -> list[dict]:
    path = _path()
    if not path.exists():
        return []
    return json.loads(path.read_text())


def save(items: list[dict]) -> None:
    _path().write_text(json.dumps(items, indent=2))


def add_item(title: str, due: str | None = None, priority: int = 2) -> dict:
    items = load()
    item = {"id": len(items) + 1, "title": title, "due": due, "priority": priority, "done": False}
    items.append(item)
    save(items)
    return item


def mark_done(item_id: int) -> None:
    items = load()
    for item in items:
        if item["id"] == item_id:
            item["done"] = True
    save(items)
```

`tests/fixtures/todo-app/src/todo/due.py`:
```python
from datetime import date, datetime


def parse_due(text: str) -> date:
    """Parse a due date written as YYYY-MM-DD."""
    return datetime.strptime(text, "%Y-%m-%d").date()


def is_overdue(due: str, today: date | None = None) -> bool:
    today = today or date.today()
    return parse_due(due) < today
```

`tests/fixtures/todo-app/src/todo/cli.py`:
```python
import argparse
from datetime import date

from todo import store
from todo.due import parse_due


def main(argv=None):
    parser = argparse.ArgumentParser(prog="todo")
    sub = parser.add_subparsers(dest="command", required=True)

    add = sub.add_parser("add")
    add.add_argument("title")
    add.add_argument("--due")
    add.add_argument("--priority", type=int, default=2)

    lst = sub.add_parser("list")
    lst.add_argument("--all", action="store_true")
    lst.add_argument("--due-before")

    done = sub.add_parser("done")
    done.add_argument("id", type=int)

    args = parser.parse_args(argv)
    if args.command == "add":
        if args.due:
            parse_due(args.due)
        store.add_item(args.title, args.due, args.priority)
    elif args.command == "list":
        for item in store.load():
            if item["done"] and not args.all:
                continue
            if args.due_before and (not item["due"] or parse_due(item["due"]) >= parse_due(args.due_before)):
                continue
            print(f"{item['id']}. {item['title']}")
    elif args.command == "done":
        store.mark_done(args.id)
```

`tests/fixtures/todo-app/tests/test_store.py`:
```python
from todo import store


def test_add_item_assigns_ids(tmp_path, monkeypatch):
    monkeypatch.setenv("TODO_FILE", str(tmp_path / "t.json"))
    assert store.add_item("a")["id"] == 1
    assert store.add_item("b")["id"] == 2


def test_mark_done(tmp_path, monkeypatch):
    monkeypatch.setenv("TODO_FILE", str(tmp_path / "t.json"))
    store.add_item("a")
    store.mark_done(1)
    assert store.load()[0]["done"] is True
```

`tests/fixtures/todo-app/tests/test_due.py`:
```python
from datetime import date

import pytest
from todo.due import parse_due, is_overdue


def test_parse_due_reads_iso_dates():
    assert parse_due("2026-10-01") == date(2026, 10, 1)


def test_parse_due_rejects_garbage():
    with pytest.raises(ValueError):
        parse_due("next week")


def test_is_overdue():
    assert is_overdue("2026-01-01", today=date(2026, 2, 1))
```

`tests/fixtures/todo-app/tests/test_cli.py` (the `test_list_due_before_today` test is the CI flake: it reads the clock twice, so it fails when a CI runner crosses midnight UTC):
```python
from datetime import date, timedelta

from todo import cli, store


def test_add_and_list(tmp_path, monkeypatch, capsys):
    monkeypatch.setenv("TODO_FILE", str(tmp_path / "t.json"))
    cli.main(["add", "milk"])
    cli.main(["list"])
    assert "1. milk" in capsys.readouterr().out


def test_done_hides_item(tmp_path, monkeypatch, capsys):
    monkeypatch.setenv("TODO_FILE", str(tmp_path / "t.json"))
    cli.main(["add", "milk"])
    cli.main(["done", "1"])
    cli.main(["list"])
    assert "milk" not in capsys.readouterr().out


def test_list_due_before_today(tmp_path, monkeypatch, capsys):
    monkeypatch.setenv("TODO_FILE", str(tmp_path / "t.json"))
    yesterday = (date.today() - timedelta(days=1)).isoformat()
    store.add_item("old", due=yesterday)
    cli.main(["list", "--due-before", date.today().isoformat()])
    assert "old" in capsys.readouterr().out
```

`tests/fixtures/todo-app/.github/workflows/ci.yml`:
```yaml
name: ci
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python: ["3.11", "3.12", "3.13"]
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python }}
      - run: pip install -e . pytest
      - run: pytest -q
```

- [ ] **Step 2: Generate `feature-export.patch`**

The branch adds CSV export with no tests and no CHANGELOG entry, so the Judge has something real to rule on.

```bash
cd /Users/harishamutha/maddog-skills
T=$(mktemp -d) && cp -R tests/fixtures/todo-app "$T/app" && cd "$T/app"
git -c core.hooksPath=/dev/null init -q -b main && git add -A && git -c user.name=t -c user.email=t@t -c commit.gpgsign=false commit -q -m init
cat > src/todo/export.py <<'EOF'
import csv
import sys

from todo import store


def export_csv(out=sys.stdout) -> None:
    writer = csv.writer(out)
    writer.writerow(["id", "title", "due", "done"])
    for item in store.load():
        writer.writerow([item["id"], item["title"], item["due"], item["done"]])
EOF
python3 - <<'EOF'
p = "src/todo/cli.py"
s = open(p).read()
s = s.replace('    done = sub.add_parser("done")\n',
              '    sub.add_parser("export")\n\n    done = sub.add_parser("done")\n')
s = s.replace('    elif args.command == "done":\n',
              '    elif args.command == "export":\n        from todo.export import export_csv\n        export_csv()\n    elif args.command == "done":\n')
open(p, "w").write(s)
EOF
git add -A && git diff --cached > /Users/harishamutha/maddog-skills/tests/fixtures/todo-app/feature-export.patch
cd /Users/harishamutha/maddog-skills && rm -rf "$T"
grep -c '^+' tests/fixtures/todo-app/feature-export.patch
```
Expected: a count above 10, and the patch touches `src/todo/cli.py` and `src/todo/export.py`.

- [ ] **Step 3: Write the failing tests**

`tests/harness/tests/test_fixture.py`:
```python
import subprocess
from pathlib import Path

import pytest
from harness.core import fixture
from harness.core.cases import TESTS_DIR

REPO = TESTS_DIR.parent


def git(workdir, *args):
    return subprocess.run(["git", "-C", str(workdir), *args], capture_output=True, text=True, check=True).stdout


def test_workdir_is_a_git_repo_outside_this_repo():
    work = fixture.make_workdir("todo-app")
    try:
        assert not work.resolve().is_relative_to(REPO.resolve())
        assert git(work, "branch", "--show-current").strip() == "main"
        assert (work / "src" / "todo" / "store.py").exists()
        assert not list(work.glob("*.patch"))
    finally:
        fixture.remove_workdir(work)
    assert not work.exists()


def test_patch_becomes_a_branch():
    work = fixture.make_workdir("todo-app")
    try:
        branches = git(work, "branch", "--format=%(refname:short)").split()
        assert "feature/export" in branches
        files = git(work, "diff", "--name-only", "main", "feature/export").split()
        assert "src/todo/export.py" in files
        assert not (work / "src" / "todo" / "export.py").exists()  # main stays checked out
    finally:
        fixture.remove_workdir(work)


def test_refuses_a_temp_dir_inside_this_repo(monkeypatch):
    monkeypatch.setenv("TMPDIR", str(REPO / "tests"))
    import tempfile
    monkeypatch.setattr(tempfile, "tempdir", None)
    with pytest.raises(RuntimeError, match="inside this repo"):
        fixture.make_workdir("todo-app")


def test_unknown_fixture_is_an_error():
    with pytest.raises(FileNotFoundError):
        fixture.make_workdir("no-such-app")
```

- [ ] **Step 4: Run to see them fail**

Run: `tests/.venv/bin/python -m pytest tests/harness/tests/test_fixture.py -q`
Expected: FAIL with `ImportError` / `AttributeError` on `make_workdir`.

- [ ] **Step 5: Implement**

`tests/harness/core/fixture.py`:
```python
"""Build a fresh practice repo for one run, outside this repo. Names no runtime."""
import shutil
import subprocess
import tempfile
from pathlib import Path

from harness.core.cases import TESTS_DIR

FIXTURES_DIR = TESTS_DIR / "fixtures"
REPO_ROOT = TESTS_DIR.parent

# Keep the user's git config (hooks, signing, identity) out of fixture repos.
GIT = ["git", "-c", "core.hooksPath=/dev/null", "-c", "commit.gpgsign=false",
       "-c", "user.name=fixture", "-c", "user.email=fixture@example.invalid"]


def _git(workdir: Path, *args: str) -> None:
    subprocess.run([*GIT, "-C", str(workdir), *args], check=True, capture_output=True)


def make_workdir(name: str) -> Path:
    source = FIXTURES_DIR / name
    if not source.is_dir():
        raise FileNotFoundError(f"no fixture named {name!r} in {FIXTURES_DIR}")

    root = Path(tempfile.mkdtemp(prefix=f"maddog-test-{name}-"))
    if root.resolve().is_relative_to(REPO_ROOT.resolve()):
        shutil.rmtree(root, ignore_errors=True)
        raise RuntimeError(f"temp folder {root} is inside this repo; a repo CLAUDE.md would leak into the session")

    workdir = root / name
    shutil.copytree(source, workdir, ignore=shutil.ignore_patterns("*.patch", "__pycache__"))
    _git(workdir, "init", "-q", "-b", "main")
    _git(workdir, "add", "-A")
    _git(workdir, "commit", "-q", "-m", "initial")

    for patch in sorted(source.glob("*.patch")):
        branch = patch.stem.replace("-", "/", 1)  # feature-export.patch → feature/export
        _git(workdir, "switch", "-q", "-c", branch)
        _git(workdir, "apply", str(patch))
        _git(workdir, "add", "-A")
        _git(workdir, "commit", "-q", "-m", f"work on {branch}")
        _git(workdir, "switch", "-q", "main")
    return workdir


def remove_workdir(workdir: Path) -> None:
    shutil.rmtree(Path(workdir).parent, ignore_errors=True)
```

- [ ] **Step 6: Run to see them pass**

Run: `tests/.venv/bin/python -m pytest tests/harness/tests/test_fixture.py -q`
Expected: `4 passed`.

- [ ] **Step 7: Commit**

```bash
git add tests/fixtures tests/harness/core/fixture.py tests/harness/tests/test_fixture.py
git commit -m "feat(testing): add the todo-app fixture and build fresh copies outside the repo"
```

---

### Task 6: Baseline plugin copies

**Files:**
- Create: `tests/harness/core/baseline.py`, `tests/harness/tests/test_baseline.py`

**Interfaces:**
- Produces: `plugin_versions(ref: str = "main") -> dict[str, Path]` returning `{"branch": <repo root>, "main": <worktree path>}`; `remove_baseline(versions: dict[str, Path]) -> None` (removes the worktree, never the repo root).

`"branch"` is the working tree as it stands, uncommitted edits included, so a skill edit can be tested before it is committed.

- [ ] **Step 1: Write the failing tests**

`tests/harness/tests/test_baseline.py`:
```python
import subprocess
import pytest
from harness.core import baseline
from harness.core.cases import TESTS_DIR

REPO = TESTS_DIR.parent


def worktrees():
    return subprocess.run(["git", "-C", str(REPO), "worktree", "list"], capture_output=True, text=True).stdout


def test_versions_are_branch_and_main():
    versions = baseline.plugin_versions()
    try:
        assert versions["branch"] == REPO
        assert (versions["main"] / "skills" / "advisor-mode" / "SKILL.md").exists()
        assert str(versions["main"]) in worktrees()
    finally:
        baseline.remove_baseline(versions)
    assert str(versions["main"]) not in worktrees()
    assert REPO.exists()


def test_unknown_ref_is_a_clear_error():
    with pytest.raises(RuntimeError, match="no-such-ref"):
        baseline.plugin_versions("no-such-ref")
```

- [ ] **Step 2: Run to see them fail**

Run: `tests/.venv/bin/python -m pytest tests/harness/tests/test_baseline.py -q`
Expected: FAIL with `ImportError`.

- [ ] **Step 3: Implement**

`tests/harness/core/baseline.py`:
```python
"""Plugin copies to compare: this working tree and main. Names no runtime."""
import shutil
import subprocess
import tempfile
from pathlib import Path

from harness.core.cases import TESTS_DIR

REPO_ROOT = TESTS_DIR.parent


def plugin_versions(ref: str = "main") -> dict[str, Path]:
    # resolve(): on macOS the temp dir sits under the /var symlink, and git
    # worktree list prints the real /private/var path.
    root = Path(tempfile.mkdtemp(prefix="maddog-baseline-")).resolve()
    worktree = root / "plugin"
    result = subprocess.run(
        ["git", "-C", str(REPO_ROOT), "worktree", "add", "--detach", "-q", str(worktree), ref],
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        shutil.rmtree(root, ignore_errors=True)
        raise RuntimeError(f"could not check out {ref!r} for the baseline: {result.stderr.strip()}")
    return {"branch": REPO_ROOT, "main": worktree}


def remove_baseline(versions: dict[str, Path]) -> None:
    worktree = versions.get("main")
    if worktree is None or worktree == REPO_ROOT:
        return
    subprocess.run(["git", "-C", str(REPO_ROOT), "worktree", "remove", "--force", str(worktree)],
                   capture_output=True)
    shutil.rmtree(worktree.parent, ignore_errors=True)
```

- [ ] **Step 4: Run to see them pass**

Run: `tests/.venv/bin/python -m pytest tests/harness/tests/test_baseline.py -q`
Expected: `2 passed`.

- [ ] **Step 5: Commit**

```bash
git add tests/harness/core/baseline.py tests/harness/tests/test_baseline.py
git commit -m "feat(testing): compare this branch against a main worktree"
```

---

### Task 7: The runner — repeats, VOID limit, ladder climb

**Files:**
- Create: `tests/harness/core/runner.py`, `tests/harness/tests/test_runner.py`

**Interfaces:**
- Consumes: `Case`, `TIERS` (Task 4); `score`, `Verdict` (Task 3); `make_workdir`, `remove_workdir` (Task 5); `Event`, `Adapter` (Task 2).
- Produces:
  - `MIN_RUNS = 3`, `MAX_VOIDS = 3`
  - `RunRecord(case_id: str, version: str, tier: str, attempt: int, events: list[Event], verdict: Verdict)` dataclass with `to_dict() -> dict`
  - `CaseResult(case: Case, records: list[RunRecord], lowest_tier: str | None, void_limited: bool, max_tier: str = "high")` dataclass
  - `passes(records, version: str, tier: str) -> int`, `failures(records, version: str, tier: str) -> int`
  - `run_case(case, adapter, plugins: dict[str, Path], runs: int = 3, make=make_workdir, remove=remove_workdir, max_tier: str = "high") -> CaseResult`

Climb rule: always start at `low` (the spec: "runs a case at the `low` tier first"). At each tier, run both versions. Stop climbing at the first tier where the `branch` version has fewer than 2 failures. That tier is `lowest_tier`. If `high` still fails repeatedly, `lowest_tier` is `None`.

- [ ] **Step 1: Write the failing tests**

`tests/harness/tests/test_runner.py`:
```python
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


def test_max_tier_stops_the_climb():
    adapter = FakeAdapter({t: [Event("handoff", "Smart")] for t in ("low", "mid", "high")})
    result = run(adapter, max_tier="mid")
    assert result.lowest_tier is None
    assert {t for _, t in adapter.calls} == {"low", "mid"}
```

- [ ] **Step 2: Run to see them fail**

Run: `tests/.venv/bin/python -m pytest tests/harness/tests/test_runner.py -q`
Expected: FAIL with `ImportError`.

- [ ] **Step 3: Implement**

`tests/harness/core/runner.py`:
```python
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

    def to_dict(self) -> dict:
        return {
            "case": self.case_id, "version": self.version, "tier": self.tier,
            "attempt": self.attempt, "events": [e.to_dict() for e in self.events],
            "result": self.verdict.result, "reason": self.verdict.reason,
        }


@dataclass
class CaseResult:
    case: Case
    records: list[RunRecord] = field(default_factory=list)
    lowest_tier: str | None = None
    void_limited: bool = False
    max_tier: str = "high"


class VoidLimit(Exception):
    pass


def _count(records, version, tier, result):
    return sum(1 for r in records if r.version == version and r.tier == tier and r.verdict.result == result)


def passes(records, version: str, tier: str) -> int:
    return _count(records, version, tier, "PASS")


def failures(records, version: str, tier: str) -> int:
    return _count(records, version, tier, "FAIL")


def _run_at_tier(case, adapter, version, plugin_path, tier, runs, make, remove, records):
    valid = 0
    voids = 0
    attempt = 0
    while valid < runs:
        attempt += 1
        workdir = make(case.fixture)
        try:
            events = adapter.run(case, plugin_path, workdir, tier)
        finally:
            remove(workdir)
        verdict = score(events, case.expect)
        records.append(RunRecord(case.id, version, tier, attempt, events, verdict))
        if verdict.result == "VOID":
            voids += 1
            if voids > MAX_VOIDS:
                raise VoidLimit(f"{case.id}: {voids} refused runs on {version} at {tier}")
        else:
            valid += 1


def run_case(case: Case, adapter, plugins: dict[str, Path], runs: int = MIN_RUNS,
             make=make_workdir, remove=remove_workdir, max_tier: str = "high") -> CaseResult:
    if runs < MIN_RUNS:
        raise ValueError(f"runs must be at least {MIN_RUNS}, got {runs}")
    if max_tier not in TIERS:
        raise ValueError(f"max_tier must be one of {TIERS}, got {max_tier!r}")

    result = CaseResult(case, max_tier=max_tier)
    for tier in TIERS[: TIERS.index(max_tier) + 1]:
        try:
            for version, plugin_path in plugins.items():
                _run_at_tier(case, adapter, version, plugin_path, tier, runs, make, remove, result.records)
        except VoidLimit:
            result.void_limited = True
            return result
        if failures(result.records, "branch", tier) < REPEATED:
            result.lowest_tier = tier
            return result
    return result
```

- [ ] **Step 4: Run to see them pass**

Run: `tests/.venv/bin/python -m pytest tests/harness/tests/test_runner.py -q`
Expected: `9 passed`.

- [ ] **Step 5: Commit**

```bash
git add tests/harness/core/runner.py tests/harness/tests/test_runner.py
git commit -m "feat(testing): run cases with repeats, a VOID limit, and the ladder climb"
```

---

### Task 8: Report

**Files:**
- Create: `tests/harness/core/report.py`, `tests/harness/tests/test_report.py`

**Interfaces:**
- Consumes: `CaseResult`, `RunRecord`, `passes` (Task 7); `expected_tier`, `TIERS` (Task 4).
- Produces: `render(results: list[CaseResult], ladders: dict, runtime: str) -> str`; `write_results(out_dir: Path, results: list[CaseResult], report: str) -> None` (writes `runs.jsonl` and `report.md`).

- [ ] **Step 1: Write the failing tests**

`tests/harness/tests/test_report.py`:
```python
import json
from harness.core.cases import Case
from harness.core.events import Event
from harness.core.score import Verdict
from harness.core.runner import CaseResult, RunRecord
from harness.core.report import render, write_results

LADDERS = {"rt": {"low": "l", "mid": "m", "high": "h"}, "expected_tier": {"none": "low", "high": "mid"}}


def rec(version, tier, result, i=1, reason="r"):
    return RunRecord("c1", version, tier, i, [Event("handoff", "Smart")], Verdict(result, reason))


def case_result(records, lowest, void_limited=False):
    return CaseResult(Case("c1", "p", "Fast", "none", "advisor-mode", "todo-app"), records, lowest, void_limited)


def test_table_shows_branch_and_main_passes_per_tier():
    recs = [rec("branch", "low", "PASS", i) for i in (1, 2, 3)] + [rec("main", "low", "PASS", 1), rec("main", "low", "FAIL", 2), rec("main", "low", "PASS", 3)]
    text = render([case_result(recs, "low")], LADDERS, "rt")
    assert "| c1 | Fast | low | 3/3 | 2/3 | low | low |" in text


def test_above_expected_is_flagged():
    recs = [rec("branch", "low", "FAIL", i) for i in (1, 2, 3)] + [rec("branch", "mid", "PASS", i) for i in (1, 2, 3)]
    text = render([case_result(recs, "mid")], LADDERS, "rt")
    assert "ABOVE EXPECTED" in text


def test_no_passing_tier_and_void_limit_are_flagged():
    assert "NO PASSING TIER" in render([case_result([rec("branch", "high", "FAIL")], None)], LADDERS, "rt")
    assert "VOID LIMIT" in render([case_result([rec("branch", "low", "VOID")], None, True)], LADDERS, "rt")


def test_failed_runs_list_their_events():
    text = render([case_result([rec("branch", "low", "FAIL", reason="first handoff went to Smart")], None)], LADDERS, "rt")
    assert "first handoff went to Smart" in text and "handoff:Smart" in text


def test_write_results(tmp_path):
    write_results(tmp_path, [case_result([rec("branch", "low", "PASS")], "low")], "# report")
    lines = (tmp_path / "runs.jsonl").read_text().splitlines()
    assert json.loads(lines[0])["result"] == "PASS"
    assert (tmp_path / "report.md").read_text() == "# report"
```

- [ ] **Step 2: Run to see them fail**

Run: `tests/.venv/bin/python -m pytest tests/harness/tests/test_report.py -q`
Expected: FAIL with `ImportError`.

- [ ] **Step 3: Implement**

`tests/harness/core/report.py`:
```python
"""Turn results into report.md and runs.jsonl. Names no runtime."""
import json
from pathlib import Path

from harness.core.cases import TIERS, expected_tier
from harness.core.runner import CaseResult, passes


def _valid(records, version, tier):
    return sum(1 for r in records if r.version == version and r.tier == tier and r.verdict.result != "VOID")


def _flag(result: CaseResult, expected: str) -> str:
    if result.void_limited:
        return "VOID LIMIT"
    if result.lowest_tier is None:
        return f"NO PASSING TIER (tried up to {result.max_tier})"
    if TIERS.index(result.lowest_tier) > TIERS.index(expected):
        return "ABOVE EXPECTED"
    return ""


def render(results: list[CaseResult], ladders: dict, runtime: str) -> str:
    lines = [
        f"# Test report — {runtime}",
        "",
        "| Case | Expected role | Tier | Branch | Main | Lowest passing tier | Expected tier | Flag |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for result in results:
        expected = expected_tier(result.case, ladders)
        flag = _flag(result, expected)
        tiers_run = [t for t in TIERS if any(r.tier == t for r in result.records)]
        for tier in tiers_run:
            branch = f"{passes(result.records, 'branch', tier)}/{_valid(result.records, 'branch', tier)}"
            main = f"{passes(result.records, 'main', tier)}/{_valid(result.records, 'main', tier)}"
            lowest = result.lowest_tier or "—"
            lines.append(f"| {result.case.id} | {result.case.expect} | {tier} | {branch} | {main} | {lowest} | {expected} | {flag} |")

    lines += ["", "## Failed and void runs", ""]
    for result in results:
        for r in result.records:
            if r.verdict.result == "PASS":
                continue
            events = ", ".join(f"{e.kind}:{e.detail}" for e in r.events) or "(none)"
            lines.append(f"- **{r.case_id}** {r.version} {r.tier} #{r.attempt} — {r.verdict.result}: {r.verdict.reason}")
            lines.append(f"  - events: {events}")
    return "\n".join(lines) + "\n"


def write_results(out_dir: Path, results: list[CaseResult], report: str) -> None:
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    with open(out_dir / "runs.jsonl", "w") as f:
        for result in results:
            for r in result.records:
                f.write(json.dumps(r.to_dict()) + "\n")
    (out_dir / "report.md").write_text(report)
```

- [ ] **Step 4: Run to see them pass**

Run: `tests/.venv/bin/python -m pytest tests/harness/tests/test_report.py -q`
Expected: `5 passed`.

- [ ] **Step 5: Commit**

```bash
git add tests/harness/core/report.py tests/harness/tests/test_report.py
git commit -m "feat(testing): write the report and the raw run log"
```

---

### Task 9: The Claude Code adapter

Use the names confirmed in `docs/testing/trial-findings.md` (Task 1). Where the findings differ from the code below (tool name, option name, message field), follow the findings and note it in the commit body.

**Files:**
- Create: `tests/harness/runtimes/claude_code.py`, `tests/harness/runtimes/test_claude_code.py`
- Modify: `tests/harness/runtimes/__init__.py`

**Interfaces:**
- Consumes: `Event` (Task 2); `Case` (Task 4); `load_ladders` (Task 4).
- Produces: `ClaudeCodeAdapter(ladder: dict[str, str])` with `run(case, plugin_path, workdir, tier) -> list[Event]`; pure helpers `to_event(tool_name: str, tool_input: dict) -> Event`, `is_refusal(is_error: bool, text: str) -> bool`, `invocation(case) -> str`; in `runtimes/__init__.py`: `get_adapter(runtime: str, ladders: dict)`.

- [ ] **Step 1: Write the failing tests (pure parts only; no model is called)**

`tests/harness/runtimes/test_claude_code.py` (beside the adapter, so runtime names stay in `runtimes/`):
```python
from harness.core.cases import Case, load_ladders
from harness.runtimes import get_adapter
from harness.runtimes.claude_code import to_event, is_refusal, invocation, STOP_REASON, ClaudeCodeAdapter


def test_handoff_maps_agent_id_to_role():
    assert to_event("Agent", {"subagent_type": "maddog:executor-fast-read"}).detail == "Fast-Read"
    assert to_event("Task", {"subagent_type": "maddog:executor-lead"}).detail == "Lead"


def test_unknown_agent_becomes_other():
    e = to_event("Agent", {"subagent_type": "general-purpose"})
    assert e.kind == "handoff" and e.detail == "other:general-purpose"


def test_missing_subagent_type_becomes_other():
    assert to_event("Agent", {}).detail == "other:"


def test_tool_kinds():
    assert to_event("Edit", {"file_path": "a.py"}).kind == "write"
    assert to_event("Write", {"file_path": "a.py"}).detail == "a.py"
    assert to_event("Read", {"file_path": "a.py"}).kind == "read"
    assert to_event("Grep", {"pattern": "x"}).kind == "read"
    assert to_event("Skill", {"skill": "maddog:efficient-md"}).kind == "skill_load"
    assert to_event("Bash", {"command": "git log"}).detail == "git log"
    assert to_event("AskUserQuestion", {}).kind == "command"


def test_shell_writes_count_as_writes():
    assert to_event("Bash", {"command": "sed -i 's/add_item/create_item/g' src/todo/store.py"}).kind == "write"
    assert to_event("Bash", {"command": "echo x > notes.txt"}).kind == "write"
    assert to_event("Bash", {"command": "git checkout feature/export"}).kind == "write"
    assert to_event("Bash", {"command": "git diff main feature/export 2>/dev/null"}).kind == "command"
    assert to_event("Bash", {"command": "pytest -q 2>&1"}).kind == "command"


def test_our_own_stop_is_not_a_refusal():
    assert not is_refusal(True, STOP_REASON)
    assert is_refusal(True, "Permission to use Bash has been denied.")
    assert not is_refusal(False, "permission denied")
    assert not is_refusal(True, "No such file or directory")


def test_invocation():
    with_skill = Case("a", "do it", "Fast", "none", "advisor-mode", "todo-app")
    plain = Case("a", "do it", "Fast", "none", None, "todo-app")
    assert invocation(with_skill) == "/maddog:advisor-mode do it"
    assert invocation(plain) == "do it"


def test_registry_builds_the_adapter_with_its_ladder():
    adapter = get_adapter("claude-code", load_ladders())
    assert isinstance(adapter, ClaudeCodeAdapter)
    assert adapter.ladder["low"] == "claude-haiku-4-5-20251001"
```

- [ ] **Step 2: Run to see them fail**

Run: `tests/.venv/bin/python -m pytest tests/harness/runtimes/test_claude_code.py -q`
Expected: FAIL with `ImportError`.

- [ ] **Step 3: Implement the adapter**

`tests/harness/runtimes/claude_code.py`:
```python
"""Claude Code adapter. The only file that knows Claude Code's tools, agent IDs,
models, and SDK. Runs one case and returns its event log."""
import re
from pathlib import Path

import anyio
from claude_agent_sdk import (
    AssistantMessage, ClaudeAgentOptions, ClaudeSDKClient, HookMatcher,
    ToolResultBlock, ToolUseBlock, UserMessage,
)

from harness.core.events import Event

ROLE_TO_AGENT = {
    "Fast-Read": "maddog:executor-fast-read",
    "Fast": "maddog:executor-fast",
    "Smart": "maddog:executor-smart",
    "Judge": "maddog:executor-judge",
    "Lead": "maddog:executor-lead",
}
AGENT_TO_ROLE = {agent: role for role, agent in ROLE_TO_AGENT.items()}

HANDOFF_TOOLS = {"Agent", "Task"}
WRITE_TOOLS = {"Edit", "Write", "MultiEdit", "NotebookEdit"}
READ_TOOLS = {"Read", "Grep", "Glob", "LS", "WebFetch", "WebSearch"}
SKILL_TOOLS = {"Skill"}
WORK_START_TOOLS = {"Workflow", "RemoteTrigger", "CronCreate", "ScheduleWakeup"}  # start work outside the session
STOP_TOOLS = HANDOFF_TOOLS | WRITE_TOOLS | WORK_START_TOOLS  # the session ends at the first of these

STOP_REASON = "maddog-test: session stopped here by the test harness"
MAX_TURNS = 20           # bounds a session that never hands off
SESSION_TIMEOUT = 600    # seconds; bounds a session that stalls without taking turns

# Shell commands that change files or git state count as the advisor doing the work.
SHELL_WRITE = re.compile(
    r"\bsed\s+-i|\bperl\s+-pi|\btee\b|\bmv\b|\brm\b|\bcp\b|\btouch\b|\bmkdir\b"
    r"|\bgit\s+(commit|apply|am|checkout|switch|merge|rebase|reset|restore|add|stash|cherry-pick)\b"
    r"|>"
)
HARMLESS_REDIRECTS = re.compile(r"\d?>\s*/dev/null|\d>&\d")


def to_event(tool_name: str, tool_input: dict) -> Event:
    if tool_name in HANDOFF_TOOLS:
        agent = tool_input.get("subagent_type", "")
        return Event("handoff", AGENT_TO_ROLE.get(agent, f"other:{agent}"))
    if tool_name in WRITE_TOOLS:
        return Event("write", tool_input.get("file_path", tool_name))
    if tool_name in READ_TOOLS:
        return Event("read", tool_name)
    if tool_name in SKILL_TOOLS:
        return Event("skill_load", tool_input.get("skill", ""))
    if tool_name == "Bash":
        command = tool_input.get("command", "")
        if SHELL_WRITE.search(HARMLESS_REDIRECTS.sub("", command)):
            return Event("write", command)
        return Event("command", command)
    return Event("command", tool_name)  # any other tool counts as a non-skill call


def is_refusal(is_error: bool, text: str) -> bool:
    if not is_error or STOP_REASON in text:
        return False
    lowered = text.lower()
    return "permission" in lowered and ("denied" in lowered or "not allowed" in lowered)


def invocation(case) -> str:
    if case.skill:
        return f"/maddog:{case.skill} {case.prompt}"
    return case.prompt


def _text(content) -> str:
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return " ".join(str(part.get("text", "")) if isinstance(part, dict) else str(part) for part in content)
    return str(content or "")


async def _deny_stop_tools(input_data, tool_use_id, context):
    # Guarantees a helper never starts and no file is written, even if the
    # interrupt below arrives late.
    return {"hookSpecificOutput": {
        "hookEventName": "PreToolUse",
        "permissionDecision": "deny",
        "permissionDecisionReason": STOP_REASON,
    }}


class ClaudeCodeAdapter:
    def __init__(self, ladder: dict[str, str]):
        self.ladder = ladder

    def run(self, case, plugin_path: Path, workdir: Path, tier: str) -> list[Event]:
        return anyio.run(self._run, case, plugin_path, workdir, tier)

    async def _run(self, case, plugin_path, workdir, tier) -> list[Event]:
        events: list[Event] = []
        options = ClaudeAgentOptions(
            model=self.ladder[tier],
            cwd=str(workdir),
            plugins=[{"type": "local", "path": str(plugin_path)}],
            setting_sources=[],  # explicit isolation: no user, project, or local settings
            permission_mode="bypassPermissions",
            max_turns=MAX_TURNS,
            hooks={"PreToolUse": [HookMatcher(matcher="|".join(sorted(STOP_TOOLS)), hooks=[_deny_stop_tools])]},
        )
        # On timeout, move_on_after cancels the session and we return the events so far;
        # with no handoff among them, the run scores FAIL "no handoff".
        with anyio.move_on_after(SESSION_TIMEOUT):
            async with ClaudeSDKClient(options=options) as client:
                await client.query(invocation(case))
                async for message in client.receive_response():
                    stop_now = False
                    if isinstance(message, AssistantMessage):
                        for block in message.content:
                            if isinstance(block, ToolUseBlock):
                                events.append(to_event(block.name, dict(block.input)))
                                stop_now = stop_now or block.name in STOP_TOOLS
                    elif isinstance(message, UserMessage) and isinstance(message.content, list):
                        for block in message.content:
                            if isinstance(block, ToolResultBlock) and is_refusal(bool(block.is_error), _text(block.content)):
                                events.append(Event("refused", _text(block.content)[:120]))
                    if stop_now or (events and events[-1].kind in ("handoff", "write")):
                        await client.interrupt()
                        break
        return events
```

`tests/harness/runtimes/__init__.py`:
```python
"""Adapter registry. Adding a runtime means one entry here and one adapter file."""


def get_adapter(runtime: str, ladders: dict):
    if runtime == "claude-code":
        from harness.runtimes.claude_code import ClaudeCodeAdapter
        return ClaudeCodeAdapter(ladders["claude-code"])
    raise ValueError(f"unknown runtime {runtime!r}; known: claude-code")
```

- [ ] **Step 4: Run to see them pass**

Run: `tests/.venv/bin/python -m pytest tests/harness/runtimes/test_claude_code.py -q`
Expected: `9 passed`.

- [ ] **Step 5: Check the neutral layer names no runtime**

Run: `grep -rnE --exclude-dir=__pycache__ 'maddog:|claude|Agent\b|Edit\b|Bash|haiku|sonnet|opus' tests/run.py tests/harness/core/ tests/harness/tests/ tests/harness/conftest.py tests/skills/`
Expected: no output. (A match means a runtime identifier leaked into the neutral layer; move it into `runtimes/`. `CLAUDE.md` in `fixture.py` is uppercase and does not match. Run this again after Task 10, once `run.py` and `test_run.py` exist.)

- [ ] **Step 6: Commit**

```bash
git add tests/harness/runtimes
git commit -m "feat(testing): add the Claude Code adapter that stops at the first handoff"
```

---

### Task 10: `run.py`, the README, and the first live run

**Files:**
- Create: `tests/run.py`, `tests/README.md`, `tests/harness/tests/test_run.py`

**Interfaces:**
- Consumes: everything above.
- Produces: the command `tests/.venv/bin/python tests/run.py <target> --runtime <name> [--case ID] [--runs N]`. `--runtime` is required, so `run.py` names no runtime itself. `<target>` is a folder under `tests/` holding `handoff.yaml`, e.g. `skills/advisor-mode`.

- [ ] **Step 1: Write `run.py`**

`tests/run.py`:
```python
#!/usr/bin/env python3
"""Run model-driven tests.

    tests/.venv/bin/python tests/run.py skills/advisor-mode --runtime <name>
    tests/.venv/bin/python tests/run.py skills/advisor-mode --runtime <name> --case ci-flake
"""
import argparse
import sys
from datetime import datetime
from pathlib import Path

from harness.core.baseline import plugin_versions, remove_baseline
from harness.core.cases import TESTS_DIR, load_cases, load_ladders
from harness.core.report import render, write_results
from harness.core.runner import MIN_RUNS, run_case
from harness.runtimes import get_adapter


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("target", help="folder under tests/ holding handoff.yaml, e.g. skills/advisor-mode")
    parser.add_argument("--runtime", required=True, help="a runtime listed in harness/runtimes/ladders.yaml")
    parser.add_argument("--case", help="run only this case id")
    parser.add_argument("--runs", type=int, default=MIN_RUNS)
    args = parser.parse_args(argv)

    case_file = TESTS_DIR / args.target / "handoff.yaml"
    cases = load_cases(case_file)
    if args.case:
        cases = [c for c in cases if c.id == args.case]
        if not cases:
            parser.error(f"no case {args.case!r} in {case_file}")

    ladders = load_ladders()
    adapter = get_adapter(args.runtime, ladders)
    plugins = plugin_versions("main")
    results = []
    try:
        for case in cases:
            print(f"running {case.id} (expect {case.expect})", flush=True)
            results.append(run_case(case, adapter, plugins, runs=args.runs, max_tier=ladders.get("max_tier", "high")))
    finally:
        remove_baseline(plugins)

    report = render(results, ladders, args.runtime)
    out_dir = TESTS_DIR / "results" / datetime.now().strftime("%Y-%m-%dT%H%M%S")
    write_results(out_dir, results, report)
    print(report)
    print(f"results: {out_dir}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 2: Test that a crash still removes the `main` worktree**

`tests/harness/tests/test_run.py`:
```python
import subprocess

import pytest
import run
from harness.core.cases import TESTS_DIR


def test_main_worktree_is_removed_when_a_case_crashes(monkeypatch):
    monkeypatch.setattr(run, "get_adapter", lambda runtime, ladders: object())

    def crash(*args, **kwargs):
        raise RuntimeError("adapter died")

    monkeypatch.setattr(run, "run_case", crash)
    with pytest.raises(RuntimeError, match="adapter died"):
        run.main(["skills/advisor-mode", "--runtime", "rt", "--case", "list-flags"])
    listing = subprocess.run(["git", "-C", str(TESTS_DIR.parent), "worktree", "list"],
                             capture_output=True, text=True).stdout
    assert "maddog-baseline-" not in listing
```

Run: `tests/.venv/bin/python -m pytest tests/harness/tests/test_run.py -q`
Expected: `1 passed`.

- [ ] **Step 3: Check the argument errors without calling a model**

Run: `tests/.venv/bin/python tests/run.py skills/advisor-mode --runtime claude-code --runs 2 --case list-flags; echo "exit $?"`
Expected: a traceback ending in `ValueError: runs must be at least 3, got 2`, and a non-zero exit. Then run `git worktree list` and confirm no `maddog-baseline-` worktree is left behind (the `finally` removed it).

Run: `tests/.venv/bin/python tests/run.py skills/advisor-mode --runtime claude-code --case nope`
Expected: `error: no case 'nope' in …/handoff.yaml`.

- [ ] **Step 4: Write `tests/README.md`**

```markdown
# tests/

Model-driven tests for this repo. Design: `docs/testing/spec.md`.

## Set up once

    python3 -m venv tests/.venv
    tests/.venv/bin/pip install -r tests/requirements.txt

## Run

    tests/.venv/bin/python tests/run.py skills/advisor-mode --runtime claude-code
    tests/.venv/bin/python tests/run.py skills/advisor-mode --runtime claude-code --case ci-flake

Each case runs 3 times on this working tree and 3 times on `main`, starting at
the `low` tier. A case that fails at least 2 of 3 climbs to the next tier, up to `max_tier` in `harness/runtimes/ladders.yaml` (currently `mid`).
Every run calls a real model and costs tokens. Runs use your existing Claude
Code login unless `ANTHROPIC_API_KEY` is set, in which case they bill that key.

Harness unit tests (no model):

    tests/.venv/bin/python -m pytest tests/harness -q

## Read a report

`tests/results/<time>/report.md` has one row per case per tier:

- **Branch / Main**: passes out of valid runs on this working tree and on `main`.
- **Lowest passing tier** vs **Expected tier**: the flag `ABOVE EXPECTED` means
  you decide: edit the skill once and rerun all cases, or give the case an
  `expected_tier` with a `why` in its `handoff.yaml`. Never change a case's
  `pressure` after its first run.
- `NO PASSING TIER (tried up to mid)`: the case never passed at any tier up to `mid`; `high` was not tried. With `max_tier: high`, this flag means a real routing defect.
- `VOID LIMIT`: commands kept being refused; the environment is broken, not the skill.

Below the table, every failed or void run lists its events in order.

## Add a case

Add an entry to the folder's `handoff.yaml`: `id`, `prompt`, `expect` (one of
Fast-Read, Fast, Smart, Judge, Lead), `pressure` (`none` or `high`). Set
pressure before the first run. Optional: `expected_tier` plus `why`, only when
a report showed the case needs a higher tier and you accepted that.

## Layout

- `harness/core/`: names no runtime. Cases, fixtures, baseline, runner, scoring, report.
- `harness/runtimes/`: the only place runtime details live. One adapter per runtime, plus `ladders.yaml`.
- `fixtures/`: practice repos, copied to a temp folder outside this repo per run.
- `skills/`, `agents/`, `scripts/`: case files, mirroring the repo's own folders.
```

- [ ] **Step 5: Run the full unit suite and the neutrality check**

Run: `tests/.venv/bin/python -m pytest tests/harness -q`
Expected: `51 passed` (events 3 + score 9 + cases 9 + fixture 4 + baseline 2 + runner 9 + report 5 + run 1 + adapter 9), 0 failed.

Run: `grep -rnE --exclude-dir=__pycache__ 'maddog:|claude|Agent\b|Edit\b|Bash|haiku|sonnet|opus' tests/run.py tests/harness/core/ tests/harness/tests/ tests/harness/conftest.py tests/skills/`
Expected: no output.

- [ ] **Step 6: First live run — one case**

Run: `tests/.venv/bin/python tests/run.py skills/advisor-mode --runtime claude-code --case rename-add-item`
Expected: finishes; prints a report with rows for `rename-add-item`; `results/<time>/runs.jsonl` holds at least 6 lines. Then check by hand:
1. Open `runs.jsonl`. For 2 runs, check that the events match what a session would plausibly do (a `skill_load`, maybe one `read`, then a `handoff`), and that the verdict follows the scoring rules.
2. `git worktree list` shows no leftover baseline worktree; `ls "$TMPDIR" | grep maddog-test-` shows no leftover fixture folders.
3. Check a session that never hands off ends: any `no handoff` FAIL must have finished within the 600-second timeout, not hung.
4. Count VOID runs. If any, read their `refused` detail: a refusal in an isolated session means the adapter's permission setup is wrong. **Stop and report** rather than proceeding.

- [ ] **Step 7: Full live run**

Run: `tests/.venv/bin/python tests/run.py skills/advisor-mode --runtime claude-code`
Expected: a report with all five cases. Do not change any case, skill, or scoring rule based on the result: report it to the maintainer, who decides per the spec's escalation loop.

- [ ] **Step 8: Commit**

```bash
git add tests/run.py tests/README.md tests/harness/tests/test_run.py
git commit -m "feat(testing): add the run command and the tests README"
```

---

### Task 11: Doc edits from the spec

**Files:**
- Modify: `CLAUDE.md` (opening lines and Invariants), `CONTRIBUTING.md` (§Validation), `README.md` (§Contributing; README has no layout section, so `tests/` is named here instead)

- [ ] **Step 1: Confirm the CLAUDE.md text with the maintainer**

The maintainer's rule: no CLAUDE.md edit without explicit approval of the verbatim text. Show them all three CLAUDE.md changes in Step 2, plus the new CONTRIBUTING.md §Validation text from Step 3 (CLAUDE.md points to it as the validation rule), and wait for a yes. Do not apply them on the strength of the spec approval alone.

- [ ] **Step 2: Apply the CLAUDE.md edits (after the yes)**

First, the opening lines. The build makes "there is no test suite" false. Replace:
```text
Layout and routing: `README.md`. How a change is validated — there is no
test suite and nothing compiles: `CONTRIBUTING.md` §Validation.
```
with:
```text
Layout and routing: `README.md`. How a change is validated — nothing
compiles; model-driven tests live in `tests/`: `CONTRIBUTING.md` §Validation.
```

Second, in Invariants, replace:
```text
- Adapter set — the only paths where runtime mechanics may live: agent and
  skill frontmatter, `hooks/`, `scripts/`, `workflows/`, `.github/`,
  `.claude/`, `.claude-plugin/`. Shipped bodies (`agents/*.md`, `skills/**`)
```
with:
```text
- Adapter set — the only paths where runtime mechanics may live: agent and
  skill frontmatter, `hooks/`, `scripts/`, `workflows/`, `tests/`, `.github/`,
  `.claude/`, `.claude-plugin/`. Within `tests/`, only code under
  `tests/harness/runtimes/` names runtime identifiers; `tests/README.md` and
  `tests/requirements.txt` may name the runtime they document. Shipped bodies (`agents/*.md`, `skills/**`)
```
and add as the last Invariants bullet:
```text
- Model-driven tests score from recorded tool calls, never a model's words or
  a grading model. `tests/harness/` enforces isolation, voided runs, and the
  main-branch baseline: change the harness, never bypass it.
```

- [ ] **Step 3: Replace CONTRIBUTING.md §Validation**

Replace everything from the heading `## Validation — there is no test suite` down to and including the **Agent/skill description change** bullet. That span is the heading, the first paragraph, the **Agent body change** bullet, and the **Agent/skill description change** bullet. Replace it with:
```markdown
## Validation

Instruction text has no compiler, so a change is validated by exercising it.
Model-driven tests live in `tests/` (see `tests/README.md` and
`docs/testing/spec.md`):

- **Advisor-mode routing change** (the Classify table, or anything the advisor
  reads before its first handoff) → run
  `tests/.venv/bin/python tests/run.py skills/advisor-mode --runtime claude-code` and compare the
  branch and main columns.
- **Agent body change** → dispatch that agent on a representative task and
  confirm it follows the new instruction, rather than assuming it will.
- **Agent/skill description change** → until `tests/agents/` exists, run
  fresh-session probes: one task the new description should win and one it
  should lose.
```
Keep the existing **Workflow change** bullet and the closing line unchanged.

- [ ] **Step 4: Update README.md §Contributing**

Replace "the no-test-suite validation model" with "the validation model and the model-driven tests in `tests/`".

- [ ] **Step 5: Verify**

Run: `grep -n "tests/" CLAUDE.md CONTRIBUTING.md README.md`
Expected: the new lines appear. Then `grep -n "no test suite\|no-test-suite" CLAUDE.md CONTRIBUTING.md README.md` prints nothing, and `grep -c "Agent body change" CONTRIBUTING.md` prints `1`.

- [ ] **Step 6: Commit**

```bash
git add CLAUDE.md CONTRIBUTING.md README.md
git commit -m "docs(testing): point validation at tests/ and add tests/ to the adapter set"
```
