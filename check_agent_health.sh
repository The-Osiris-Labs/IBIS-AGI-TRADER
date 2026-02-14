#!/bin/bash

# IBIS True Agent Health Check
# Verifies the agent is running and getting real-time data

AGENT_DIR="/root/projects/Dont enter unless solicited/AGI Trader"
AGENT_LOG="$AGENT_DIR/ibis_true_agent.log"
PID_FILE="$AGENT_DIR/ibis_true_agent.pid"

# Check if agent is running
if [ ! -f "$PID_FILE" ]; then
    echo "❌ PID file not found"
    exit 1
fi

PID=$(cat "$PID_FILE")
if ! kill -0 $PID 2>/dev/null; then
    echo "❌ Agent process (PID: $PID) not running"
    exit 1
fi

# Check log file activity
if [ ! -f "$AGENT_LOG" ]; then
    echo "❌ Agent log file not found"
    exit 1
fi

LOG_TIME=$(stat "$AGENT_LOG" 2>/dev/null | grep Modify | awk '{print $2" "$3}')
if [ -z "$LOG_TIME" ]; then
    echo "❌ Log file modification time not available"
    exit 1
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
    echo "❌ No recent activity in log"
    exit 1
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