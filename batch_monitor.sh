#!/bin/bash

# Batch Write System Monitor
# Runs every 5 minutes to check system health

MONITOR_LOG="batch_monitor.log"
DB_FILE="data/ibis_v8.db"
STATE_FILE="data/ibis_true_state.json"

# Function to log messages
log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" >> "$MONITOR_LOG"
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
        
        POSITION_COUNT=$(sqlite3 "$DB_FILE" "SELECT COUNT(*) FROM positions;" 2>/dev/null)
        TRADE_COUNT=$(sqlite3 "$DB_FILE" "SELECT COUNT(*) FROM trades;" 2>/dev/null)
        
        echo "Positions: $POSITION_COUNT"
        echo "Trades: $TRADE_COUNT"
        
        # Check for negative positions
        NEGATIVE_POSITIONS=$(sqlite3 "$DB_FILE" "SELECT COUNT(*) FROM positions WHERE quantity < 0;" 2>/dev/null)
        if [ "$NEGATIVE_POSITIONS" -gt 0 ]; then
            echo "⚠️ Negative positions: $NEGATIVE_POSITIONS"
        fi
        echo ""
    fi
}

# Check agent process
check_agent() {
    echo "=== Agent Status ==="
    
    AGENT_PID=$(ps aux | grep -v grep | grep "python3 -u ibis_true_agent.py" | awk '{print $2}')
    if [ -n "$AGENT_PID" ]; then
        echo "Agent PID: $AGENT_PID"
        
        # Check CPU and memory
        AGENT_STATS=$(ps -o %cpu,%mem -p "$AGENT_PID" 2>/dev/null)
        if [ $? -eq 0 ]; then
            echo "$AGENT_STATS"
        fi
    else
        echo "⚠️ Agent process not found"
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
