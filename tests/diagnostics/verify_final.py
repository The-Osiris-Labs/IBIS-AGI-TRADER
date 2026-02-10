#!/usr/bin/env python3
import asyncio
from ibis_true_agent import IBISTrueAgent


async def verify_all():
    agent = IBISTrueAgent()
    await agent.initialize()

    # Capital Awareness
    capital = agent.state["capital_awareness"]
    print("CAPITAL AWARENESS:")
    print(f"USDT Available: ${capital['usdt_available']:.2f}")
    print(f"USDT Locked Buy: ${capital['usdt_locked_buy']:.2f}")
    print(f"Holdings Value: ${capital['holdings_value']:.2f}")
    print(f"Total Assets: ${capital['total_assets']:.2f}")

    # Open Orders
    open_orders = await agent.client.get_open_orders()
    print(f"\nOPEN ORDERS: {len(open_orders)}")
    if open_orders:
        for order in open_orders:
            print(
                f"{order.get('symbol')} - ${order.get('price')} - {order.get('size')}"
            )

    # Market Intelligence
    await agent.analyze_market_intelligence()
    high_score = sum(
        1 for intel in agent.market_intel.values() if intel.get("score", 0) >= 90
    )
    print(f"\nHIGH SCORE OPPORTUNITIES: {high_score}")

    # Position Awareness
    portfolio = await agent.update_positions_awareness()
    print(f"\nPORTFOLIO VALUE: ${portfolio['total_value']:.2f}")
    print(
        f"PORTFOLIO PnL: ${portfolio['total_pnl']:.2f} ({portfolio['total_pnl_pct']:.2f}%)"
    )


asyncio.run(verify_all())
