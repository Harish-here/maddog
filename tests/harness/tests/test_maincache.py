from harness.core.cases import Case
from harness.core.events import Event
from harness.core.maincache import CacheKey, MainCache, hash_file

CASE = Case("c1", "do it", "Fast", "none", "advisor-mode", "todo-app")
LADDER = {"low": "haiku", "mid": "sonnet", "high": "opus"}


def make_cache(tmp_path, **kw):
    defaults = dict(cache_dir=tmp_path, sha="abc123", runtime="claude-code",
                    model_ladder=LADDER, adapter_hash="deadbeef")
    defaults.update(kw)
    return MainCache(**defaults)


def test_miss_when_nothing_stored(tmp_path):
    cache = make_cache(tmp_path)
    assert cache.get(CASE, "low", 3) is None


def test_put_then_get_round_trips_events(tmp_path):
    cache = make_cache(tmp_path)
    events = [[Event("handoff", "Fast")], [Event("handoff", "Fast")], [Event("handoff", "Fast")]]
    cache.put(CASE, "low", events)
    loaded = cache.get(CASE, "low", 3)
    assert loaded == events


def test_miss_when_fewer_runs_stored_than_required(tmp_path):
    cache = make_cache(tmp_path)
    cache.put(CASE, "low", [[Event("handoff", "Fast")], [Event("handoff", "Fast")]])
    assert cache.get(CASE, "low", 3) is None


def test_different_tier_is_a_different_key(tmp_path):
    cache = make_cache(tmp_path)
    cache.put(CASE, "low", [[Event("handoff", "Fast")]] * 3)
    assert cache.get(CASE, "mid", 3) is None


def test_different_sha_is_a_different_key(tmp_path):
    make_cache(tmp_path).put(CASE, "low", [[Event("handoff", "Fast")]] * 3)
    other = make_cache(tmp_path, sha="different-sha")
    assert other.get(CASE, "low", 3) is None


def test_different_adapter_hash_is_a_different_key(tmp_path):
    make_cache(tmp_path).put(CASE, "low", [[Event("handoff", "Fast")]] * 3)
    other = MainCache(cache_dir=tmp_path, sha="abc123", runtime="claude-code",
                      model_ladder=LADDER, adapter_hash="other-hash")
    assert other.get(CASE, "low", 3) is None


def test_fresh_ignores_a_populated_cache(tmp_path):
    make_cache(tmp_path).put(CASE, "low", [[Event("handoff", "Fast")]] * 3)
    fresh = make_cache(tmp_path, fresh=True)
    assert fresh.get(CASE, "low", 3) is None


def test_fresh_put_overwrites_the_old_entry(tmp_path):
    make_cache(tmp_path).put(CASE, "low", [[Event("handoff", "Smart")]] * 3)
    fresh = make_cache(tmp_path, fresh=True)
    fresh.put(CASE, "low", [[Event("handoff", "Fast")]] * 3)
    reread = make_cache(tmp_path)  # not fresh: reads what's on disk now
    assert reread.get(CASE, "low", 3) == [[Event("handoff", "Fast")]] * 3


def test_hash_file_is_stable_for_the_same_bytes(tmp_path):
    f = tmp_path / "a.py"
    f.write_text("print(1)\n")
    assert hash_file(f) == hash_file(f)


def test_hash_file_differs_when_bytes_differ(tmp_path):
    f1, f2 = tmp_path / "a.py", tmp_path / "b.py"
    f1.write_text("print(1)\n")
    f2.write_text("print(2)\n")
    assert hash_file(f1) != hash_file(f2)


def test_cache_key_digest_is_deterministic():
    k1 = CacheKey("sha", "rt", "model", "prompt", "fixture", "hash")
    k2 = CacheKey("sha", "rt", "model", "prompt", "fixture", "hash")
    assert k1.digest() == k2.digest()
