#!/usr/bin/env bash
# watchdog-resume — relaunch a paused unattended Claude run once its resume time
# passes, even if the original session (or the host) died. Launches an INTERACTIVE
# session inside detached tmux: permission prompts wait for a human (correct for
# risky gates; Telegram pages you), everything else proceeds unattended, and you
# attach later with:  tmux attach -t jobbunny-resume   (from Ghostty, SSH, phone).
# State is written by the agent at pause time; deleted by it on in-session resume.
# Guard rails: single-shot per state file, no-launch if the tmux session already
# exists, lock against concurrent cron fires, logged, ping on every action.
NOTIFY="$HOME/.claude/channels/telegram/notify.sh"
DIR="$HOME/.claude/watchdogs"
STATE="$DIR/resume.state"
LOCK="$DIR/resume.lock"
LOG="$DIR/resume.log"
TMUX_SESSION="jobbunny-resume"

[ -f "$STATE" ] || exit 0
mkdir -p "$DIR"
if ! mkdir "$LOCK" 2>/dev/null; then exit 0; fi            # another fire mid-launch
trap 'rmdir "$LOCK" 2>/dev/null' EXIT

resume_at=$(sed -n 's/^resume_at=//p' "$STATE" | head -1)
cwd=$(sed -n 's/^cwd=//p' "$STATE" | head -1)
prompt=$(sed -n 's/^prompt=//p' "$STATE" | head -1)
[ -n "$resume_at" ] && [ -n "$cwd" ] && [ -n "$prompt" ] || { echo "$(date) malformed state" >> "$LOG"; exit 0; }
[ "$(date +%s)" -ge "$resume_at" ] || exit 0

# cron's env is minimal — get node (nvm) and the claude/tmux binaries on PATH
export PATH="$HOME/.local/bin:/opt/homebrew/bin:/usr/local/bin:$PATH"
[ -s "$HOME/.nvm/nvm.sh" ] && . "$HOME/.nvm/nvm.sh" >> "$LOG" 2>&1
command -v tmux  >/dev/null || { echo "$(date) tmux not found" >> "$LOG"; bash "$NOTIFY" "🤖 watchdog-resume: FAILED — tmux not on PATH"; exit 0; }
command -v claude >/dev/null || { echo "$(date) claude not found" >> "$LOG"; bash "$NOTIFY" "🤖 watchdog-resume: FAILED — claude not on PATH"; exit 0; }

if tmux has-session -t "$TMUX_SESSION" 2>/dev/null; then   # a resume is already live
  echo "$(date) session already exists — not launching" >> "$LOG"
  bash "$NOTIFY" "🤖 watchdog-resume: $TMUX_SESSION already running — attach with: tmux attach -t $TMUX_SESSION"
  exit 0
fi

mv "$STATE" "$STATE.launched"                               # single-shot: never double-launch
echo "=== $(date) launching tmux session: $prompt" >> "$LOG"
tmux new-session -d -s "$TMUX_SESSION" -c "$cwd" "claude"
sleep 5                                                     # let the REPL come up
tmux send-keys -t "$TMUX_SESSION" -l "$prompt"
tmux send-keys -t "$TMUX_SESSION" Enter
bash "$NOTIFY" "🤖 watchdog-resume: limit window passed — interactive session relaunched in $cwd. Attach: tmux attach -t $TMUX_SESSION (it pages you if a permission gate blocks)"
exit 0
