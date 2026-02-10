#!/usr/bin/env python3
"""
🦅 IBIS TRUE AUTONOMOUS AGENT - ENTRY POINT
============================================
Full AGI Trading System with:
- Multi-source intelligence (FreeIntelligence)
- AGI Brain (6 reasoning models)
- Cross-exchange monitoring
- Self-learning & adaptive risk
- Alpha recycling

Usage:
  python3 main.py           # Run TRUE AGI agent
"""

import asyncio
import logging
import signal
import sys
from ibis_true_agent import IBISTrueAgent

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("IBIS_MAIN")


async def main():
    logger.info("=" * 70)
    logger.info("🦅 IBIS TRUE AUTONOMOUS AGENT v3.1 - FULL AGI TRADING")
    logger.info("=" * 70)
    logger.info("🚀 Initializing AGI Brain, FreeIntelligence, Cross-Exchange...")

    agent = IBISTrueAgent()

    loop = asyncio.get_running_loop()
    stop_event = asyncio.Event()

    def signal_handler():
        logger.info("🛑 SHUTDOWN SIGNAL RECEIVED")
        stop_event.set()

    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, signal_handler)

    try:
        task = asyncio.create_task(agent.run())
        await stop_event.wait()

        if not task.done():
            try:
                await asyncio.wait_for(task, timeout=10)
            except asyncio.TimeoutError:
                logger.warning("⚠️ Task timeout during shutdown")

    except Exception as e:
        logger.error(f"❌ CRITICAL ERROR: {e}", exc_info=True)
        sys.exit(1)

    logger.info("✅ IBIS AGI Halted cleanly")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
