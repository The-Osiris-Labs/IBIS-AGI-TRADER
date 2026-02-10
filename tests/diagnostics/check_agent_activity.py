#!/usr/bin/env python3
import asyncio
from ibis_true_agent import IBISTrueAgent


async def check_agent_activity():
    agent = IBISTrueAgent()
    await agent.initialize()

    print("=== AGENT STATUS ===")
    print(f"Market Regime: {agent.state['market_regime']}")
    print(f"Agent Mode: {agent.state['agent_mode']}")
    print(f"Positions: {len(agent.state['positions'])}")
    print()

    print("=== CAPITAL AWARENESS ===")
    capital = agent.state["capital_awareness"]
    print(f"USDT Total: ${capital['usdt_total']:.2f}")
    print(f"USDT Available: ${capital['usdt_available']:.2f}")
    print(f"Holdings Value: ${capital['holdings_value']:.2f}")
    print(f"Total Assets: ${capital['total_assets']:.2f}")
    print()

    print("=== OPEN ORDERS ===")
    open_orders = await agent.client.get_open_orders()
    print(f"Total Open Orders: {len(open_orders)}")
    if open_orders:
        for order in open_orders:
            print(f"  {order.symbol}: {order.side} {order.size} @ {order.price}")
    print()

    print("=== RECENT TRADES ===")
    recent_trades = await agent.client.get_recent_fills(limit=10)
    print(f"Recent Trades (last 10): {len(recent_trades)}")
    for trade in recent_trades[:5]:
        print(
            f"  {trade['symbol']}: {trade['side']} {trade['size']} @ {trade['price']}"
        )
    print()

    print("=== MARKET INTELLIGENCE ===")
    await agent.analyze_market_intelligence()
    high_score_count = sum(
        1 for intel in agent.market_intel.values() if intel.get("score", 0) >= 90
    )
    print(f"High Score Opportunities (≥90): {high_score_count}")

    if high_score_count > 0:
        print("Top Opportunities:")
        for symbol, intel in sorted(
            agent.market_intel.items(), key=lambda x: x[1].get("score", 0), reverse=True
        )[:3]:
            print(f"  {symbol}: {intel.get('score', 0):.1f}")


asyncio.run(check_agent_activity())
