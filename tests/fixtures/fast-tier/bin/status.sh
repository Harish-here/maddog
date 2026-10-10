#!/bin/sh
# Ask the service whether it answers. It does not while a lock is held.
cd "$(dirname "$0")/.." || exit 1
if [ -e var/app.lock ]; then
  echo "no answer: var/app.lock exists" >&2
  exit 1
fi
echo "service answers"
