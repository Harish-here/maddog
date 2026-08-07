#!/usr/bin/env bash
# tg-notify — fire-and-forget Telegram checkpoint pings for unattended loops.
# Usage:  notify.sh "message"        (or pipe:  echo "message" | notify.sh)
# Env:    TELEGRAM_BOT_TOKEN / TELEGRAM_CHAT_ID — shell env wins, else
#         ~/.claude/channels/telegram/.env is sourced.
# Always exits 0: a dead network or bad token must NEVER fail the calling loop.

ENV_FILE="$HOME/.claude/channels/telegram/.env"
[ -z "$TELEGRAM_BOT_TOKEN" ] && [ -f "$ENV_FILE" ] && . "$ENV_FILE"

MSG="${1:-$(cat)}"
[ -z "$MSG" ] && exit 0
[ -z "$TELEGRAM_BOT_TOKEN" ] && exit 0
[ -z "$TELEGRAM_CHAT_ID" ] && exit 0

curl -sS --max-time 10 "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage" \
  --data-urlencode "chat_id=${TELEGRAM_CHAT_ID}" \
  --data-urlencode "text=${MSG}" \
  --data-urlencode "disable_web_page_preview=true" \
  >/dev/null 2>&1 || true
exit 0
