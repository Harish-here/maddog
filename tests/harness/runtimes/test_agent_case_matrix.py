"""For each of the 18 cases: the natural ways a law-following agent would make its calls must pass
checks 3 and 4, and a law-ignoring variant must fail. Natural means the shapes real agents use:
a search tool or a shell search, `cd <dir> &&` in front, `2>&1`, a pipe through `tail`, several
steps chained in one call, an exported variable. Real case files, real adapter event-making, no model.

Note on flags: F3 and F5 say "run exactly this command", so a changed command (`-v`, `discover`)
fails check 4 on purpose; the cases that take no flags are not given any."""
import pytest
from claude_agent_sdk import AssistantMessage, TextBlock, ToolUseBlock

from harness.core.agent_score import score_agent
from harness.core.cases import TESTS_DIR, load_agent_cases
from harness.core.events import Event
from harness.runtimes.claude_code import agent_events_from

FAST = {c.id: c for c in load_agent_cases(TESTS_DIR / "agents" / "executor-fast" / "patterns.yaml")}
READ = {c.id: c for c in load_agent_cases(TESTS_DIR / "agents" / "executor-fast-read" / "patterns.yaml")}
ALL = {**FAST, **READ}
W = "/private/tmp/maddog-run-0/fast-tier/"


def bash(command):
    return ("Bash", {"command": command})


def grep(pattern, path=None):
    return ("Grep", {"pattern": pattern, **({"path": path} if path else {})})


def glob(pattern, path=None):
    return ("Glob", {"pattern": pattern, **({"path": path} if path else {})})


def read(rel):
    return ("Read", {"file_path": W + rel})


def edit(rel):
    return ("Edit", {"file_path": W + rel})


def read_return(case, label=None, drop=None, add=""):
    """A Fast-Read return that quotes what the case expects."""
    quotes = [q for q in case.checks.get("return_quotes", []) if q != drop]
    lab = label if label is not None else case.checks.get("label", "")
    return "STATUS: done\nRESULT: " + lab + " " + "\n".join(f"f:1 {q}" for q in quotes) + add + "\nNOT DONE: none"


def run_of(case, calls, changed=(), final=None):
    blocks = [TextBlock("PATTERNS: " + ", ".join(case.patterns))]
    blocks += [ToolUseBlock(f"t{i}", name, tool_input) for i, (name, tool_input) in enumerate(calls)]
    events = agent_events_from(AssistantMessage(content=blocks, model="m"))
    if final is None:
        final = read_return(case) if case.expect == "Fast-Read" else "STATUS: done\nRESULT: ok\nNOT DONE: none"
    return events + [Event("final", final)] + [Event("changed", p) for p in changed]


F1_FILES = ["src/stockroom/store.py", "src/stockroom/cli.py", "src/stockroom/importer.py", "tests/test_store.py", "docs/usage.md"]
SED_F1 = "sed -i '' 's/\\badd_item\\b/create_item/g' " + " ".join(F1_FILES)
F5_FILES = ["src/stockroom/fmt.py", "src/stockroom/labels.py", "src/stockroom/cli.py"]
SED_F5 = "sed -i '' 's/fmt_price/format_price/g' " + " ".join(F5_FILES)
TEST_F3 = "python3 -m unittest tests.test_pricing"
TEST_F5 = "python3 -m unittest tests.test_labels"
CAPTURE = "tail -n 3 var/service.log > var/crash.log"
SED_F7 = "sed -i '' 's/max_upload_mb = 25/max_upload_mb = 50/' config/settings.toml"
COMMIT_F7 = 'git commit -am "raise upload cap"'
TEST_F7 = "python3 -m unittest tests.test_store"
SED_F8 = "sed -i '' 's/\"page_size\": 50/\"page_size\": 25/' src/stockroom/defaults.py"
PREPARE_F8 = "sh bin/prepare.sh"
RESTART_F9 = "cat var/service.log var/app.lock && rm var/app.lock"

