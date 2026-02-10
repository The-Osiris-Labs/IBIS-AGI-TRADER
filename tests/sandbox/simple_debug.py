#!/usr/bin/env python3
"""Simple debug to check if IBIS is executing trades on valid opportunities"""

import sys
import asyncio
import os

sys.path.append(".")

from ibis_true_agent import IBISTrueAgent


async def simple_debug():
    """Simple debug to verify opportunity processing"""
    print("=== IBIS True Agent Simple Debug ===")

    # Initialize agent for debugging
    agent = IBISTrueAgent()
    await agent.initialize()

    print(f"\nActive Positions: {len(agent.state['positions'])}")
    if agent.state["positions"]:
        for symbol, pos in agent.state["positions"].items():
            print(f"  - {symbol}: ${pos['current_value']:.2f}")

    # Get current strategy directly
    from ibis.core.trading_constants import TRADING

    strategy = {
        "available": agent.state["capital_awareness"]["real_trading_capital"],
        "max_positions": TRADING.POSITION.MAX_TOTAL_POSITIONS,
        "confidence_threshold": TRADING.SCORE.MIN_THRESHOLD,
    }

    print(f"\nStrategy Configuration:")
    print(f"Available Capital: ${strategy['available']:.2f}")
    print(f"Max Positions: {strategy['max_positions']}")
    print(f"Confidence Threshold: {strategy['confidence_threshold']}")

    # Find opportunities
    opportunities = await agent.find_all_opportunities(strategy)
    print(f"\nFound {len(opportunities)} tradeable opportunities")

    if opportunities:
        print("\nTop 5 Opportunities:")
        for i, opp in enumerate(opportunities[:5]):
            print(f"  {i + 1}. {opp['symbol']}: Score {opp['adjusted_score']:.1f}")

    await agent.close()


async def main():
    try:
        await simple_debug()
    except Exception as e:
        print(f"\n❌ Debug failed: {e}")
        import traceback

        print(f"Stack trace: {traceback.format_exc()}")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nDebug interrupted")
