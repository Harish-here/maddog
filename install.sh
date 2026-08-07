#!/usr/bin/env bash
# Symlinks maddog-skills agents and skills into ~/.claude so Claude Code
# picks them up globally. Idempotent: existing symlinks are re-pointed;
# existing REAL files/dirs are backed up to <name>.bak first, never deleted.
set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CLAUDE_DIR="${CLAUDE_DIR:-$HOME/.claude}"

mkdir -p "$CLAUDE_DIR/agents" "$CLAUDE_DIR/skills" "$CLAUDE_DIR/workflows" "$CLAUDE_DIR/channels/telegram"

link() {
  local src="$1" dst="$2"
  if [ -L "$dst" ]; then
    rm "$dst"
  elif [ -e "$dst" ]; then
    echo "backup: $dst -> $dst.bak"
    mv "$dst" "$dst.bak"
  fi
  ln -s "$src" "$dst"
  echo "linked: $dst -> $src"
}

for f in "$REPO_DIR"/agents/*.md; do
  link "$f" "$CLAUDE_DIR/agents/$(basename "$f")"
done

for d in "$REPO_DIR"/skills/*/; do
  d="${d%/}"
  link "$d" "$CLAUDE_DIR/skills/$(basename "$d")"
done

for f in "$REPO_DIR"/workflows/*.js; do
  link "$f" "$CLAUDE_DIR/workflows/$(basename "$f")"
done

# Checkpoint-ping helper the sdd-task-loop workflow calls by default.
# Reads TELEGRAM_BOT_TOKEN / TELEGRAM_CHAT_ID from ~/.claude/channels/telegram/.env
# (never versioned here) — see workflows/sdd-task-loop.js header for the contract.
link "$REPO_DIR/scripts/tg-notify.sh" "$CLAUDE_DIR/channels/telegram/notify.sh"

echo "done — restart Claude Code sessions to pick up changes"
