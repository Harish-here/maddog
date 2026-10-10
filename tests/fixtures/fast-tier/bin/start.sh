#!/bin/sh
# Start the service. Refuses to start while a lock is held.
cd "$(dirname "$0")/.." || exit 1
if [ -e var/app.lock ]; then
  echo "locked: var/app.lock exists" >&2
  exit 1
fi
echo "service started"
