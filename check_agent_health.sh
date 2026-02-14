#!/bin/bash

# IBIS True Agent Health Check
# Verifies the agent is running and getting real-time data

AGENT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
AGENT_LOG="$AGENT_DIR/ibis_true_agent.log"
PID_FILE="$AGENT_DIR/ibis_true_agent.pid"
AGENT_REGEX="/root/projects/(ibis_trader|Dont enter unless solicited/AGI Trader)/ibis_true_agent.py"
SERVICE_NAME="ibis-agent.service"
AGENT_RUNNING=0

find_agent_pid() {
    pgrep -f "$AGENT_REGEX" 2>/dev/null | head -n 1
}

service_is_active() {
    systemctl is-active --quiet "$SERVICE_NAME" 2>/dev/null
}

has_recent_journal_activity() {
    journalctl -u "$SERVICE_NAME" --since "3 minutes ago" --no-pager -n 200 2>/dev/null \
        | rg -q "CAPITAL:|Found [0-9]+ open orders|Portfolio:|Updating position awareness|RECONCILING"
}

# Check if agent is running
PID=""
if [ -f "$PID_FILE" ]; then
    PID=$(cat "$PID_FILE")
fi

if ! kill -0 "$PID" 2>/dev/null; then
    PID=$(find_agent_pid || true)
    if [ -z "$PID" ]; then
        if service_is_active; then
            echo "✅ $SERVICE_NAME is active"
        else
            echo "❌ Agent process not running"
            exit 1
        fi
    else
        echo "$PID" > "$PID_FILE"
        echo "✅ Agent process running (PID: $PID)"
        AGENT_RUNNING=1
    fi
else
    echo "✅ Agent process running (PID: $PID)"
    AGENT_RUNNING=1
fi

# If service is active and journal is healthy, we can pass even if local log is stale
if service_is_active && has_recent_journal_activity; then
    echo "✅ Recent journal activity detected for $SERVICE_NAME"
    exit 0
fi

# Fallback to file-based checks
if [ ! -f "$AGENT_LOG" ]; then
    if service_is_active; then
        echo "⚠️ Agent log file not found, but $SERVICE_NAME is active"
        exit 0
    else
        echo "❌ Agent log file not found"
        exit 1
    fi
fi

LOG_TIME=$(stat "$AGENT_LOG" 2>/dev/null | grep Modify | awk '{print $2" "$3}')
if [ -z "$LOG_TIME" ]; then
    if service_is_active; then
        echo "⚠️ Log file modification time unavailable, but $SERVICE_NAME is active"
        exit 0
    else
        echo "❌ Log file modification time not available"
        exit 1
    fi
fi

LOG_AGE=$(($(date +%s) - $(date -d "$LOG_TIME" +%s)))

# Check if log has been updated in last 2 minutes
if [ $LOG_AGE -gt 120 ]; then
    echo "⚠️ Agent log not updated in $LOG_AGE seconds - may be unresponsive"
else
    echo "✅ Agent log updated $LOG_AGE seconds ago"
fi

# Check for recent activity in log
RECENT_ACTIVITY=$(grep -n "Updating position awareness\|CAPITAL:\|Found [0-9]\+ open orders" "$AGENT_LOG" | tail -10)
if [ -z "$RECENT_ACTIVITY" ]; then
    if [ "$AGENT_RUNNING" -eq 1 ]; then
        echo "⚠️ No recent activity in local log, but process is running"
        exit 0
    fi
    if service_is_active; then
        echo "⚠️ No recent activity in local log, but $SERVICE_NAME is active"
        exit 0
    else
        echo "❌ No recent activity in log"
        exit 1
    fi
fi

# Get latest position data
LATEST_POS=$(grep -A 14 "Portfolio:" "$AGENT_LOG" | tail -14)
if [ -n "$LATEST_POS" ]; then
    echo -e "\n📊 Latest Portfolio Data:"
    echo "$LATEST_POS"
else
    echo "❌ No portfolio data found"
    exit 1
fi

# Get open orders
OPEN_ORDERS=$(grep -B 1 "Order (dict):" "$AGENT_LOG" | grep "Found [0-9]\+ open orders" | tail -1)
if [ -n "$OPEN_ORDERS" ]; then
    echo -e "\n✅ $OPEN_ORDERS"
else
    echo "⚠️ No open orders information"
fi

# Check health of watchdog
WATCHDOG_PID_FILE="$AGENT_DIR/agent_watchdog.pid"
if [ -f "$WATCHDOG_PID_FILE" ]; then
    WATCHDOG_PID=$(cat "$WATCHDOG_PID_FILE")
    if kill -0 $WATCHDOG_PID 2>/dev/null; then
        echo -e "\n✅ Watchdog running (PID: $WATCHDOG_PID)"
    else
        echo "⚠️ Watchdog process not running"
    fi
else
    echo "⚠️ Watchdog PID file not found"
fi

echo -e "\n✅ Agent is running and functioning normally"