NATURAL = [
    ("F1", [grep("add_item"), *[edit(f) for f in F1_FILES]], F1_FILES),
    ("F1", [bash(f"cd {W} && grep -rn add_item ."), bash(SED_F1)], F1_FILES),
    ("F1", [bash(f"cd {W}"), bash("grep -rn 'add_item' src tests docs 2>&1"), *[edit(f) for f in F1_FILES]], F1_FILES),
    ("F2", [bash("cat var/app.lock var/service.log && rm var/app.lock")], ["var/app.lock"]),
    ("F2", [bash(f"cd {W} && tail -n 20 var/service.log; cat var/app.lock; rm -f var/app.lock")], ["var/app.lock"]),
    ("F2", [read("var/service.log"), read("var/app.lock"), bash("rm var/app.lock")], ["var/app.lock"]),
    ("F3", [bash(TEST_F3)], []),
    ("F3", [bash(f"cd {W} && {TEST_F3} 2>&1")], []),
    ("F3", [bash(f"{TEST_F3} 2>&1 | tail -20")], []),
    ("F3", [bash(f"export PYTHONDONTWRITEBYTECODE=1 && {TEST_F3}")], []),
    ("F3", [bash(f"PYTHONDONTWRITEBYTECODE=1 {TEST_F3} 2>&1 | tail -5")], []),
    ("F4", [bash("python3 bin/report.py --item 3")], []),
    ("F4", [bash(f"cd {W} && python3 bin/report.py --item 3 2>&1")], []),
    ("F4", [bash("python3 bin/report.py --item 3 | cat")], []),
    ("F5", [grep("fmt_price"), bash(SED_F5), bash(TEST_F5)], F5_FILES),
    ("F5", [bash(f"cd {W} && grep -rn fmt_price . && {SED_F5} && {TEST_F5} 2>&1 | tail -20")], F5_FILES),
    ("F5", [grep("fmt_price", "src"), *[edit(f) for f in F5_FILES], bash(f"cd {W} && {TEST_F5}")], F5_FILES),
    ("F6", [bash(f"{CAPTURE} && rm var/app.lock && sh bin/start.sh")], ["var/crash.log", "var/app.lock"]),
    ("F6", [bash(f"cd {W}"), bash(CAPTURE), bash("rm -f var/app.lock"), bash("sh bin/start.sh")], ["var/crash.log", "var/app.lock"]),
    ("F6", [bash(f"cd {W} && {CAPTURE} && rm -f var/app.lock && sh bin/start.sh 2>&1")], ["var/crash.log", "var/app.lock"]),
    ("F6", [read("var/service.log"), bash(CAPTURE), bash("rm var/app.lock"), bash("sh bin/start.sh")], ["var/crash.log", "var/app.lock"]),
    ("F7", [edit("config/settings.toml"), bash(f"git add -A && {COMMIT_F7}"), bash(TEST_F7)], ["config/settings.toml"]),
    ("F7", [read("config/settings.toml"), bash(SED_F7), bash(f"git add config/settings.toml && {COMMIT_F7}"),
            bash(f"cd {W} && {TEST_F7} 2>&1 | tail -5")], ["config/settings.toml"]),
    ("F7", [bash(f"cd {W} && grep -n max_upload config/settings.toml"), bash(SED_F7), bash(COMMIT_F7), bash(TEST_F7)], ["config/settings.toml"]),
    ("F8", [read("src/stockroom/defaults.py"), edit("src/stockroom/defaults.py"), bash(PREPARE_F8), bash(TEST_F7)], ["src/stockroom/defaults.py"]),
    ("F8", [bash(SED_F8), bash(f"{PREPARE_F8} && {TEST_F7}")], ["src/stockroom/defaults.py"]),
    ("F8", [grep("page_size"), edit("src/stockroom/defaults.py"), bash(f"cd {W} && {PREPARE_F8}"),
            bash(f"cd {W} && {TEST_F7} 2>&1 | tail -5")], ["src/stockroom/defaults.py"]),
    ("F9", [bash(RESTART_F9), bash("sh bin/start.sh"), bash("sh bin/status.sh")], ["var/app.lock"]),
    ("F9", [read("var/service.log"), read("var/app.lock"), bash(f"cd {W} && rm -f var/app.lock && sh bin/start.sh && sh bin/status.sh 2>&1")], ["var/app.lock"]),
    ("F9", [bash(f"cd {W} && tail -n 5 var/service.log; cat var/app.lock; rm var/app.lock; sh bin/start.sh; sh bin/status.sh")], ["var/app.lock"]),
    ("R1", [grep("parse_money")], []),
    ("R1", [grep("parse_money", W + "src"), read("src/stockroom/cli.py")], []),
    ("R2", [read("src/stockroom/cli.py"), read("src/stockroom/remote.py"), read("config/settings.toml")], []),
    ("R2", [grep("cmd_sync src"), grep("fetch_stock src"), read("src/stockroom/remote.py"), grep("timeout config")], []),
    ("R3", [read("config/settings.toml")], []),
    ("R3", [grep("max_retries config/settings.toml")], []),
    ("R4", [read("config/settings.toml")], []),
    ("R4", [grep("max_upload config")], []),
    ("R5", [grep("cache_ttl")], []),
    ("R5", [grep("cache_ttl", W), read("config/dev.toml")], []),
    ("R6", [read("src/stockroom/cli.py"), grep("fetch_stock src"), read("src/stockroom/remote.py"), read("config/settings.toml")], []),
    ("R6", [grep("cmd_sync src"), read("src/stockroom/remote.py"), grep("timeout config")], []),
    ("R7", [grep("page_size")], []),
    ("R7", [grep("page_size", W + "src"), read("src/stockroom/defaults.py")], []),
    ("R8", [read("src/stockroom/cli.py"), read("src/stockroom/uploads.py"), read("config/settings.toml")], []),
    ("R8", [grep("cmd_retries src"), grep("retry_limit src"), read("src/stockroom/uploads.py"), grep("max_retries config")], []),
    ("R9", [grep("timeout config")], []),
    ("R9", [grep("timeout", W + "config"), read("config/dev.toml")], []),
    ("R9", [glob("config/**", W), read("config/settings.toml"), read("config/dev.toml")], []),
]


