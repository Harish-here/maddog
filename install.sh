#!/usr/bin/env bash
# Symlinks maddog-skills agents and skills into ~/.claude so Claude Code
# picks them up globally. Idempotent: existing symlinks are re-pointed;
# existing REAL files/dirs are backed up to <name>.bak first, never deleted.
set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CLAUDE_DIR="${CLAUDE_DIR:-$HOME/.claude}"

mkdir -p "$CLAUDE_DIR/agents" "$CLAUDE_DIR/skills" "$CLAUDE_DIR/workflows" "$CLAUDE_DIR/channels/telegram" "$CLAUDE_DIR/watchdogs" "$CLAUDE_DIR/hooks"

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

# executor-guard: PreToolUse Bash hook that bounces irreversible commands
# (force-delete, force-push, hard reset, mass discard, etc.) away from
# executor-fast — see scripts/executor-guard.sh header for the contract.
link "$REPO_DIR/scripts/executor-guard.sh" "$CLAUDE_DIR/hooks/executor-guard.sh"

# watchdog-resume: LaunchAgent that relaunches a paused unattended run once its
# resume time passes. Symlink the script, then generate the plist from the
# template (its __HOME__ placeholder is substituted here, not committed).
link "$REPO_DIR/scripts/watchdog-resume.sh" "$CLAUDE_DIR/watchdogs/watchdog-resume.sh"

WATCHDOG_PLIST="$HOME/Library/LaunchAgents/com.maddog.watchdog-resume.plist"
mkdir -p "$HOME/Library/LaunchAgents"
WATCHDOG_PLIST_NEW="$(sed "s|__HOME__|$HOME|g" "$REPO_DIR/scripts/com.maddog.watchdog-resume.plist")"
if [ ! -f "$WATCHDOG_PLIST" ] || [ "$(cat "$WATCHDOG_PLIST")" != "$WATCHDOG_PLIST_NEW" ]; then
  printf '%s\n' "$WATCHDOG_PLIST_NEW" > "$WATCHDOG_PLIST"
  echo "wrote: $WATCHDOG_PLIST"
  echo "next step — load it: launchctl bootstrap gui/$(id -u) $WATCHDOG_PLIST"
else
  echo "unchanged: $WATCHDOG_PLIST"
fi

echo "done — restart Claude Code sessions to pick up changes"
