#!/usr/bin/env bash
# Routing-probe runner for skill or agent fixtures. Usage: run-skill-routing.sh [fixtures.json]
# Candidate descriptions are extracted from each candidate's frontmatter
# at RUN TIME (SKILL.md for skills, agent .md for agents), so probes grade the shipped text, never a paraphrase.
# Routing probes are stochastic: each graded fixture is sampled SAMPLES times
# (default 5) and passes at PASS_AT (default 4) or more agreeing answers.
# "expect": null fixtures are report-only: all sampled answers are printed,
# none are graded. A failed claude call records ERROR for that sample instead
# of aborting the run.
set -euo pipefail
cd "$(dirname "$0")/.."
FIXTURES="${1:-evals/author-agent.json}"
SAMPLES="${SAMPLES:-5}"
PASS_AT="${PASS_AT:-4}"
CANDIDATES_TYPE=$(python3 -c "
import json
d = json.load(open('$FIXTURES'))
print(d.get('candidates_type', 'skills'))")
VERB="invoke"; [ "$CANDIDATES_TYPE" = "agents" ] && VERB="dispatch"
DESCS=$(python3 -c "
import json, yaml
d = json.load(open('$FIXTURES'))
parts = []
for c in d['candidates']:
    fm = open(c['path']).read().split('---')[1]
    desc = ' '.join(yaml.safe_load(fm)['description'].split())
    parts.append(c['name'] + ': ' + desc)
print(' || '.join(parts))")
NAMES=$(python3 -c "
import json
d = json.load(open('$FIXTURES'))
print(', '.join(c['name'] for c in d['candidates']))")
pass=0; fail=0
while IFS=$'\t' read -r id prompt expect core; do
  hits=0; answers=""
  for _ in $(seq "$SAMPLES"); do
    ans=$(claude -p "You can $VERB exactly these $CANDIDATES_TYPE, described verbatim: $DESCS. Answer with ONLY one word — $NAMES, or none — for this task: $prompt" --model haiku </dev/null 2>/dev/null | tail -1) || ans="ERROR"
    answers="$answers $ans"
    if [ "$expect" != "None" ] && printf '%s' "$ans" | grep -qi "$expect"; then
      hits=$((hits+1))
    fi
  done
  if [ "$expect" = "None" ]; then
    echo "REPORT $id:$answers"
  elif [ "$hits" -ge "$PASS_AT" ]; then
    echo "PASS $id ($hits/$SAMPLES:$answers)"; pass=$((pass+1))
  elif [ "$core" = "True" ]; then
    echo "FAIL $id expected=$expect ($hits/$SAMPLES:$answers)"; fail=$((fail+1))
  else
    echo "FAIL(non-gating) $id expected=$expect ($hits/$SAMPLES:$answers)"; fi
done < <(python3 -c "
import json
for f in json.load(open('$FIXTURES'))['fixtures']:
    print(f['id'], f['prompt'], f.get('expect'), f.get('core', True), sep='\t')")
echo "$pass passed, $fail failed"
[ "$fail" -eq 0 ]
