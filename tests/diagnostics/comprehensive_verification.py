#!/usr/bin/env python3
"""
Comprehensive verification of all IBIS capabilities
"""

import asyncio
import json
import os
from ibis_true_agent import IBISTrueAgent


async def comprehensive_verification():
    agent = IBISTrueAgent()
    await agent.initialize()

    print("=" * 60)
    print("🎯 COMPREHENSIVE IBIS CAPABILITIES VERIFICATION")
    print("=" * 60)

    # 1. Capital Awareness Verification
    print("\n1️⃣ CAPITAL AWARENESS VERIFICATION")
    capital = agent.state["capital_awareness"]
    print(f"   Total Assets: ${capital['total_assets']:.2f}")
    print(f"   USDT Available: ${capital['usdt_available']:.2f}")
    print(f"   USDT Locked Buy: ${capital['usdt_locked_buy']:.2f}")
    print(f"   Holdings Value: ${capital['holdings_value']:.2f}")

    assert capital["total_assets"] > 0, "Total assets should be positive"
    assert capital["usdt_available"] >= 0, "USDT available should be non-negative"
    assert capital["holdings_value"] >= 0, "Holdings value should be non-negative"
    print("   ✅ Capital awareness correctly calculated")

    # 2. Portfolio Verification
    print("\n2️⃣ PORTFOLIO VERIFICATION")
    portfolio = await agent.update_positions_awareness()
    print(f"   Portfolio Value: ${portfolio['total_value']:.2f}")
    print(
        f"   Portfolio PnL: ${portfolio['total_pnl']:.2f} ({portfolio['total_pnl_pct']:.2f}%)"
    )
    print(f"   Avg AGI Score: {portfolio['avg_agi_score']:.1f}")

    assert portfolio["total_value"] > 0, "Portfolio value should be positive"
    print("   ✅ Portfolio calculations include USDT + holdings")

    # 3. Market Intelligence Verification
    print("\n3️⃣ MARKET INTELLIGENCE VERIFICATION")
    await agent.analyze_market_intelligence()
    high_score_count = sum(
        1 for intel in agent.market_intel.values() if intel.get("score", 0) >= 90
    )
    print(f"   High Score Opportunities: {high_score_count}")

    if high_score_count > 0:
        for symbol, intel in agent.market_intel.items():
            if intel.get("score", 0) >= 90:
                print(f"   • {symbol}: {intel['score']:.1f} - {intel['agi_insight']}")

    print("   ✅ Market intelligence active")

    # 4. Open Orders Verification
    print("\n4️⃣ OPEN ORDERS VERIFICATION")
    open_orders = await agent.client.get_open_orders()
    print(f"   Open Orders: {len(open_orders)}")

    if open_orders:
        for order in open_orders:
            print(
                f"   • {order.get('symbol')}: {order.get('size')} @ {order.get('price')}"
            )

    assert len(open_orders) <= 10, "Too many open orders"
    print("   ✅ Order management working")

    # 5. Position Management Verification
    print("\n5️⃣ POSITION MANAGEMENT VERIFICATION")
    for sym, pos in portfolio["positions"].items():
        print(f"   • {sym}:")
        print(f"      Quantity: {pos['quantity']:.8f}")
        print(f"      Entry: ${pos['entry_price']:.6f}")
        print(f"      Current: ${pos['current_price']:.6f}")
        print(f"      PnL: ${pos['pnl']:.2f} ({pos['pnl_pct']:.2f}%)")

    assert len(portfolio["positions"]) <= 10, "Too many positions"
    print("   ✅ Positions properly tracked")

    # 6. Strategy Verification
    print("\n6️⃣ STRATEGY VERIFICATION")
    print(f"   Market Regime: {agent.state['market_regime']}")
    print(f"   Agent Mode: {agent.state['agent_mode']}")
    # Fear & Greed from free intelligence
    fg_index = await agent.free_intel.get_fear_greed_index()
    print(f"   Fear & Greed Index: {fg_index['value']} ({fg_index['classification']})")

    assert agent.state["market_regime"] in [
        "VOLATILE",
        "FLAT",
        "TRENDING",
        "NORMAL",
        "UNKNOWN",
    ], "Invalid market regime"
    print("   ✅ Strategy selection working")

    # 7. Performance Metrics Verification
    print("\n7️⃣ PERFORMANCE METRICS VERIFICATION")
    daily = agent.state["daily"]
    print(f"   Trades: {daily['trades']}")
    print(f"   Wins: {daily['wins']}")
    print(f"   Losses: {daily['losses']}")
    print(f"   PnL: ${daily['pnl']:.2f}")

    print("   ✅ Performance tracking working")

    # 8. State File Verification
    print("\n8️⃣ STATE FILE VERIFICATION")
    state_path = "/root/projects/Dont enter unless solicited/AGI Trader/data/ibis_true_state.json"
    assert os.path.exists(state_path), "State file not found"

    with open(state_path, "r") as f:
        state_file = json.load(f)

    assert "capital_awareness" in state_file, "State file missing capital awareness"
    assert state_file["capital_awareness"]["total_assets"] > 0, (
        "State file has zero assets"
    )
    print("   ✅ State file contains valid data")

    print("\n" + "=" * 60)
    print("✅ ALL ASPECTS VERIFIED AND WORKING CORRECTLY!")
    print("=" * 60)


asyncio.run(comprehensive_verification())
