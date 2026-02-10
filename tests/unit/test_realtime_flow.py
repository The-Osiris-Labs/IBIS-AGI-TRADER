#!/usr/bin/env python3
"""
Test real-time data flow and market intelligence
"""

import asyncio
from ibis_true_agent import IBISTrueAgent


async def test_realtime_data():
    print("🧪 Testing real-time data flow...")
    agent = IBISTrueAgent()
    await agent.initialize()

    print("\n📊 Market Discovery:")
    print(f"   Symbols discovered: {len(agent.symbols_cache)}")
    print(f"   Rules loaded: {len(agent.symbol_rules)}")

    print("\n💰 Capital Awareness:")
    capital = await agent.update_capital_awareness()
    print(f"   USDT Total: ${capital['usdt_total']:.2f}")
    print(f"   USDT Available: ${capital['usdt_available']:.2f}")
    print(f"   Holdings Value: ${capital['holdings_value']:.2f}")
    print(f"   Total Assets: ${capital['total_assets']:.2f}")

    print("\n📈 Position Awareness:")
    portfolio = await agent.update_positions_awareness()
    print(f"   Portfolio Value: ${portfolio['total_value']:.2f}")
    print(
        f"   Total PnL: ${portfolio['total_pnl']:.2f} ({portfolio['total_pnl_pct']:.2f}%)"
    )
    print(f"   Positions: {len(portfolio['positions'])}")

    print("\n🧠 Market Intelligence:")
    await agent.analyze_market_intelligence()
    print(f"   Intel collected: {len(agent.market_intel)} symbols")

    print("\n🎯 Priority Signals:")
    for symbol in ["ADI", "AIO", "AERGO", "ALEPH"]:
        intel = agent.market_intel.get(symbol, {})
        if intel:
            print(
                f"   {symbol}: Score={intel.get('score', 0):.1f}, Signal={intel.get('agi_insight', 'N/A')}"
            )


if __name__ == "__main__":
    try:
        asyncio.run(test_realtime_data())
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback

        print(traceback.format_exc())
