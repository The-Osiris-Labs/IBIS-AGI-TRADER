#!/usr/bin/env python3
"""
IBIS v2 - ENHANCED ENTRY POINT
Main Entry Point with Enhanced Error Recovery.

Usage:
  python3 run_v2.py
"""

import asyncio
import logging
import signal
import sys
from ibis.execution.engine_v2 import EnhancedExecutionEngine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("IBIS_V2")


async def main():
    logger.info("=" * 60)
    logger.info("🦅 IBIS v2 ENHANCED TRADING SYSTEM")
    logger.info("=" * 60)

    engine = EnhancedExecutionEngine()

    loop = asyncio.get_running_loop()
    stop_event = asyncio.Event()

    def signal_handler():
        logger.info("🛑 SHUTDOWN SIGNAL RECEIVED")
        stop_event.set()

    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, signal_handler)

    try:
        task = asyncio.create_task(engine.run())
        await stop_event.wait()
        await engine.shutdown()
        await task
    except Exception as e:
        logger.error(f"❌ CRITICAL ERROR: {e}", exc_info=True)
        sys.exit(1)

    logger.info("✅ IBIS v2 Halted cleanly")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
