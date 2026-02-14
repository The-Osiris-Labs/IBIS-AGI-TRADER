#!/bin/bash

# IBIS True Agent Watchdog
# Ensures the agent runs continuously 24/7

AGENT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
AGENT_LOG="$AGENT_DIR/agent_monitor.log"
PID_FILE="$AGENT_DIR/ibis_true_agent.pid"
AGENT_REGEX="/root/projects/(ibis_trader|Dont enter unless solicited/AGI Trader)/ibis_true_agent.py"
AGENT_CMD="python3 -u \"$AGENT_DIR/ibis_true_agent.py\" > \"$AGENT_DIR/ibis_true_agent.log\" 2>&1 < /dev/null"
LOCK_FILE="$AGENT_DIR/data/agent_watchdog.lock"
SERVICE_NAME="ibis-agent.service"

# Function to log messages
log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" >> "$AGENT_LOG"
}

service_is_active() {
    systemctl is-active --quiet "$SERVICE_NAME" 2>/dev/null
}

load_env_files() {
    for env_file in "$AGENT_DIR/keys.env" "$AGENT_DIR/ibis/keys.env" "$AGENT_DIR/.env"; do
        if [ -f "$env_file" ]; then
            set -a
            # shellcheck disable=SC1090
            source "$env_file"
            set +a
        fi
    done
}

find_agent_pid() {
    pgrep -f "$AGENT_REGEX" 2>/dev/null | head -n 1
}

# Function to check if agent is running
is_agent_running() {
    local running_pid
    running_pid=$(find_agent_pid || true)
    if [ -n "$running_pid" ]; then
        echo "$running_pid" > "$PID_FILE"
        return 0
    fi

    if [ -f "$PID_FILE" ]; then
        local PID=$(cat "$PID_FILE" 2>/dev/null)
        if [ -n "$PID" ]; then
            if kill -0 "$PID" 2>/dev/null; then
                # Check if it's actually the agent process
                if ps -p "$PID" -o args= | grep -Eq "$AGENT_REGEX"; then
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
    load_env_files
    eval "nohup $AGENT_CMD" &
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
mkdir -p "$AGENT_DIR/data"
exec 9>"$LOCK_FILE"
if ! flock -n 9; then
    log "Watchdog already running, exiting"
    exit 0
fi

if service_is_active; then
    log "$SERVICE_NAME is active; skipping standalone watchdog to avoid supervisor conflicts"
    exit 0
fi

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
