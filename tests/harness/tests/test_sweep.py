import os
import subprocess
import sys
import time

from harness.core import sweep
from harness.core.cases import TESTS_DIR

REPO = TESTS_DIR.parent


def _dead_pid() -> int:
    proc = subprocess.Popen([sys.executable, "-c", "pass"])
    proc.wait()
    return proc.pid  # reaped by wait(); guaranteed not to belong to a live process


def test_removes_a_folder_whose_marker_pid_is_dead(tmp_path):
    folder = tmp_path / "maddog-run-0"
    folder.mkdir()
    (folder / sweep.MARKER_NAME).write_text(str(_dead_pid()))

    removed = sweep.sweep(REPO, base=tmp_path)

    assert folder in removed
    assert not folder.exists()


def test_keeps_a_folder_whose_marker_pid_is_alive(tmp_path):
    folder = tmp_path / "maddog-run-1"
    folder.mkdir()
    (folder / sweep.MARKER_NAME).write_text(str(os.getpid()))

    removed = sweep.sweep(REPO, base=tmp_path)

    assert folder not in removed
    assert folder.exists()


def test_removes_a_markerless_folder_older_than_24h(tmp_path):
    folder = tmp_path / "maddog-test-old-1234"
    folder.mkdir()
    old = time.time() - sweep.STALE_AGE_SECONDS - 60
    os.utime(folder, (old, old))

    removed = sweep.sweep(REPO, base=tmp_path)

    assert folder in removed


def test_keeps_a_markerless_recent_folder(tmp_path):
    folder = tmp_path / "maddog-baseline-abcd"
    folder.mkdir()

    removed = sweep.sweep(REPO, base=tmp_path)

    assert folder not in removed
    assert folder.exists()


def test_ignores_folders_with_unrelated_names(tmp_path):
    folder = tmp_path / "not-ours"
    folder.mkdir()
    old = time.time() - sweep.STALE_AGE_SECONDS - 60
    os.utime(folder, (old, old))

    removed = sweep.sweep(REPO, base=tmp_path)

    assert folder not in removed
    assert folder.exists()
