#!/bin/bash
set -u

BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DATA_DIR="$BASE_DIR/data"
LOCK_FILE="$DATA_DIR/log_retention.lock"
REPORT="$DATA_DIR/log_retention.log"

mkdir -p "$DATA_DIR"
exec 9>"$LOCK_FILE"
if ! flock -n 9; then
  exit 0
fi

keep_tail() {
  local f="$1"
  local lines="$2"
  [ -f "$f" ] || return 0
  local tmp
  tmp="$(mktemp /tmp/ibis_logtrim.XXXXXX)"
  tail -n "$lines" "$f" > "$tmp" 2>/dev/null || true
  cp "$tmp" "$f"
  rm -f "$tmp"
}

# Keep fast-moving ops logs compact and parseable.
keep_tail "$BASE_DIR/health_check.log" 4000
keep_tail "$BASE_DIR/agent_monitor.log" 4000
keep_tail "$DATA_DIR/execution_integrity.log" 4000
keep_tail "$DATA_DIR/hourly_kpi_runner.log" 4000
keep_tail "$DATA_DIR/truth_stream.log" 8000
keep_tail "$DATA_DIR/log_retention.log" 2000

# Prune old compressed backups if any exist.
find "$DATA_DIR" -maxdepth 1 -type f -name '*.gz' -mtime +21 -delete 2>/dev/null || true

{
  echo "$(date '+%Y-%m-%d %H:%M:%S') retention_ok"
  du -h "$DATA_DIR"/*.log 2>/dev/null | sort -h | tail -n 12
  echo ""
} >> "$REPORT"
