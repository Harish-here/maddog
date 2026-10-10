"""Score one agent-mode run with four checks. Pure logic; names no runtime.

    1  the text `PATTERNS:` is in the agent's own text before its first tool call
    2  the line holding it names every pattern the case expects (it may name more)
    3  the first tool call is the kind the case expects, on the target it expects
    4  the law check: the case's own conditions on edits, call order, the command
       run, and the quotes and label in the return

PASS means all four. The run's verdict keeps each check's result, so a report
can show which one failed.

Two limits, by design. Check 2 is a superset test: naming every pattern passes
it, so checks 3 and 4 are what catch a wrong classification. Check 3 is strict:
a first call that is not the case's kind on its target (a directory listing, or
a search by file name, before the search the case expects) fails it, as the
design locks.

The check 1 rule is the user-locked hook rule, and scripts/pattern-declare-guard.sh
applies the same one: the text `PATTERNS:` appears in the agent's own text, in any
position, with any markup around it. Check 2 then reads the pattern names from the
line that holds it.

Setup steps are not scored. A step that only changes directory or sets up the
shell (`cd <dir>`, `pushd`, `popd`, `pwd`, `export X=1`, `X=1`, `set -e`, `unset X`),
a bare `echo` with no redirect (`echo "--- ls var ---"`), or exactly
`git rev-parse --show-toplevel` is kept in the event log but skipped when choosing the first call (check 3) and when
matching `before`, `then` and `command_runs`, so `cd /w && python3 -m unittest t`
is scored as the test run it is. A lone `cd` followed by an edit still fails check 3.

A shell call arrives here already split into one event per step (core/shell.py),
so `before`, `then` and `command_runs` see the order of the steps, not of the
calls.

Matching a model's own words is allowed here only for the `PATTERNS:` line and,
for the read-only agent, its quotes and labels (user waiver, 2026-10-08). The
loader rejects those keys in a case for any other agent. Nothing here asks a
model to grade anything."""
import re

from harness.core.cases import CALL_KINDS, AgentCase
from harness.core.events import Event
from harness.core.score import Verdict
from harness.core.shell import first_in_pipeline

CHECK_NAMES = {"1": "PATTERNS line before the first call", "2": "declared patterns",
               "3": "first call", "4": "law check"}
PATTERNS_LINE = re.compile(r"^.*?PATTERNS:[ \t]*(.*)$", re.MULTILINE)  # the line holding the marker; the rest of it is the names
SETUP_STEP = re.compile(r"^(cd|pushd|popd|pwd)(\s|$)|^set\s+[-+]|^(export|unset)\s+\w+|^\w+=\S*$"
                        r"|^echo(\s|$)(?![^\n]*[>|])|^git rev-parse --show-toplevel$")  # echo: no redirect or pipe
# A model may wrap a field name in markdown (`**RESULT:**`, `## RESULT:`, `- RESULT:`); it is still the field.
MARK = r"[ \t>#*_`-]*"
RESULT_FIELD = re.compile(rf"^{MARK}RESULT[ \t]*:[*_` \t]*(.*?)(?=^{MARK}NOT DONE[ \t]*:|\Z)", re.MULTILINE | re.DOTALL)
LABEL = re.compile(r"CONFIRMED|CONTRADICTED|NO EVIDENCE")


def score_agent(events: list[Event], case: AgentCase) -> Verdict:
    refused = next((e for e in events if e.kind == "refused"), None)
    if refused is not None:
        return Verdict("VOID", f"a command was refused: {refused.detail}")

    all_calls = [e for e in events if e.kind in CALL_KINDS]
    calls = [e for e in all_calls if not is_setup_step(e)]  # what checks 3 and 4 look at
    first_call_at = next((i for i, e in enumerate(events) if e.kind in CALL_KINDS), len(events))
    said_before_first_call = [e.detail for e in events[:first_call_at] if e.kind == "say"]

    problems: dict[str, str] = {}  # check number -> why it failed
    declared = declared_patterns(said_before_first_call)
    if declared is None:
        problems["1"] = "no PATTERNS: line before the first tool call"
    missing = [p for p in case.patterns if p not in (declared or [])]
    if missing:
        problems["2"] = f"declared {sorted(declared or [])}, missing {missing}"
    why = first_call_problem(calls, case.first_call)
    if why:
        problems["3"] = why
    law = law_problems(events, calls, case.checks)
    if law:
        problems["4"] = "; ".join(law)

    checks = {key: key not in problems for key in CHECK_NAMES}
    if not problems:
        return Verdict("PASS", "all four checks passed", checks)
    reason = "; ".join(f"check {key} ({CHECK_NAMES[key]}): {why}" for key, why in problems.items())
    return Verdict("FAIL", reason, checks)


