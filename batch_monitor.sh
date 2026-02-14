#!/bin/bash

# Batch Write System Monitor
# Runs every 5 minutes to check system health

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MONITOR_LOG="$SCRIPT_DIR/batch_monitor.log"
DB_FILE="$SCRIPT_DIR/data/ibis_v8.db"
STATE_FILE="$SCRIPT_DIR/data/ibis_true_state.json"
AGENT_REGEX="/root/projects/(ibis_trader|Dont enter unless solicited/AGI Trader)/ibis_true_agent.py"

# Function to log messages
log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" >> "$MONITOR_LOG"
}

find_agent_pid() {
    pgrep -f "$AGENT_REGEX" 2>/dev/null | head -n 1
}

# Check if batch writer is active by tracking file writes
check_system_activity() {
    if [ -f "$STATE_FILE" ]; then
        STATE_MOD=$(stat -c %Y "$STATE_FILE" 2>/dev/null)
        DB_MOD=$(stat -c %Y "$DB_FILE" 2>/dev/null)
        
        CURRENT_TIME=$(date +%s)
        STATE_AGE=$((CURRENT_TIME - STATE_MOD))
        DB_AGE=$((CURRENT_TIME - DB_MOD))
        
        echo "=== System Activity ==="
        echo "State file modified: $((STATE_AGE / 60)) minutes ago"
        echo "Database modified: $((DB_AGE / 60)) minutes ago"
        echo ""
    fi
}

# Check database state
check_database() {
    if [ -f "$DB_FILE" ]; then
        echo "=== Database Status ==="
        local has_positions has_trades
        has_positions=$(sqlite3 "$DB_FILE" "SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name='positions';" 2>/dev/null)
        has_trades=$(sqlite3 "$DB_FILE" "SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name='trades';" 2>/dev/null)

        POSITION_COUNT=0
        TRADE_COUNT=0
        if [ "$has_positions" = "1" ]; then
            POSITION_COUNT=$(sqlite3 "$DB_FILE" "SELECT COUNT(*) FROM positions;" 2>/dev/null)
            POSITION_COUNT=${POSITION_COUNT:-0}
        fi
        if [ "$has_trades" = "1" ]; then
            TRADE_COUNT=$(sqlite3 "$DB_FILE" "SELECT COUNT(*) FROM trades;" 2>/dev/null)
            TRADE_COUNT=${TRADE_COUNT:-0}
        fi
        
        echo "Positions: $POSITION_COUNT"
        echo "Trades: $TRADE_COUNT"
        
        # Check for negative positions
        NEGATIVE_POSITIONS=0
        if [ "$has_positions" = "1" ]; then
            NEGATIVE_POSITIONS=$(sqlite3 "$DB_FILE" "SELECT COUNT(*) FROM positions WHERE quantity < 0;" 2>/dev/null)
            NEGATIVE_POSITIONS=${NEGATIVE_POSITIONS:-0}
        fi
        if [ "$NEGATIVE_POSITIONS" -gt 0 ]; then
            echo "⚠️ Negative positions: $NEGATIVE_POSITIONS"
        fi
        echo ""
    fi
}

# Check agent process
check_agent() {
    echo "=== Agent Status ==="
    
    AGENT_PID=$(find_agent_pid || true)
    if [ -n "$AGENT_PID" ]; then
        echo "Agent PID: $AGENT_PID"
        
        # Check CPU and memory
        AGENT_STATS=$(ps -o %cpu,%mem -p "$AGENT_PID" 2>/dev/null)
        if [ $? -eq 0 ]; then
            echo "$AGENT_STATS"
        fi
    else
        if systemctl is-active --quiet ibis-agent.service 2>/dev/null; then
            echo "⚠️ Agent PID not found by pattern, but ibis-agent.service is active"
        else
            echo "⚠️ Agent process not found"
        fi
    fi
}

# Main monitoring loop
echo "=== BATCH WRITE MONITOR ==="
echo "Generated: $(date '+%Y-%m-%d %H:%M:%S')"

check_system_activity
check_database
check_agent

echo ""
echo "---"
