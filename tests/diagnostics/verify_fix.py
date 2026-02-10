#!/usr/bin/env python3
import asyncio
import json
from ibis_true_agent import IBISTrueAgent


async def verify_fix():
    agent = IBISTrueAgent()
    await agent.initialize()

    print("=== CAPITAL AWARENESS ===")
    capital = agent.state["capital_awareness"]
    print(f"USDT Available: ${capital['usdt_available']:.2f}")
    print(f"USDT Locked Buy: ${capital['usdt_locked_buy']:.2f}")
    print(f"Holdings Value: ${capital['holdings_value']:.2f}")
    print(f"Total Assets: ${capital['total_assets']:.2f}")

    print("\n=== OPEN ORDERS ===")
    open_orders = await agent.client.get_open_orders()
    print(f"Total Open Orders: {len(open_orders)}")
    if open_orders:
        for order in open_orders:
            print(f"Symbol: {order.get('symbol')}")
            print(f"Price: ${order.get('price')}")
            print(f"Size: {order.get('size')}")

    print("\n=== MARKET INTELLIGENCE ===")
    await agent.analyze_market_intelligence()
    high_score = sum(
        1 for intel in agent.market_intel.values() if intel.get("score", 0) >= 90
    )
    print(f"High Score Opportunities: {high_score}")

    print("\n=== POSITION AWARENESS ===")
    portfolio = await agent.update_positions_awareness()
    print(f"Total Value: ${portfolio['total_value']:.2f}")
    print(f"PnL: ${portfolio['total_pnl']:.2f} ({portfolio['total_pnl_pct']:.2f}%)")
    print(f"Avg AGI Score: {portfolio['avg_agi_score']:.1f}")


asyncio.run(verify_fix())
