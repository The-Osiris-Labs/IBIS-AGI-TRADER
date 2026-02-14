#!/bin/bash

# IBIS True Agent Health Check
# Runs every 15 minutes to ensure agent is healthy

AGENT_DIR="/root/projects/Dont enter unless solicited/AGI Trader"
HEALTH_LOG="$AGENT_DIR/health_check.log"
HEALTH_CHECK="$AGENT_DIR/check_agent_health.sh"

# Log health check
echo "=== Health Check: $(date '+%Y-%m-%d %H:%M:%S') ===" >> "$HEALTH_LOG"

# Run health check
if [ -f "$HEALTH_CHECK" ]; then
    if [ -x "$HEALTH_CHECK" ]; then
        cd "$AGENT_DIR" || exit 1
        ./check_agent_health.sh >> "$HEALTH_LOG" 2>&1
    else
        chmod +x "$HEALTH_CHECK"
        cd "$AGENT_DIR" || exit 1
        ./check_agent_health.sh >> "$HEALTH_LOG" 2>&1
    fi
else
    echo "Health check script not found: $HEALTH_CHECK" >> "$HEALTH_LOG"
    exit 1
fi

echo "" >> "$HEALTH_LOG"