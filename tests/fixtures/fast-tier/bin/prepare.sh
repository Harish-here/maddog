#!/bin/sh
# Check the tools a test run needs.
command -v python3 >/dev/null || { echo "python3 is missing" >&2; exit 1; }
echo "environment ready"
