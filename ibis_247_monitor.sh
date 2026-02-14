#!/bin/bash

# IBIS True Agent 24/7 Monitoring System
# Includes health checks, recovery, and performance metrics

LOG_FILE="ibis_247_monitor.log"
DB_FILE="data/ibis_v8.db"
STATE_FILE="data/ibis_true_state.json"
AGENT_LOG="ibis_true_agent.log"
BATCH_LOG="batch_monitor.log"

# Configuration
MAX_CRASHES=3
CRASH_WINDOW=300  # 5 minutes
MAX_DB_LAG=300  # 5 minutes
MIN_MEMORY=50000  # KB
MAX_CPU=90  # %
MAX_TRADE_GAP=1800  # 30 minutes

# Function to log messages
log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" >> "$LOG_FILE"
}

# Check if file is recent
is_recent() {
    local file_path="$1"
    local max_age="$2"
    local file_time=$(stat -c %Y "$file_path" 2>/dev/null || echo 0)
    local current_time=$(date +%s)
    
    return $(( current_time - file_time > max_age ))
}

# Check system health
check_health() {
    local health_score=100
    
    # Check if all core files exist
    for file in "$DB_FILE" "$STATE_FILE" "$AGENT_LOG"; do
        if [ ! -f "$file" ]; then
            log "ERROR: File not found - $file"
            health_score=$((health_score - 30))
        fi
    done
    
    # Check database connectivity
    if ! sqlite3 "$DB_FILE" "SELECT 1;" 2>/dev/null; then
        log "ERROR: Database connectivity failed"
        health_score=0
    fi
    
    # Check database state
    POSITION_COUNT=$(sqlite3 "$DB_FILE" "SELECT COUNT(*) FROM positions;" 2>/dev/null)
    if [ "$POSITION_COUNT" -lt 5 ]; then
        log "WARNING: Low position count - $POSITION_COUNT"
        health_score=$((health_score - 20))
    fi
    
    # Check agent log activity
    if is_recent "$AGENT_LOG" $((MAX_TRADE_GAP / 2)); then
        log "WARNING: Agent log not updated in over $((MAX_TRADE_GAP / 2 / 60)) minutes"
        health_score=$((health_score - 15))
    fi
    
    # Check agent process
    AGENT_PID=$(ps aux | grep -v grep | grep "python3 -u ibis_true_agent.py" | awk '{print $2}')
    if [ -z "$AGENT_PID" ]; then
        log "CRITICAL: Agent process not running"
        health_score=0
    else
        # Check agent resources
        CPU_USAGE=$(ps -o %cpu -p "$AGENT_PID" 2>/dev/null | grep -v %cpu)
        MEM_USAGE=$(ps -o rss -p "$AGENT_PID" 2>/dev/null | grep -v RSS)
        
        if (( $(echo "$CPU_USAGE > $MAX_CPU" | bc -l) )); then
            log "WARNING: Agent CPU usage too high - ${CPU_USAGE%.*}%"
            health_score=$((health_score - 25))
        fi
        
        if [ "$MEM_USAGE" -gt $((1024 * 1024)) ]; then  # >1GB
            log "WARNING: Agent memory usage too high - $((MEM_USAGE / 1024)) MB"
            health_score=$((health_score - 20))
        fi
    fi
    
    return $health_score
}

# Attempt to restart agent
restart_agent() {
    log "INFO: Attempting agent restart"
    
    # Stop any existing agent processes
    pkill -f "python3 -u ibis_true_agent.py" 2>/dev/null
    sleep 2
    
    # Clean up old PID file
    rm -f ibis_true_agent.pid
    
    # Start new agent process
    nohup python3 -u ibis_true_agent.py > ibis_true_agent.log 2>&1 < /dev/null &
    AGENT_PID=$!
    
    if [ $? -eq 0 ]; then
        echo $AGENT_PID > ibis_true_agent.pid
        log "SUCCESS: Agent restarted with PID $AGENT_PID"
    else
        log "ERROR: Agent restart failed"
    fi
}

