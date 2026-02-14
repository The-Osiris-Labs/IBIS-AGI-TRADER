#!/bin/bash
set -u

AGENT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OUT_FILE="$AGENT_DIR/data/truth_stream.log"
LOCK_FILE="$AGENT_DIR/data/truth_snapshot.lock"

mkdir -p "$AGENT_DIR/data"
exec 9>"$LOCK_FILE"
if ! flock -n 9; then
  exit 0
fi

cd "$AGENT_DIR" || exit 1
python3 tools/truth_snapshot.py >> "$OUT_FILE" 2>&1
exit $?
