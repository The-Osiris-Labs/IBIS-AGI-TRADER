#!/bin/bash

# Unified runtime diagnostics for IBIS production operation.

set -u

BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
STATE_FILE="$BASE_DIR/data/ibis_true_state.json"
DB_FILE="$BASE_DIR/data/ibis_v8.db"
TRADE_HISTORY_FILE="$BASE_DIR/data/trade_history.json"
SERVICE_NAME="ibis-agent.service"
AGENT_REGEX="/root/projects/(ibis_trader|Dont enter unless solicited/AGI Trader)/ibis_true_agent.py"

now_ts=$(date +%s)
critical=0
degraded=0

print_age_minutes() {
    local file="$1"
    if [ ! -f "$file" ]; then
        echo "missing"
        return
    fi
    local ts
    ts=$(stat -c %Y "$file" 2>/dev/null || echo 0)
    if [ "$ts" -le 0 ]; then
        echo "unknown"
        return
    fi
    echo $(( (now_ts - ts) / 60 ))
}

echo "=== IBIS Runtime Status ==="
echo "time: $(date '+%Y-%m-%d %H:%M:%S %Z')"
echo "base_dir: $BASE_DIR"
echo ""

service_active="unknown"
service_enabled="unknown"
if systemctl show "$SERVICE_NAME" >/dev/null 2>&1; then
    if systemctl is-active --quiet "$SERVICE_NAME" 2>/dev/null; then
        service_active="active"
    else
        service_active="inactive"
    fi
    if systemctl is-enabled --quiet "$SERVICE_NAME" 2>/dev/null; then
        service_enabled="enabled"
    else
        service_enabled="disabled"
    fi
else
    service_active="unavailable_to_query"
    service_enabled="unavailable_to_query"
fi
echo "service_active: $service_active"
echo "service_enabled: $service_enabled"

agent_pid=$(pgrep -f "$AGENT_REGEX" 2>/dev/null | head -n 1 || true)
if [ -n "$agent_pid" ]; then
    agent_etime=$(ps -p "$agent_pid" -o etime= 2>/dev/null | xargs)
    agent_cmd=$(ps -p "$agent_pid" -o cmd= 2>/dev/null)
    echo "agent_pid: $agent_pid"
    echo "agent_uptime: ${agent_etime:-unknown}"
    echo "agent_cmd: ${agent_cmd:-unknown}"
else
    echo "agent_pid: none"
    critical=1
fi
echo ""

state_age_min=$(print_age_minutes "$STATE_FILE")
db_age_min=$(print_age_minutes "$DB_FILE")
echo "state_file_age_min: $state_age_min"
echo "db_file_age_min: $db_age_min"

state_positions=0
db_positions=0
db_trades=0
trade_history_records=0
if [ -f "$STATE_FILE" ]; then
    state_positions=$(jq '.positions | length' "$STATE_FILE" 2>/dev/null || echo 0)
fi
if [ -f "$DB_FILE" ]; then
    has_positions=$(sqlite3 "$DB_FILE" "SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name='positions';" 2>/dev/null || echo 0)
    has_trades=$(sqlite3 "$DB_FILE" "SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name='trades';" 2>/dev/null || echo 0)
    if [ "$has_positions" = "1" ]; then
        db_positions=$(sqlite3 "$DB_FILE" "SELECT COUNT(*) FROM positions;" 2>/dev/null || echo 0)
    fi
    if [ "$has_trades" = "1" ]; then
        db_trades=$(sqlite3 "$DB_FILE" "SELECT COUNT(*) FROM trades;" 2>/dev/null || echo 0)
    fi
fi
if [ -f "$TRADE_HISTORY_FILE" ]; then
    # Supports both {"trades":[...]} and bare [...] layouts.
    trade_history_records=$(jq 'if type=="object" then (.trades // [] | length) elif type=="array" then length else 0 end' "$TRADE_HISTORY_FILE" 2>/dev/null || echo 0)
fi
echo "state_positions: $state_positions"
echo "db_positions: $db_positions"
echo "db_trades: $db_trades"
echo "trade_history_records: $trade_history_records"

if [ "$state_positions" != "$db_positions" ]; then
    echo "warning: position_count_mismatch=1"
fi
if [ "$trade_history_records" -gt 0 ] && [ "$db_trades" -lt "$trade_history_records" ]; then
    echo "note: db_trades_lagging_trade_history=1"
fi

if [ -x "$BASE_DIR/tools/check_credentials_source.sh" ]; then
    echo ""
    "$BASE_DIR/tools/check_credentials_source.sh"
    creds_rc=$?
    if [ "$creds_rc" -ne 0 ]; then
        degraded=1
        echo "warning: credential_restart_survivability=at_risk"
    fi
fi

if [ -x "$BASE_DIR/tools/deep_state_audit.py" ]; then
    echo ""
    "$BASE_DIR/tools/deep_state_audit.py" --live-exchange
    audit_rc=$?
    if [ "$audit_rc" -eq 2 ]; then
        critical=1
        echo "warning: deep_state_audit=critical"
    elif [ "$audit_rc" -eq 1 ]; then
        degraded=1
        echo "warning: deep_state_audit=warnings"
    fi
fi

echo ""
if [ "$service_active" = "inactive" ] && [ -z "${agent_pid:-}" ]; then
    echo "overall: CRITICAL"
    exit 2
fi
if [ "$critical" -eq 1 ]; then
    echo "overall: CRITICAL"
    exit 2
fi
if [ "$degraded" -eq 1 ]; then
    echo "overall: DEGRADED"
    exit 1
fi
echo "overall: OK"
exit 0