# Recover database from state file
recover_database() {
    log "INFO: Recovering database from state file"
    
    if [ ! -f "$STATE_FILE" ]; then
        log "ERROR: State file not found for recovery"
        return 1
    fi
    
    # Clean existing database and recreate from state file
    rm -f "$DB_FILE"
    python3 << 'PYTHON'
import json
import sqlite3
from datetime import datetime

with open('data/ibis_true_state.json', 'r') as f:
    state = json.load(f)

conn = sqlite3.connect('data/ibis_v8.db')
cursor = conn.cursor()

# Create tables
cursor.execute('''
    CREATE TABLE IF NOT EXISTS positions (
        symbol TEXT PRIMARY KEY,
        quantity REAL,
        entry_price REAL,
        current_price REAL,
        unrealized_pnl REAL,
        unrealized_pnl_pct REAL,
        opened_at TIMESTAMP,
        mode TEXT
    )
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS trades (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        symbol TEXT,
        side TEXT,
        quantity REAL,
        price REAL,
        fees REAL,
        timestamp TIMESTAMP,
        pnl REAL,
        pnl_pct REAL,
        reason TEXT
    )
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS system_state (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TIMESTAMP,
        market_regime TEXT,
        capital_awareness TEXT,
        performance TEXT
    )
''')

# Insert positions
for symbol, pos in state['positions'].items():
    cursor.execute('''
        INSERT INTO positions (symbol, quantity, entry_price, current_price, unrealized_pnl, 
                               unrealized_pnl_pct, opened_at, mode)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        f"{symbol}-USDT",
        pos['quantity'],
        pos['buy_price'],
        pos['current_price'],
        0,
        0,
        datetime.now(),
        state['agent_mode']
    ))

conn.commit()
conn.close()
PYTHON

    if [ $? -eq 0 ]; then
        log "SUCCESS: Database recovered from state file"
    else
        log "ERROR: Database recovery failed"
    fi
}

# Check and clean up old files
clean_up() {
    log "INFO: Checking for old files"
    
    # Rotate log files larger than 100MB
    for log_file in "$LOG_FILE" "$AGENT_LOG" "$BATCH_LOG"; do
        if [ -f "$log_file" ]; then
            FILE_SIZE=$(stat -c %s "$log_file" 2>/dev/null)
            if [ "$FILE_SIZE" -gt $((100 * 1024 * 1024)) ]; then
                mv "$log_file" "$log_file.old"
                log "INFO: Rotated large log file - $log_file"
            fi
        fi
    done
    
    # Clean up temporary files
    rm -f *.tmp 2>/dev/null
}

# Main monitoring loop
echo "=== IBIS TRUE AGENT 24/7 MONITOR ===" >> "$LOG_FILE"
echo "Started: $(date '+%Y-%m-%d %H:%M:%S')" >> "$LOG_FILE"
echo "Configuration: MAX_CRASHES=$MAX_CRASHES, CRASH_WINDOW=$CRASH_WINDOW, MAX_DB_LAG=$MAX_DB_LAG" >> "$LOG_FILE"

CRASH_COUNT=0
LAST_CRASH_TIME=$(date +%s)

while true; do
    CURRENT_TIME=$(date +%s)
    
    # Check health
    HEALTH=$(check_health)
    
    if [ $HEALTH -lt 60 ]; then
        log "CRITICAL: Health score $HEALTH - initiating recovery"
        
        CRASH_COUNT=$((CRASH_COUNT + 1))
        
        if [ $CRASH_COUNT -ge $MAX_CRASHES ]; then
            ELAPSED=$((CURRENT_TIME - LAST_CRASH_TIME))
            if [ $ELAPSED -lt $CRASH_WINDOW ]; then
                log "CRITICAL: Too many crashes in short window - performing full recovery"
                recover_database
                sleep 10
            fi
            LAST_CRASH_TIME=$CURRENT_TIME
            CRASH_COUNT=0
        fi
        
        restart_agent
        sleep 60
    else
        log "HEALTHY: System running normally (score: $HEALTH)"
    fi
    
    # Run batch monitor
    ./batch_monitor.sh >> "$BATCH_LOG"
    
    # Clean up old files
    clean_up
    
    # Wait 5 minutes for next check
    sleep 300
done
