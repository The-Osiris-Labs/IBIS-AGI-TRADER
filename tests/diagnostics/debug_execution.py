#!/usr/bin/env python3
"""Debug script to identify why IBIS True Agent isn't executing trades"""

import sys
import asyncio
import os

sys.path.append(".")

from ibis_true_agent import IBISTrueAgent
from ibis.exchange.kucoin_client import get_kucoin_client


async def debug_execution_barriers():
    """Debug execution barriers by checking current state"""
    print("=== IBIS True Agent Execution Debug ===")
    print("Current time:", asyncio.get_event_loop().time())

    # Initialize agent for debugging
    agent = IBISTrueAgent()
    await agent.initialize()

    print("\n=== Agent Configuration ===")
    print(f"Paper Trading: {agent.paper_trading}")
    print(f"Debug Mode: {agent.debug_mode}")
    print(f"Verbose Mode: {agent.verbose_mode}")

    # Check exchange connection
    client = get_kucoin_client(paper_trading=agent.paper_trading)

    print("\n=== Exchange Status ===")
    try:
        usdt_balance = await client.get_balance("USDT")
        print(f"USDT Balance: ${usdt_balance:.2f}")

        balances = await client.get_all_balances()
        print(f"Total Assets: {len(balances)} assets")
    except Exception as e:
        print(f"❌ Exchange connection error: {e}")

    # Check agent state
    print("\n=== Agent State ===")
    print(f"Active Positions: {len(agent.state.get('positions', []))}")

    if "positions" in agent.state:
        for symbol, pos in agent.state["positions"].items():
            print(f"  - {symbol}: {pos['quantity']:.4f} @ ${pos['entry_price']:.4f}")

    print(f"Capital Awareness: {agent.state.get('capital_awareness', {})}")

    # Check if there are any tradeable opportunities
    print("\n=== Recent Market Analysis ===")
    try:
        opportunities = await agent.analyze_market()
        print(f"Analyzed {len(opportunities)} opportunities")

        if opportunities:
            best_op = max(opportunities, key=lambda x: x["score"])
            print(
                f"Best Opportunity: {best_op['symbol']} (Score: {best_op['score']:.1f})"
            )
    except Exception as e:
        print(f"❌ Market analysis error: {e}")

    # Check execution constraints
    print("\n=== Execution Constraints ===")
    capital = agent.state.get("capital_awareness", {})
    available = capital.get("available", 0)
    print(f"Available Capital: ${available:.2f}")

    if "positions" in agent.state:
        max_positions = agent.config.get("max_positions", 5)
        current_positions = len(agent.state["positions"])
        print(f"Position Limit: {current_positions}/{max_positions}")

    await agent.close()

    return True


async def main():
    try:
        await debug_execution_barriers()
    except Exception as e:
        print(f"\n❌ Debug failed: {e}")
        print(f"\nError type: {type(e).__name__}")
        print(f"Error traceback: {e.__traceback__}")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nDebug interrupted")
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
