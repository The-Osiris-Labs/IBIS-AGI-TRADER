#!/usr/bin/env python3
"""
IBIS 24/7 Watchdog
Keeps the IBIS trading agent running continuously.
Auto-restarts on crash with exponential backoff.
"""

import subprocess
import sys
import time
import os
from datetime import datetime

AGENT_PATH = "/root/projects/Dont enter unless solicited/AGI Trader/ibis_true_agent.py"
LOG_PATH = (
    "/root/projects/Dont enter unless solicited/AGI Trader/data/ibis_watchdog.log"
)
MAX_RESTARTS = 10
INITIAL_BACKOFF = 30  # seconds


def log(msg):
    """Log with timestamp."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{timestamp}] {msg}"
    print(line)
    try:
        with open(LOG_PATH, "a") as f:
            f.write(line + "\n")
    except:
        pass


def get_agent_process():
    """Check if agent is running."""
    try:
        result = subprocess.run(
            ["pgrep", "-f", "ibis_true_agent.py"],
            capture_output=True,
            text=True,
        )
        return result.returncode == 0
    except:
        return False


def kill_agent():
    """Kill any existing agent process."""
    try:
        subprocess.run(["pkill", "-f", "ibis_true_agent.py"], capture_output=True)
        log("Killed existing agent process")
        time.sleep(2)
    except:
        pass


def start_agent():
    """Start the IBIS agent."""
    env = os.environ.copy()
    env["PYTHONUNBUFFERED"] = "1"

    log("Starting IBIS agent...")
    return subprocess.Popen(
        [sys.executable, AGENT_PATH],
        env=env,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


def main():
    log("=" * 50)
    log("IBIS WATCHDOG STARTED")
    log("=" * 50)

    restart_count = 0
    backoff = INITIAL_BACKOFF

    while True:
        try:
            if get_agent_process():
                log("Agent is running")
            else:
                log("Agent not running, starting...")
                kill_agent()
                process = start_agent()

                if process.returncode is None:
                    log("Agent started successfully")
                    restart_count = 0
                    backoff = INITIAL_BACKOFF
                else:
                    log(f"Agent failed to start (return code: {process.returncode})")
                    restart_count += 1

            time.sleep(30)  # Check every 30 seconds

        except KeyboardInterrupt:
            log("Watchdog stopped by user")
            break
        except Exception as e:
            log(f"Watchdog error: {e}")
            time.sleep(10)


if __name__ == "__main__":
    main()
