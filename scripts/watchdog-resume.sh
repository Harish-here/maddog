#!/usr/bin/env bash
# watchdog-resume — relaunch a paused unattended Claude run once its resume time
# passes, even if the original session (or the host) died. Launches an INTERACTIVE
# session inside detached tmux: permission prompts wait for a human (correct for
# risky gates; Telegram pages you), everything else proceeds unattended, and you
# attach later with:  tmux attach -t <session>   (from Ghostty, SSH, phone).
# State is written by the agent at pause time; deleted by it on in-session resume.
# Runs as a LaunchAgent (NOT cron): launchd gui/ sessions reach the keychain, cron cannot
# (live-tested 2026-08-08: cron -> Not logged in; LaunchAgent -> Claude Max, prompt answered).
#
# State file fields (one `key=value` per line):
#   mode=standing|<anything else>   'standing' persists across relaunches; anything
#                                    else is one-shot (consumed after a verified launch)
#   resume_at=<epoch seconds>       must be all-digits or the run is treated as malformed
#   cwd=<path>
#   prompt=<text>                   MUST be a single line — sent verbatim via
#                                    `tmux send-keys -l`, a newline would submit early
#   session=<tmux session name>     optional; defaults to `claude-resume`
#
# Guard rails: single-shot per state file (consumed only after the REPL and prompt
# send are verified), no-launch if the tmux session already exists, lock against
# concurrent cron/launchd fires (with a >30min stale-lock breaker), crash-loop
# quarantine (scoped to the state file's own mtime, so a rewritten state file never
# inherits an old attempt count), logged, ping on every action (including failures).
NOTIFY="$HOME/.claude/channels/telegram/notify.sh"
DIR="$HOME/.claude/watchdogs"
STATE="$DIR/resume.state"
LOCK="$DIR/resume.lock"
LOG="$DIR/resume.log"

[ -f "$STATE" ] || exit 0
mkdir -p "$DIR"

# Stale-lock breaker: a lock dir older than 30min means a prior run died without
# cleaning up (crash, kill -9) — clear it so we don't wedge forever.
if [ -d "$LOCK" ] && [ -z "$(find "$LOCK" -maxdepth 0 -mmin -30 2>/dev/null)" ]; then
  rmdir "$LOCK" 2>/dev/null
fi

if ! mkdir "$LOCK" 2>/dev/null; then exit 0; fi            # another fire mid-launch
trap 'rmdir "$LOCK" 2>/dev/null' EXIT

resume_at=$(sed -n 's/^resume_at=//p' "$STATE" | head -1)
cwd=$(sed -n 's/^cwd=//p' "$STATE" | head -1)
prompt=$(sed -n 's/^prompt=//p' "$STATE" | head -1)
mode=$(sed -n 's/^mode=//p' "$STATE" | head -1)     # 'standing' = persists for a whole run; anything else = one-shot
session=$(sed -n 's/^session=//p' "$STATE" | head -1)
TMUX_SESSION="${session:-claude-resume}"

[ -n "$resume_at" ] && [ -n "$cwd" ] && [ -n "$prompt" ] || { echo "$(date) malformed state" >> "$LOG"; exit 0; }

case "$resume_at" in
  ''|*[!0-9]*)
    echo "$(date) malformed resume_at: $resume_at" >> "$LOG"
    bash "$NOTIFY" "🤖 watchdog-resume: FAILED — malformed resume_at ($resume_at)"
    exit 0
    ;;
esac

[ "$(date +%s)" -ge "$resume_at" ] || exit 0

# cron's env is minimal — get node (nvm) and the claude/tmux binaries on PATH
export PATH="$HOME/.local/bin:/opt/homebrew/bin:/usr/local/bin:$PATH"
[ -s "$HOME/.nvm/nvm.sh" ] && . "$HOME/.nvm/nvm.sh" >> "$LOG" 2>&1
command -v tmux  >/dev/null || { echo "$(date) tmux not found" >> "$LOG"; bash "$NOTIFY" "🤖 watchdog-resume: FAILED — tmux not on PATH"; exit 0; }
command -v claude >/dev/null || { echo "$(date) claude not found" >> "$LOG"; bash "$NOTIFY" "🤖 watchdog-resume: FAILED — claude not on PATH"; exit 0; }

if tmux has-session -t "$TMUX_SESSION" 2>/dev/null; then   # a resume is already live
  exit 0                       # run alive — silent (standing files fire every 10 min; the launch ping is the signal)
fi

LAST="$DIR/resume.lastlaunch"
state_mtime=$(stat -f %m "$STATE" 2>/dev/null)
if [ "$mode" = "standing" ] && [ -f "$LAST" ]; then
  last_state_mtime=$(awk '{print $1}' "$LAST" 2>/dev/null)
  last_epoch=$(awk '{print $2}' "$LAST" 2>/dev/null)
  if [ -n "$state_mtime" ] && [ "$last_state_mtime" = "$state_mtime" ] \
     && [ -n "$last_epoch" ] && [ $(( $(date +%s) - last_epoch )) -lt 3600 ]; then
    mv "$STATE" "$STATE.crashloop.$(date +%s)"              # relaunched <1h ago (same state file) and died again — stop churning
    bash "$NOTIFY" "🤖 watchdog-resume: CRASH LOOP — relaunch died within the hour; state quarantined (resume.state.crashloop.<ts>), needs you"
    exit 0
  fi
fi
echo "$state_mtime $(date +%s)" > "$LAST"                   # scoped to this state file's mtime, not just wall-clock

echo "=== $(date) launching tmux session: $prompt" >> "$LOG"
tmux new-session -d -s "$TMUX_SESSION" -c "$cwd" "/bin/zsh -lic claude" || {   # interactive login shell: full user env (auth) regardless of cron's stripped env
  echo "$(date) FAILED — tmux new-session" >> "$LOG"
  bash "$NOTIFY" "🤖 watchdog-resume: FAILED — tmux new-session"
  exit 0
}

ready=0
i=0
while [ "$i" -lt 30 ]; do                                   # poll up to 60s (2s interval) for the REPL to come up
  sleep 2
  if tmux capture-pane -p -t "$TMUX_SESSION" 2>/dev/null | grep -qE '❯|Claude Code'; then
    ready=1
    break
  fi
  i=$((i + 1))
done

if [ "$ready" -ne 1 ]; then
  echo "$(date) FAILED — REPL never became ready" >> "$LOG"
  bash "$NOTIFY" "🤖 watchdog-resume: FAILED — REPL never became ready; session left for inspection"
  exit 0                                                     # do NOT consume state; has-session guard prevents relaunch churn while it's up
fi

tmux send-keys -t "$TMUX_SESSION" -l "$prompt"
tmux send-keys -t "$TMUX_SESSION" Enter

tmux has-session -t "$TMUX_SESSION" 2>/dev/null || {
  echo "$(date) FAILED — session gone after prompt send" >> "$LOG"
  bash "$NOTIFY" "🤖 watchdog-resume: FAILED — session died right after the prompt was sent"
  exit 0
}

[ "$mode" = "standing" ] || mv "$STATE" "$STATE.launched"   # one-shot files are consumed only after a verified launch; standing files persist
bash "$NOTIFY" "🤖 watchdog-resume: limit window passed — interactive session relaunched in $cwd. Attach: tmux attach -t $TMUX_SESSION (it pages you if a permission gate blocks)"
exit 0
