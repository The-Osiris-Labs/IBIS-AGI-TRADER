#!/bin/bash

set -u

AGENT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_FILE="$AGENT_DIR/data/hourly_kpi_runner.log"
LOCK_FILE="$AGENT_DIR/data/hourly_kpi.lock"

mkdir -p "$AGENT_DIR/data"
exec 9>"$LOCK_FILE"
if ! flock -n 9; then
  echo "Another hourly KPI run is in progress, exiting"
  exit 0
fi

echo "=== Hourly KPI Report: $(date '+%Y-%m-%d %H:%M:%S') ===" >> "$LOG_FILE"

cd "$AGENT_DIR" || exit 1
python3 tools/hourly_kpi_report.py >> "$LOG_FILE" 2>&1
rc=$?

echo "hourly_kpi_report exit code: $rc" >> "$LOG_FILE"
echo "" >> "$LOG_FILE"

exit $rc
