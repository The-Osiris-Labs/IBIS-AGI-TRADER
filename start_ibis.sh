#!/bin/bash
# IBIS Startup Script
# Run IBIS True Agent with optional watchdog

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

case "$1" in
    watchdog)
        echo "Starting IBIS with watchdog (auto-restart)..."
        python3 ibis_watchdog.py
        ;;
    systemd)
        echo "Installing systemd service..."
        cp deploy/ibis.service /etc/systemd/system/
        systemctl daemon-reload
        systemctl enable ibis
        systemctl start ibis
        echo "IBIS service installed and started"
        ;;
    stop)
        echo "Stopping IBIS..."
        pkill -f "ibis_true_agent.py" || true
        pkill -f "ibis_watchdog.py" || true
        echo "IBIS stopped"
        ;;
    status)
        if pgrep -f "ibis_true_agent.py" > /dev/null; then
            echo "IBIS is running"
        else
            echo "IBIS is NOT running"
        fi
        ;;
    *)
        echo "IBIS True Autonomous Trading Agent"
        echo ""
        echo "Usage: $0 {watchdog|systemd|stop|status}"
        echo ""
        echo "  watchdog  - Run agent with auto-restart watchdog"
        echo "  systemd   - Install and start as systemd service (24/7)"
        echo "  stop      - Stop all IBIS processes"
        echo "  status    - Check if IBIS is running"
        ;;
esac
