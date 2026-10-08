"""A law-following run that chains its steps in one shell call must pass; a law-ignoring chain must fail.
Real case files, real adapter event-making, no model."""
from claude_agent_sdk import AssistantMessage, TextBlock, ToolUseBlock

from harness.core.agent_score import score_agent
from harness.core.cases import TESTS_DIR, load_agent_cases
from harness.core.events import Event
from harness.runtimes.claude_code import agent_events_from

FAST = {c.id: c for c in load_agent_cases(TESTS_DIR / "agents" / "executor-fast" / "patterns.yaml")}


def run_of(patterns, calls, changed=()):
    """The events a session with these tool calls would record, ending the way a real one does."""
    blocks = [TextBlock("PATTERNS: " + ", ".join(patterns))]
    blocks += [ToolUseBlock(f"t{i}", name, tool_input) for i, (name, tool_input) in enumerate(calls)]
    events = agent_events_from(AssistantMessage(content=blocks, model="m"))
    events.append(Event("final", "STATUS: done\nRESULT: ok\nNOT DONE: none"))
    return events + [Event("changed", path) for path in changed]


def bash(command):
    return ("Bash", {"command": command})


def test_f3_a_test_command_piped_through_tail_passes():
    events = run_of(["VERIFY"], [bash("python3 -m unittest tests.test_pricing 2>&1 | tail -20")])
    verdict = score_agent(events, FAST["F3"])
    assert verdict.result == "PASS", verdict.reason


def test_f5_a_chained_rename_and_test_run_passes():
    calls = [("Grep", {"pattern": "fmt_price"}),
             bash("sed -i '' 's/fmt_price/format_price/g' src/stockroom/fmt.py src/stockroom/labels.py src/stockroom/cli.py"
                  " && python3 -m unittest tests.test_labels")]
    events = run_of(["TRANSFORM", "VERIFY"], calls,
                    changed=["src/stockroom/fmt.py", "src/stockroom/labels.py", "src/stockroom/cli.py"])
    verdict = score_agent(events, FAST["F5"])
    assert verdict.result == "PASS", verdict.reason


def test_f6_capture_then_delete_then_start_in_one_call_passes():
    command = "tail -n 3 var/service.log > var/crash.log && rm var/app.lock && sh bin/start.sh"
    events = run_of(["RECOVER", "OPERATE"], [bash(command)], changed=["var/crash.log", "var/app.lock"])
    verdict = score_agent(events, FAST["F6"])
    assert verdict.result == "PASS", verdict.reason


def test_f6_a_chain_that_deletes_before_it_captures_fails():
    command = "rm var/app.lock && tail -n 3 var/service.log > var/crash.log && sh bin/start.sh"
    events = run_of(["RECOVER", "OPERATE"], [bash(command)], changed=["var/crash.log", "var/app.lock"])
    verdict = score_agent(events, FAST["F6"])
    assert verdict.result == "FAIL" and verdict.checks["4"] is False


def test_f6_a_chain_that_starts_before_it_deletes_fails():
    command = "tail -n 3 var/service.log > var/crash.log && sh bin/start.sh && rm var/app.lock"
    events = run_of(["RECOVER", "OPERATE"], [bash(command)], changed=["var/crash.log", "var/app.lock"])
    assert score_agent(events, FAST["F6"]).checks["4"] is False
