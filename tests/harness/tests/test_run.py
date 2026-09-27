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
