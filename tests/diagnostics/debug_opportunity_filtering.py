#!/usr/bin/env python3
"""Debug script to check why IBIS isn't executing trades on valid opportunities"""

import sys
import asyncio
import os

sys.path.append(".")

from ibis_true_agent import IBISTrueAgent
from ibis.exchange.kucoin_client import get_kucoin_client


async def debug_opportunity_filtering():
    """Debug why opportunities aren't being marked as tradeable"""
    print("=== IBIS True Agent Opportunity Filtering Debug ===")

    # Initialize agent for debugging
    agent = IBISTrueAgent()
    await agent.initialize()

    print("\n=== Current State ===")
    print(f"Active Positions: {len(agent.state['positions'])}")
    if agent.state["positions"]:
        print("Held Symbols:")
        for symbol, pos in agent.state["positions"].items():
            print(f"  - {symbol}")

    print("\n=== Market Intel Analysis ===")
    print(f"Market Intel Entries: {len(agent.market_intel)}")

    # Get top opportunities
    sorted_opps = sorted(
        agent.market_intel.items(), key=lambda x: x[1]["score"], reverse=True
    )

    print("\nTop 10 Opportunities:")
    for sym, intel in sorted_opps[:10]:
        print(f"  - {sym}: Score {intel['score']:.1f}, Price ${intel['price']:.4f}")

    print("\n=== Strategy Configuration ===")
    strategy = await agent.get_strategy()
    print(f"Available Capital: ${strategy['available']:.2f}")
    print(f"Max Positions: {strategy['max_positions']}")
    print(f"Confidence Threshold: {strategy['confidence_threshold']}")

    print("\n=== Finding All Opportunities ===")
    opportunities = await agent.find_all_opportunities(strategy)
    print(f"Found {len(opportunities)} tradeable opportunities")

    if opportunities:
        print("\nTradeable Opportunities:")
        for opp in opportunities:
            print(f"  - {opp['symbol']}: Score {opp['score']:.1f}")

    await agent.close()
    return len(opportunities)


async def main():
    try:
        tradeable_count = await debug_opportunity_filtering()

        if tradeable_count == 0:
            print("\n❌ No tradeable opportunities found!")
            print("Possible reasons:")
            print("1. All high-scoring symbols are already in portfolio")
            print("2. Opportunity scores don't meet threshold")
            print("3. Low liquidity/volume filtering")
            print("4. Spread too wide for trading")
        else:
            print(f"\n✅ Found {tradeable_count} tradeable opportunities!")

    except Exception as e:
        print(f"\n❌ Debug failed: {e}")
        import traceback

        print(f"Stack trace: {traceback.format_exc()}")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nDebug interrupted")
