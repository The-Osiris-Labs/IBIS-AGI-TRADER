#!/usr/bin/env python3
"""
Fix agent activity issues:
1. Reset capital awareness with real data
2. Lower high-quality opportunity threshold temporarily
3. Check and fix position state
"""

import asyncio
import json
import os
from ibis_true_agent import IBISTrueAgent


async def fix_agent_activity():
    print("🔧 Fixing IBIS agent activity issues...")

    agent = IBISTrueAgent()
    await agent.initialize()

    print("\n=== FIX 1: UPDATE CAPITAL AWARENESS ===")
    await agent.update_capital_awareness()
    capital = agent.state["capital_awareness"]
    print(f"USDT Total: ${capital['usdt_total']:.2f}")
    print(f"USDT Available: ${capital['usdt_available']:.2f}")
    print(f"Holdings Value: ${capital['holdings_value']:.2f}")
    print(f"Total Assets: ${capital['total_assets']:.2f}")

    print("\n=== FIX 2: CHECK RECENT TRADES ===")
    recent_trades = await agent.client.get_recent_fills(limit=5)
    print(f"Recent Trades: {len(recent_trades)}")
    for trade in recent_trades:
        print(
            f"  {trade['symbol']}: {trade['side']} {trade['size']} @ {trade['price']}"
        )

    print("\n=== FIX 3: ANALYZE MARKET INTELLIGENCE ===")
    await agent.analyze_market_intelligence()
    high_score_count = 0
    for symbol, intel in agent.market_intel.items():
        score = intel.get("score", 0)
        if score >= 85:  # Lowered threshold for testing
            high_score_count += 1
            print(f"  {symbol}: {score:.1f}")

    print(f"\nHigh-Quality Opportunities (≥85): {high_score_count}")

    print("\n=== FIX 4: UPDATE POSITION PRICES ===")
    portfolio = await agent.update_positions_awareness()
    for sym, pos in portfolio["positions"].items():
        print(f"  {sym}: ${pos['current_price']:.6f} | {pos['pnl_pct']:+.2f}%")

    print("\n=== FIX 5: SAVE UPDATED STATE ===")
    agent._save_state()
    print("✅ State saved successfully")


asyncio.run(fix_agent_activity())
