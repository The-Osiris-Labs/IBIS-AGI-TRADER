#!/usr/bin/env python3
"""
IBIS True Agent Monitor
Monitors the agent to ensure it stays running 24/7
"""

import psutil
import subprocess
import time
import os
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    filename="/root/projects/Dont enter unless solicited/AGI Trader/agent_monitor.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)


def is_agent_running():
    """Check if the IBIS True Agent is running"""
    for proc in psutil.process_iter(["cmdline"]):
        if proc.info["cmdline"] and "ibis_true_agent.py" in str(proc.info["cmdline"]):
            return True
    return False


def start_agent():
    """Start the IBIS True Agent"""
    logging.info("Starting IBIS True Agent...")
    try:
        subprocess.Popen(
            ["python3", "ibis_true_agent.py"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            cwd="/root/projects/Dont enter unless solicited/AGI Trader",
        )
        time.sleep(3)
        if is_agent_running():
            logging.info("Agent started successfully")
            return True
        else:
            logging.error("Failed to start agent")
            return False
    except Exception as e:
        logging.error(f"Error starting agent: {e}")
        return False


def check_agent_health():
    """Check agent health by running system health check"""
    try:
        result = subprocess.run(
            [
                "python3",
                "-c",
                'import sys; sys.path.insert(0, "/root/projects/Dont enter unless solicited/AGI Trader"); from ibis.system_health import SystemHealthCheck; c = SystemHealthCheck(); h, i = c.run_all_checks(); print("Healthy:", h); print("Issues:", len(i))',
            ],
            capture_output=True,
            text=True,
            cwd="/root/projects/Dont enter unless solicited/AGI Trader",
        )

        if "Healthy: True" in result.stdout:
            logging.info("System health check passed")
            return True
        else:
            logging.warning(f"System health check issues: {result.stdout}")
            return False
    except Exception as e:
        logging.error(f"Health check failed: {e}")
        return False


def main():
    logging.info("=== IBIS True Agent Monitor Started ===")

    while True:
        try:
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # Check if agent is running
            if not is_agent_running():
                logging.warning(f"[{current_time}] Agent not running - attempting to start")
                start_agent()

            # Check system health
            check_agent_health()

            # Sleep for 5 minutes
            time.sleep(300)

        except Exception as e:
            logging.error(f"Monitor error: {e}")
            time.sleep(60)  # Retry after 1 minute


if __name__ == "__main__":
    main()