def is_setup_step(event: Event) -> bool:
    """A shell step that only changes directory or sets up the shell: not scored."""
    return event.kind == "command" and SETUP_STEP.match(event.detail.strip()) is not None


def declared_patterns(texts: list[str]) -> list[str] | None:
    """The pattern names on the first line holding `PATTERNS:` in these texts; None if no text holds it."""
    for text in texts:
        match = PATTERNS_LINE.search(text)
        if match:
            return re.findall(r"[A-Z]{2,}", match.group(1))
    return None


def short(text: str, limit: int = 90) -> str:
    return text if len(text) <= limit else text[:limit] + "..."


def first_call_problem(calls: list[Event], spec: dict) -> str | None:
    if not calls:
        return "no tool call"
    first = calls[0]
    if first.kind not in spec["kind"]:
        return f"first call was {first.kind}:{short(first.detail)}, expected kind {'/'.join(spec['kind'])}"
    if not re.search(spec["target"], first.detail):
        return f"first call {first.kind}:{short(first.detail)} does not match /{spec['target']}/"
    return None


def first_index(rendered: list[str], pattern: str) -> int | None:
    return next((i for i, text in enumerate(rendered) if re.search(pattern, text)), None)


def last_index(rendered: list[str], pattern: str) -> int | None:
    return next((i for i in range(len(rendered) - 1, -1, -1) if re.search(pattern, rendered[i])), None)


def normalize_command(command: str) -> str:
    """A step as run: leading `VAR=value` assignments and a trailing `2>&1` are dropped, and a
    pipeline counts as its head command."""
    head = re.sub(r"^(\w+=\S*\s+)+", "", first_in_pipeline(command.strip()))
    return re.sub(r"\s*2>&1$", "", head).strip()


def final_text(events: list[Event]) -> str:
    return next((e.detail for e in reversed(events) if e.kind == "final"), "")


def result_field(text: str) -> str:
    match = RESULT_FIELD.search(text)
    return match.group(1) if match else ""


def law_problems(events: list[Event], calls: list[Event], checks: dict) -> list[str]:
    problems = []
    changed = [e.detail for e in events if e.kind == "changed"]
    rendered = [f"{e.kind}:{e.detail}" for e in calls]  # what `before` and `then` patterns match
    text = final_text(events)
    result = result_field(text)

    for path in checks.get("edits_include", []):
        if path not in changed:
            problems.append(f"{path} was not edited")
    for path in checks.get("edits_exclude", []):
        if path in changed:
            problems.append(f"{path} was edited")
    if checks.get("no_edits") and changed:
        problems.append("files changed: " + ", ".join(changed))

    for earlier, later in checks.get("before", []):  # first match of each: earlier must come first
        a, b = first_index(rendered, earlier), first_index(rendered, later)
        if a is None or b is None:
            problems.append(f"no call matches /{earlier if a is None else later}/")
        elif a >= b:
            problems.append(f"/{earlier}/ did not come before /{later}/")
    for earlier, later in checks.get("then", []):  # last match of each: the later one must come last
        a, b = last_index(rendered, earlier), last_index(rendered, later)
        if a is None or b is None:
            problems.append(f"no call matches /{earlier if a is None else later}/")
        elif a >= b:
            problems.append(f"the last /{earlier}/ did not come before the last /{later}/")

    command = checks.get("command_runs")
    if command and not any(normalize_command(e.detail) == command for e in calls if e.kind in ("command", "write")):
        problems.append(f"command not run exactly as given: {command}")

    for quote in checks.get("return_quotes", []):
        if quote not in text:
            problems.append(f"return lacks: {quote}")
    for quote in checks.get("return_lacks", []):
        if quote in result:
            problems.append(f"RESULT holds a line it should not: {quote}")
    label = checks.get("label")
    if label and set(LABEL.findall(result)) != {label}:
        problems.append(f"RESULT labels are {sorted(set(LABEL.findall(result)))}, expected only {label}")
    return problems
