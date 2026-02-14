#!/bin/bash

set -u

AGENT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_FILE="$AGENT_DIR/data/execution_integrity.log"
LOCK_FILE="$AGENT_DIR/data/execution_integrity.lock"

mkdir -p "$AGENT_DIR/data"
exec 9>"$LOCK_FILE"
if ! flock -n 9; then
  echo "Another execution-integrity run is in progress, exiting"
  exit 0
fi

echo "=== Execution Integrity Check: $(date '+%Y-%m-%d %H:%M:%S') ===" >> "$LOG_FILE"

cd "$AGENT_DIR" || exit 1
python3 tools/execution_integrity_check.py >> "$LOG_FILE" 2>&1
rc=$?

echo "execution_integrity_check exit code: $rc" >> "$LOG_FILE"
echo "" >> "$LOG_FILE"

exit $rc
