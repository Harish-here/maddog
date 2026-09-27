import sys
from pathlib import Path

import pytest

# Make `harness` importable the same way run.py sees it: tests/ on sys.path.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


@pytest.fixture(autouse=True)
def _isolate_results_dir(tmp_path, monkeypatch):
    """Redirect run.py's RESULTS_DIR to a temp folder so unit tests don't
    clutter the real tests/results/. This fixture runs for every test."""
    import run
    monkeypatch.setattr(run, "RESULTS_DIR", tmp_path / "results")
