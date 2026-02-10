#!/usr/bin/env python3
"""Quick test to see if agent is running and logging"""

import sys
import asyncio
import os

sys.path.append(".")

from ibis_true_agent import IBISTrueAgent


async def quick_test():
    """Quick test to verify agent functionality"""
    print("=== IBIS True Agent Quick Test ===")

    # Initialize agent
    agent = IBISTrueAgent()
    await agent.initialize()

    print(f"\nAgent Initialization: SUCCESS")
    print(f"Process PID: {os.getpid()}")

    # Check market intel
    print(f"\nMarket Intel Count: {len(agent.market_intel)}")

    # Check strategy
    strategy = {
        "available": agent.state["capital_awareness"]["real_trading_capital"],
        "max_positions": 5,
        "confidence_threshold": 55,
    }

    print(f"\nAvailable Capital: ${strategy['available']:.2f}")
    print(f"Active Positions: {len(agent.state['positions'])}")

    # Find opportunities
    opportunities = await agent.find_all_opportunities(strategy)
    print(f"Tradeable Opportunities: {len(opportunities)}")

    if opportunities:
        print("\nTop 5 Opportunities:")
        for i, opp in enumerate(opportunities[:5]):
            print(f"  {i + 1}. {opp['symbol']}: {opp['adjusted_score']:.1f}")

    # Cleanup
    await agent.client.session.close()
    await agent.free_intel.session.close()
    return len(opportunities)


async def main():
    try:
        count = await quick_test()
        print(f"\n✅ Test completed. Found {count} opportunities.")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback

        print(f"Stack trace: {traceback.format_exc()}")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nTest interrupted")
