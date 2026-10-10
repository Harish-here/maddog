"""The pull-request workflow keeps its shape: one `validate` job that only
prepares the machine and runs .github/validate.sh."""
import subprocess
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[3]
WORKFLOW = ROOT / ".github" / "workflows" / "validate.yml"
SCRIPT = ROOT / ".github" / "validate.sh"


def workflow():
    return yaml.safe_load(WORKFLOW.read_text())


def test_one_job_named_validate_on_pull_requests_only():
    data = workflow()
    assert list(data["jobs"]) == ["validate"]
    assert list(data[True]) == ["pull_request"]  # PyYAML reads the key `on` as True


def test_runs_cancel_when_a_newer_push_arrives():
    assert workflow()["concurrency"] == {"group": "validate-${{ github.ref }}", "cancel-in-progress": True}


def test_job_fetches_history_builds_local_main_and_runs_the_script():
    steps = workflow()["jobs"]["validate"]["steps"]
    checkout = next(s for s in steps if s.get("uses", "").startswith("actions/checkout"))
    python = next(s for s in steps if s.get("uses", "").startswith("actions/setup-python"))
    assert checkout["with"]["fetch-depth"] == 0
    assert str(python["with"]["python-version"]) == "3.13" and python["with"]["cache"] == "pip"
    runs = [s["run"] for s in steps if "run" in s]
    assert any("git branch main origin/main" in r for r in runs)
    assert any("jq" in r and "apt-get install" in r for r in runs)
    assert runs[-1] == "bash .github/validate.sh"


def test_the_script_is_valid_bash_and_strict():
    subprocess.run(["bash", "-n", str(SCRIPT)], check=True)
    text = SCRIPT.read_text()
    assert "set -euo pipefail" in text and 'PYTHON="${PYTHON:-python3}"' in text


def test_the_script_runs_every_check_in_order():
    text = SCRIPT.read_text()
    order = ["\nVALIDATE\n", "scripts/fragment-check.py", "bash -n", "hooks/hooks.json", "command -v jq",
             "-m pytest tests/harness tests/guard -q", "tests/gate.py --base"]
    positions = [text.index(marker) for marker in order]
    assert positions == sorted(positions)