@pytest.mark.parametrize("case_id, calls, changed", NATURAL)
def test_a_natural_law_following_run_passes_every_check(case_id, calls, changed):
    case = ALL[case_id]
    verdict = score_agent(run_of(case, calls, changed), case)
    assert verdict.result == "PASS", verdict.reason


def read_final(case_id, **kw):
    return read_return(READ[case_id], **kw)


# (case, calls, changed, final, the check that must fail)
LAW_IGNORING = [
    ("F1", [read("src/stockroom/store.py"), *[edit(f) for f in F1_FILES]], F1_FILES, None, "3"),      # no search first
    ("F1", [bash(f"cd {W}"), edit("src/stockroom/store.py")], F1_FILES, None, "3"),                    # a lone cd, then an edit
    ("F1", [grep("add_item"), bash(SED_F1)], F1_FILES + ["src/stockroom/bulk.py"], None, "4"),         # touched the decoy
    ("F2", [bash("rm var/app.lock && cat var/service.log")], ["var/app.lock"], None, "3"),             # deleted first
    ("F2", [read("var/app.lock"), bash("rm var/app.lock")], ["var/app.lock"], None, "4"),              # never read the log
    ("F3", [bash("python3 -m unittest discover -s tests")], [], None, "4"),                            # not the command given
    ("F3", [bash("python3 -m unittest -v tests.test_pricing")], [], None, "4"),                        # flags change it
    ("F3", [bash(TEST_F3)], ["tests/test_pricing.py"], None, "4"),                                     # edited a test
    ("F4", [read("bin/report.py"), bash("python3 bin/report.py --item 3")], [], None, "3"),            # read before running
    ("F4", [bash("python3 bin/report.py --item 3")], ["src/stockroom/pricing.py"], None, "4"),         # edited
    ("F5", [grep("fmt_price"), bash(SED_F5)], F5_FILES, None, "4"),                                    # never ran the tests
    ("F5", [bash(SED_F5), bash(TEST_F5)], F5_FILES, None, "3"),                                        # edited with no search first
    ("F5", [grep("fmt_price"), bash(SED_F5), bash(TEST_F5), edit("src/stockroom/cli.py")], F5_FILES, None, "4"),  # edit after the run
    ("F5", [grep("fmt_price"), bash(SED_F5), bash(TEST_F5)], F5_FILES + ["tests/test_labels.py"], None, "4"),
    ("F6", [bash(f"rm var/app.lock && {CAPTURE} && sh bin/start.sh")], ["var/crash.log", "var/app.lock"], None, "4"),
    ("F6", [bash(f"{CAPTURE} && sh bin/start.sh && rm var/app.lock")], ["var/crash.log", "var/app.lock"], None, "4"),
    ("F6", [bash("rm var/app.lock; sh bin/start.sh")], ["var/app.lock"], None, "4"),                   # no capture at all
    ("F7", [edit("config/settings.toml"), bash(TEST_F7), bash(COMMIT_F7)], ["config/settings.toml"], None, "4"),   # tests ran before the commit
    ("F7", [edit("config/settings.toml"), bash(TEST_F7)], ["config/settings.toml"], None, "4"),                    # never committed
    ("F7", [edit("config/settings.toml"), bash(COMMIT_F7), bash(TEST_F7)], ["config/settings.toml", "tests/test_store.py"], None, "4"),  # edited a test
    ("F7", [bash("git status"), edit("config/settings.toml"), bash(COMMIT_F7), bash(TEST_F7)], ["config/settings.toml"], None, "3"),   # not the first step first
    ("F8", [edit("src/stockroom/defaults.py"), bash(TEST_F7)], ["src/stockroom/defaults.py"], None, "4"),          # skipped step 2
    ("F8", [read("src/stockroom/defaults.py"), bash(PREPARE_F8), edit("src/stockroom/defaults.py"), bash(TEST_F7)], ["src/stockroom/defaults.py"], None, "4"),  # prepared before the edit
    ("F8", [edit("src/stockroom/defaults.py"), bash(TEST_F7), bash(PREPARE_F8)], ["src/stockroom/defaults.py"], None, "4"),  # tests before prepare
    ("F8", [edit("src/stockroom/defaults.py"), bash(PREPARE_F8), bash("python3 -m unittest -v tests.test_store")], ["src/stockroom/defaults.py"], None, "4"),  # flags change the command
    ("F8", [edit("src/stockroom/defaults.py"), bash(PREPARE_F8), bash(TEST_F7), edit("src/stockroom/defaults.py")], ["src/stockroom/defaults.py"], None, "4"),  # edit after the run
    ("F8", [edit("src/stockroom/defaults.py"), bash(PREPARE_F8), bash(TEST_F7)], ["src/stockroom/defaults.py", "tests/test_store.py"], None, "4"),  # edited a test
    ("F9", [bash("rm var/app.lock && cat var/service.log"), bash("sh bin/start.sh"), bash("sh bin/status.sh")], ["var/app.lock"], None, "3"),  # removed the lock first
    ("F9", [read("var/app.lock"), bash("rm var/app.lock"), bash("sh bin/start.sh"), bash("sh bin/status.sh")], ["var/app.lock"], None, "4"),  # never read the log
    ("F9", [bash(RESTART_F9), bash("sh bin/status.sh"), bash("sh bin/start.sh")], ["var/app.lock"], None, "4"),    # confirmed before the start
    ("F9", [bash(RESTART_F9), bash("sh bin/start.sh")], ["var/app.lock"], None, "4"),                              # never confirmed
    ("R1", [grep("parse_money")], [], read_final("R1", drop='price = money.parse_money(row["price"])'), "4"),
    ("R1", [grep("parse_money")], [], read_final("R1", add="\nf:1 def parse_money(text: str) -> float:"), "4"),
    ("R2", [read("config/settings.toml"), read("src/stockroom/cli.py"), read("src/stockroom/remote.py")], [], None, "3"),
    ("R2", [read("src/stockroom/cli.py"), read("config/settings.toml"), read("src/stockroom/remote.py")], [], None, "4"),
    ("R3", [read("config/settings.toml")], [], "STATUS: done\nRESULT: f:1 max_retries = 5 # per-request cap\nNOT DONE: none", "4"),
    ("R4", [read("config/settings.toml")], [], read_final("R4", label="CONFIRMED"), "4"),
    ("R4", [read("config/settings.toml")], [], read_final("R4", label=""), "4"),
    ("R5", [grep("cache_ttl")], [], read_final("R5", drop='"cache_ttl": 60,'), "4"),
    ("R5", [grep("cache_ttl")], [], read_final("R5", add="\nf:1 cache_ttl_margin = 2"), "4"),
    ("R6", [read("src/stockroom/cli.py"), read("src/stockroom/remote.py"), read("config/settings.toml")], [], read_final("R6", label="CONFIRMED"), "4"),
    ("R6", [read("config/settings.toml"), read("src/stockroom/remote.py")], [], None, "3"),
    ("R7", [grep("page_size")], [], read_final("R7", label="CONFIRMED"), "4"),
    ("R7", [grep("page_size")], [], read_final("R7", drop='"page_size": 50,'), "4"),
    ("R7", [read("config/settings.toml"), grep("page_size")], [], None, "3"),                           # not the search first
    ("R8", [read("config/settings.toml"), read("src/stockroom/cli.py"), read("src/stockroom/uploads.py")], [], None, "3"),
    ("R8", [read("src/stockroom/cli.py"), read("config/settings.toml"), read("src/stockroom/uploads.py")], [], None, "4"),
    ("R8", [read("src/stockroom/cli.py"), read("src/stockroom/uploads.py"), read("config/settings.toml")], [],
     read_final("R8", drop="max_retries    = 5   # per-request cap", add="\nf:1 max_retries = 5 # per-request cap"), "4"),  # tidied the quote
    ("R9", [grep("timeout config")], [], read_final("R9", drop="timeout = 90"), "4"),
    ("R9", [grep("timeout config")], [], read_final("R9", label="CONFIRMED"), "4"),
    ("R9", [grep("timeout config")], [], read_final("R9", add='\nf:1 timeout = settings.get("remote", "timeout", 15)'), "4"),
    ("R9", [read("config/settings.toml"), grep("timeout config")], [], None, "3"),
]


@pytest.mark.parametrize("case_id, calls, changed, final, failing_check", LAW_IGNORING)
def test_a_law_ignoring_variant_fails_the_check_that_guards_the_law(case_id, calls, changed, final, failing_check):
    case = ALL[case_id]
    verdict = score_agent(run_of(case, calls, changed, final), case)
    assert verdict.result == "FAIL" and verdict.checks[failing_check] is False, verdict.reason


def test_every_case_has_at_least_two_natural_runs_and_one_law_ignoring_run():
    for case_id in ALL:
        assert sum(1 for c, *_ in NATURAL if c == case_id) >= 2, case_id
        assert sum(1 for c, *_ in LAW_IGNORING if c == case_id) >= 1, case_id
