#!/usr/bin/env bash
# Every check a pull request must pass, in one place so CI and the release
# skill run the same thing. Needs: python with pyyaml and pytest (set PYTHON
# to the test venv's python locally), jq, and a local `main` branch.
#
#   PYTHON=tests/.venv/bin/python .github/validate.sh
#
# BASE (default origin/main) is the ref the release gate compares against.
set -euo pipefail

PYTHON="${PYTHON:-python3}"
if [[ "$PYTHON" == */* && "$PYTHON" != /* ]]; then
  PYTHON="$PWD/$PYTHON"  # keep a relative interpreter path valid after the cd below
fi
cd "$(dirname "$0")/.."

echo "== frontmatter, JSON, version consistency"
"$PYTHON" - << 'VALIDATE'
import json
import yaml
from pathlib import Path
import re
import sys

errors = []

# Validate frontmatter YAML in markdown skill files
for pattern in ['skills/*/SKILL.md', '.claude/skills/*/SKILL.md', 'agents/*.md']:
    for md_file in Path('.').glob(pattern):
        try:
            with open(md_file) as f:
                content = f.read()
                if content.startswith('---'):
                    end = content.find('---', 3)
                    if end > 0:
                        frontmatter = content[3:end].strip()
                        yaml.safe_load(frontmatter)
        except Exception as e:
            errors.append(f'{md_file}: {e}')

# Validate JSON files
for pattern in ['.claude-plugin/*.json']:
    for json_file in Path('.').glob(pattern):
        try:
            json.loads(json_file.read_text())
        except Exception as e:
            errors.append(f'{json_file}: {e}')

# Check version consistency
try:
    plugin_version = json.loads(Path('.claude-plugin/plugin.json').read_text()).get('version')
    changelog = Path('CHANGELOG.md').read_text()
    match = re.search(r'^## \[([^\]]+)\]', changelog, re.MULTILINE)
    changelog_version = match.group(1) if match else None
    if plugin_version != changelog_version:
        errors.append(f'Version mismatch: plugin.json={plugin_version}, CHANGELOG={changelog_version}')
except Exception as e:
    errors.append(f'Version check: {e}')

if errors:
    for err in errors:
        print(err)
    sys.exit(1)
VALIDATE

echo "== fragment check"
"$PYTHON" scripts/fragment-check.py

echo "== shell syntax"
for script in scripts/*.sh; do
  bash -n "$script"
done

echo "== hook command paths exist"
"$PYTHON" - << 'HOOKS'
import json
import sys
from pathlib import Path

missing = []
hooks = json.loads(Path('hooks/hooks.json').read_text())
for entries in hooks.get('hooks', {}).values():
    for entry in entries:
        for hook in entry.get('hooks', []):
            command = hook.get('command', '')
            path = Path(command.replace('${CLAUDE_PLUGIN_ROOT}', '.'))
            if not path.is_file():
                missing.append(command)
if missing:
    print('hooks.json names missing files: ' + ', '.join(missing))
    sys.exit(1)
HOOKS

echo "== jq present"
command -v jq > /dev/null || { echo "jq is required: the guard tests need it"; exit 1; }

echo "== offline tests"
"$PYTHON" -m pytest tests/harness tests/guard -q -p no:cacheprovider

echo "== release gate"
"$PYTHON" tests/gate.py --base "${BASE:-origin/main}"
