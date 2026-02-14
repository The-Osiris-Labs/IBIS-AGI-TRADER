#!/bin/bash

# IBIS True Agent Watchdog
# Ensures the agent runs continuously 24/7

AGENT_DIR="/root/projects/Dont enter unless solicited/AGI Trader"
AGENT_LOG="$AGENT_DIR/agent_monitor.log"
PID_FILE="$AGENT_DIR/ibis_true_agent.pid"
AGENT_CMD="python3 -u $AGENT_DIR/ibis_true_agent.py > $AGENT_DIR/ibis_true_agent.log 2>&1 < /dev/null"

# Function to log messages
log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" >> "$AGENT_LOG"
}

# Function to check if agent is running
is_agent_running() {
    if [ -f "$PID_FILE" ]; then
        local PID=$(cat "$PID_FILE" 2>/dev/null)
        if [ -n "$PID" ]; then
            if kill -0 "$PID" 2>/dev/null; then
                # Check if it's actually the agent process
                if ps -p "$PID" -o cmd | grep -q "python.*ibis_true_agent"; then
                    return 0 # Running
                fi
            fi
        fi
    fi
    return 1 # Not running
}

# Function to start the agent
start_agent() {
    log "Starting IBIS True Agent..."
    cd "$AGENT_DIR" || exit 1
    nohup $AGENT_CMD &
    local PID=$!
    if [ $? -eq 0 ]; then
        echo $PID > "$PID_FILE"
        log "Agent started successfully (PID: $PID)"
        return 0
    else
        log "Failed to start agent"
        return 1
    fi
}

# Function to check agent health
check_agent_health() {
    local PID=$(cat "$PID_FILE" 2>/dev/null)
    if [ -n "$PID" ]; then
        # Check if log file is being updated
        local log_time=$(stat "$AGENT_DIR/ibis_true_agent.log" 2>/dev/null | grep Modify | awk '{print $2" "$3}')
        if [ -z "$log_time" ]; then
            log "Agent log file not being updated - restarting"
            return 1
        fi
        
        local log_seconds=$(date -d "$log_time" +%s 2>/dev/null)
        local current_seconds=$(date +%s)
        local log_age=$((current_seconds - log_seconds))
        
        # If log hasn't been updated in 5 minutes, restart
        if [ $log_age -gt 300 ]; then
            log "Agent log hasn't been updated in $log_age seconds - restarting"
            kill -9 "$PID" 2>/dev/null
            rm -f "$PID_FILE"
            return 1
        fi
    fi
    return 0
}

# Main watchdog loop
log "Watchdog started - monitoring IBIS True Agent"

while true; do
    if ! is_agent_running; then
        log "Agent is not running - starting now"
        start_agent
    else
        if ! check_agent_health; then
            log "Agent is unhealthy - restarting"
            start_agent
        fi
    fi
    # Sleep for 1 minute before next check
    sleep 60
done