#!/usr/bin/env bash
# Routing-probe runner for skill fixtures (evals/author-agent.json).
# Each probe runs in a FRESH claude session so the live registry is read,
# not a stale snapshot. Exit 0 only if every fixture passes.
set -euo pipefail
cd "$(dirname "$0")/.."
pass=0; fail=0
while IFS=$'\t' read -r id prompt expect; do
  ans=$(claude -p "You have two skills: author-agent (runs the gated authoring loop — use when authoring the fix and applying it are part of the same job) and review-agent (design review — use when the deliverable is the verdict itself). Answer with ONLY one word — author-agent, review-agent, or none — for this task: $prompt" --model haiku </dev/null 2>/dev/null | tail -1)
  if printf '%s' "$ans" | grep -qi "$expect"; then
    echo "PASS $id ($ans)"; pass=$((pass+1))
  else
    echo "FAIL $id expected=$expect got=$ans"; fail=$((fail+1))
  fi
done < <(python3 -c "
import json
for f in json.load(open('evals/author-agent.json'))['fixtures']:
    print(f['id'], f['prompt'], f['expect'], sep='\t')")
echo "$pass passed, $fail failed"
[ "$fail" -eq 0 ]
