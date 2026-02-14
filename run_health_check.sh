#!/bin/bash

# IBIS True Agent Health Check
# Runs every 15 minutes to ensure agent is healthy

AGENT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HEALTH_LOG="$AGENT_DIR/health_check.log"
HEALTH_CHECK="$AGENT_DIR/check_agent_health.sh"
RUNTIME_STATUS="$AGENT_DIR/runtime_status.sh"
RECONCILE_SCRIPT="$AGENT_DIR/tools/reconcile_state_db.py"
EXEC_INTEGRITY_SCRIPT="$AGENT_DIR/tools/execution_integrity_check.py"
TRUTH_SNAPSHOT_SCRIPT="$AGENT_DIR/tools/truth_snapshot.py"
TRUTH_STREAM_LOG="$AGENT_DIR/data/truth_stream.log"
LOCK_FILE="$AGENT_DIR/data/run_health_check.lock"
SERVICE_NAME="ibis-agent.service"
AGENT_REGEX="/root/projects/(ibis_trader|Dont enter unless solicited/AGI Trader)/ibis_true_agent.py"

mkdir -p "$AGENT_DIR/data"
exec 9>"$LOCK_FILE"
if ! flock -n 9; then
    echo "Another health-check run is in progress, exiting"
    exit 0
fi

# Log health check
echo "=== Health Check: $(date '+%Y-%m-%d %H:%M:%S') ===" >> "$HEALTH_LOG"

# Ensure we only ever keep one live agent process.
agent_pids="$(pgrep -f "$AGENT_REGEX" 2>/dev/null || true)"
pid_count="$(echo "$agent_pids" | awk 'NF' | wc -l)"
if [ "${pid_count:-0}" -gt 1 ]; then
    main_pid="$(systemctl show "$SERVICE_NAME" -p MainPID --value 2>/dev/null || echo 0)"
    echo "Detected duplicate agent processes ($pid_count). MainPID=$main_pid" >> "$HEALTH_LOG"
    while read -r pid; do
        [ -z "$pid" ] && continue
        if [ "$pid" != "$main_pid" ]; then
            kill "$pid" 2>/dev/null || true
            echo "Killed duplicate agent pid=$pid" >> "$HEALTH_LOG"
        fi
    done <<< "$agent_pids"
fi

# Run health check
if [ -f "$HEALTH_CHECK" ]; then
    if [ -x "$HEALTH_CHECK" ]; then
        cd "$AGENT_DIR" || exit 1
        ./check_agent_health.sh >> "$HEALTH_LOG" 2>&1
        HEALTH_EXIT=$?
    else
        chmod +x "$HEALTH_CHECK"
        cd "$AGENT_DIR" || exit 1
        ./check_agent_health.sh >> "$HEALTH_LOG" 2>&1
        HEALTH_EXIT=$?
    fi
else
    echo "Health check script not found: $HEALTH_CHECK" >> "$HEALTH_LOG"
    exit 1
fi

echo "Health check exit code: ${HEALTH_EXIT:-1}" >> "$HEALTH_LOG"

if [ -f "$RECONCILE_SCRIPT" ]; then
    echo "--- reconcile_state_db ---" >> "$HEALTH_LOG"
    python3 "$RECONCILE_SCRIPT" --apply >> "$HEALTH_LOG" 2>&1
    RECON_EXIT=$?
    echo "reconcile_state_db exit code: ${RECON_EXIT}" >> "$HEALTH_LOG"
    if [ "${HEALTH_EXIT:-1}" -eq 0 ] && [ "$RECON_EXIT" -ge 2 ]; then
        HEALTH_EXIT=$RECON_EXIT
    fi
fi

if [ -f "$EXEC_INTEGRITY_SCRIPT" ]; then
    echo "--- execution_integrity ---" >> "$HEALTH_LOG"
    python3 "$EXEC_INTEGRITY_SCRIPT" --live-open-orders >> "$HEALTH_LOG" 2>&1
    EXEC_EXIT=$?
    echo "execution_integrity exit code: ${EXEC_EXIT}" >> "$HEALTH_LOG"
    # Treat warnings as informational; fail only on critical integrity errors.
    if [ "${HEALTH_EXIT:-1}" -eq 0 ] && [ "$EXEC_EXIT" -ge 2 ]; then
        HEALTH_EXIT=$EXEC_EXIT
    fi
fi

if [ -f "$TRUTH_SNAPSHOT_SCRIPT" ]; then
    echo "--- truth_snapshot ---" >> "$HEALTH_LOG"
    python3 "$TRUTH_SNAPSHOT_SCRIPT" >> "$TRUTH_STREAM_LOG" 2>&1
    SNAP_EXIT=$?
    echo "truth_snapshot exit code: ${SNAP_EXIT}" >> "$HEALTH_LOG"
fi

if [ -x "$RUNTIME_STATUS" ]; then
    echo "--- runtime_status ---" >> "$HEALTH_LOG"
    "$RUNTIME_STATUS" >> "$HEALTH_LOG" 2>&1
    STATUS_EXIT=$?
    echo "runtime_status exit code: ${STATUS_EXIT}" >> "$HEALTH_LOG"
    # Propagate only critical runtime failures (exit 2+).
    # Degraded (exit 1) is logged but does not fail the health-check job.
    if [ "${HEALTH_EXIT:-1}" -eq 0 ] && [ "$STATUS_EXIT" -ge 2 ]; then
        HEALTH_EXIT=$STATUS_EXIT
    fi
fi

# Self-heal critical failures by restarting the main service once.
if [ "${HEALTH_EXIT:-1}" -ge 2 ]; then
    echo "--- auto_remediation ---" >> "$HEALTH_LOG"
    echo "Critical health failure detected (exit=${HEALTH_EXIT}). Restarting $SERVICE_NAME..." >> "$HEALTH_LOG"
    systemctl restart "$SERVICE_NAME" >> "$HEALTH_LOG" 2>&1 || true
    sleep 3
    if systemctl is-active --quiet "$SERVICE_NAME"; then
        echo "Auto-remediation: restart successful" >> "$HEALTH_LOG"
        # Mark remediation success as degraded (not critical) for this pass.
        HEALTH_EXIT=1
    else
        echo "Auto-remediation: restart failed" >> "$HEALTH_LOG"
    fi
fi

echo "" >> "$HEALTH_LOG"

exit ${HEALTH_EXIT:-1}
