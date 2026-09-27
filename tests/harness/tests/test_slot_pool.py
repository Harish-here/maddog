from harness.core.fixture import SlotPool
from harness.core.sweep import MARKER_NAME


def test_grants_one_distinct_path_per_job(tmp_path):
    pool = SlotPool(3, base=tmp_path)
    try:
        paths = [pool.path(i) for i in range(3)]
        assert len(set(paths)) == 3
        assert all(p.exists() for p in paths)
        assert all((p / MARKER_NAME).exists() for p in paths)
    finally:
        pool.close()


def test_same_process_reuses_the_same_slot_after_closing(tmp_path):
    first = SlotPool(1, base=tmp_path)
    path1 = first.path(0)
    first.close()

    second = SlotPool(1, base=tmp_path)
    try:
        assert second.path(0) == path1
    finally:
        second.close()


def test_a_locked_slot_is_skipped_in_favor_of_the_next_free_number(tmp_path):
    holder = SlotPool(1, base=tmp_path)  # takes maddog-run-0 and holds its lock
    try:
        other = SlotPool(1, base=tmp_path)
        try:
            assert other.path(0) != holder.path(0)
            assert other.path(0).name != holder.path(0).name
        finally:
            other.close()
    finally:
        holder.close()


def test_close_removes_every_slot_folder(tmp_path):
    pool = SlotPool(2, base=tmp_path)
    paths = [pool.path(i) for i in range(2)]
    pool.close()
    assert not any(p.exists() for p in paths)
