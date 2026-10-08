import pytest
from harness.core.shell import first_in_pipeline, split_shell


@pytest.mark.parametrize("command, steps", [
    ("ls", ["ls"]),
    ("tail -n 3 var/service.log > var/crash.log && rm var/app.lock && sh bin/start.sh",
     ["tail -n 3 var/service.log > var/crash.log", "rm var/app.lock", "sh bin/start.sh"]),
    ("a || b; c\nd", ["a", "b", "c", "d"]),
    ("python3 -m unittest tests.test_pricing 2>&1 | tail -20", ["python3 -m unittest tests.test_pricing 2>&1 | tail -20"]),
    ("cd /tmp/x && python3 -m unittest t", ["cd /tmp/x", "python3 -m unittest t"]),
    ("sed -i 's/a;b/c && d/' f && ls", ["sed -i 's/a;b/c && d/' f", "ls"]),
    ('grep "a && b" f; echo "say \\" ; quoted"', ['grep "a && b" f', 'echo "say \\" ; quoted"']),
    ("  ;; ", []),
    ("", []),
])
def test_split_shell(command, steps):
    assert split_shell(command) == steps


@pytest.mark.parametrize("step, head", [
    ("python3 -m unittest t | tail -5", "python3 -m unittest t"),
    ("grep 'a|b' f | head", "grep 'a|b' f"),
    ("ls", "ls"),
])
def test_first_in_pipeline(step, head):
    assert first_in_pipeline(step) == head
