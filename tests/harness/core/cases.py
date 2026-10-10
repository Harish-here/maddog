"""Load case files and the ladder config. Names no runtime."""
import re
from dataclasses import dataclass
from pathlib import Path

import yaml

ROLES = ("Fast-Read", "Fast", "Smart", "Judge", "Lead")
TIERS = ("low", "mid", "high")
PRESSURES = ("none", "user", "decision")

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
    file_tier = data.get("expected_tier")
    file_why = data.get("why")
    if file_tier is not None and file_tier not in TIERS:
        raise ValueError(f"{path}: unknown tier {file_tier!r}")
    if file_tier is not None and not file_why:
        raise ValueError(f"{path}: expected_tier needs a 'why'")
    if file_why and not file_tier:
        raise ValueError(f"{path}: 'why' needs an 'expected_tier'")
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
        if tier is None:
            # No case-level override: inherit the file-level pair, if any.
            tier, why = file_tier, file_why
        cases.append(Case(raw["id"], raw["prompt"], raw["expect"], raw["pressure"], skill, fixture, tier, why))
    if not cases:
        raise ValueError(f"{path}: no cases")
    return cases


# --- agent cases: an agent file run as the main session, scored by four checks ---

AGENT_ROLES = ("Fast", "Fast-Read")  # the executors whose declared patterns these cases test
PATTERN_NAMES = ("CHANGE", "OPERATE", "TRANSFORM", "RECOVER", "VERIFY", "REPRODUCE", "SWEEP", "TRACE", "EXTRACT")
CALL_KINDS = ("read", "write", "command")
LABELS = ("CONFIRMED", "CONTRADICTED", "NO EVIDENCE")
# Keys a case may use for check 4 (the law check). Anything else is a typo.
CHECK_KEYS = ("edits_include", "edits_exclude", "no_edits", "before", "then",
              "command_runs", "return_quotes", "return_lacks", "label")
CASE_KEYS = ("id", "prompt", "patterns", "first_call")
# Check keys that read the agent's returned words. Only Fast-Read's quotes and labels are waived.
WORDS_KEYS = ("return_quotes", "return_lacks", "label")


@dataclass(frozen=True)
class AgentCase:
    id: str
    prompt: str
    expect: str        # the role under test, Fast or Fast-Read; the adapter maps it to the agent file
    fixture: str
    patterns: tuple    # the pattern names the work holds: check 2 wants all of them declared
    first_call: dict   # {"kind": [..], "target": regex}: check 3
    checks: dict       # check 4: only keys from CHECK_KEYS


def _regex(where: str, text) -> str:
    if not isinstance(text, str):
        raise ValueError(f"{where}: expected a regex string, got {text!r}")
    try:
        re.compile(text)
    except re.error as e:
        raise ValueError(f"{where}: bad regex {text!r}: {e}") from None
    return text


def load_agent_cases(path: Path) -> list[AgentCase]:
    data = yaml.safe_load(Path(path).read_text())
    expect, fixture = data.get("expect"), data.get("fixture")
    if expect not in AGENT_ROLES:
        raise ValueError(f"{path}: 'expect' must be one of {', '.join(AGENT_ROLES)}, got {expect!r}")
    if not fixture:
        raise ValueError(f"{path}: missing 'fixture'")

    cases, seen = [], set()
    for raw in data.get("cases", []):
        for field in CASE_KEYS:
            if field not in raw:
                raise ValueError(f"{path}: a case is missing '{field}'")
        cid = raw["id"]
        if cid in seen:
            raise ValueError(f"{path}: duplicate case id {cid!r}")
        seen.add(cid)
        unknown_patterns = [p for p in raw["patterns"] if p not in PATTERN_NAMES]
        if not raw["patterns"] or unknown_patterns:
            raise ValueError(f"{path}: case {cid}: patterns must be a non-empty list from {PATTERN_NAMES}, got {raw['patterns']!r}")

        first_call = dict(raw["first_call"])
        kinds = first_call.get("kind")
        kinds = [kinds] if isinstance(kinds, str) else list(kinds or [])
        if not kinds or any(k not in CALL_KINDS for k in kinds):
            raise ValueError(f"{path}: case {cid}: first_call.kind must be from {CALL_KINDS}, got {first_call.get('kind')!r}")
        first_call = {"kind": kinds, "target": _regex(f"{path}: case {cid}: first_call.target", first_call.get("target"))}

        checks = {k: v for k, v in raw.items() if k not in CASE_KEYS}
        unknown = sorted(set(checks) - set(CHECK_KEYS))
        if unknown:
            raise ValueError(f"{path}: case {cid}: unknown check key(s) {', '.join(unknown)}; known: {', '.join(CHECK_KEYS)}")
        words = sorted(set(checks) & set(WORDS_KEYS))
        if words and expect != "Fast-Read":
            raise ValueError(f"{path}: case {cid}: {', '.join(words)} score a model's words; the waiver "
                             f"(2026-10-08) allows that for Fast-Read's quotes and labels only")
        for key in ("before", "then"):
            for pair in checks.get(key, []):
                if len(pair) != 2:
                    raise ValueError(f"{path}: case {cid}: every {key} entry is a pair [earlier, later], got {pair!r}")
                for part in pair:
                    _regex(f"{path}: case {cid}: {key}", part)
        if "command_runs" in checks and not isinstance(checks["command_runs"], str):
            raise ValueError(f"{path}: case {cid}: command_runs is one command string")
        if "label" in checks and checks["label"] not in LABELS:
            raise ValueError(f"{path}: case {cid}: label must be one of {LABELS}")

        cases.append(AgentCase(cid, raw["prompt"], expect, fixture, tuple(raw["patterns"]), first_call, checks))
    if not cases:
        raise ValueError(f"{path}: no cases")
    return cases


def load_ladders(path: Path = LADDERS_FILE) -> dict:
    return yaml.safe_load(Path(path).read_text())


def expected_tier(case: Case | AgentCase, ladders: dict) -> str:
    if isinstance(case, AgentCase):
        return TIERS[0]  # agent cases carry no pressure and always run at the low tier
    if case.expected_tier:
        return case.expected_tier
    return ladders["expected_tier"][case.pressure]
