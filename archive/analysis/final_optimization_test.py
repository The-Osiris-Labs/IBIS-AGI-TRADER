#!/usr/bin/env python3
"""
Final optimization verification test
"""

import asyncio
import json
import os
from ibis_true_agent import IBISTrueAgent
from advanced_intelligence import AdvancedIntelligenceSystem
from enhanced_execution import EnhancedExecutionSystem


async def final_optimization_test():
    """Test all optimization systems together"""
    print("=" * 80)
    print("🎯 FINAL IBIS OPTIMIZATION VERIFICATION")
    print("=" * 80)

    # Initialize agent
    agent = IBISTrueAgent()
    await agent.initialize()

    print("\n✅ Agent initialized successfully")

    # Test enhanced execution system
    print("\n🚀 TESTING ENHANCED EXECUTION SYSTEM")
    execution_system = EnhancedExecutionSystem(agent)

    try:
        await execution_system.enhance_execution_strategy()
        print("\n✅ Enhanced execution system tested successfully")
    except Exception as e:
        print(f"\n⚠️ Execution system test failed: {e}")

    # Test advanced intelligence system
    print("\n🧠 TESTING ADVANCED INTELLIGENCE SYSTEM")
    ai_system = AdvancedIntelligenceSystem(agent)

    try:
        await ai_system.enhance_market_intelligence()
        print("\n✅ Advanced intelligence system tested successfully")

        # Display intelligence summary
        print("\n📊 INTELLIGENCE SUMMARY")
        print("=" * 60)

        print("\nReal-Time Signals:")
        for symbol, signal in ai_system.real_time_signals.items():
            status = (
                "📈"
                if signal["signal"] in ["BUY", "STRONG_BUY"]
                else "📉"
                if signal["signal"] in ["SELL", "STRONG_SELL"]
                else "➡️"
            )
            print(f"{status} {symbol}: {signal['signal']}")

        print("\nPredictive Analysis:")
        for symbol, model in ai_system.predictive_models.items():
            print(
                f"{symbol}: Up={model['upward_probability']:.2f}, Down={model['downward_probability']:.2f}"
            )

    except Exception as e:
        print(f"\n⚠️ Intelligence system test failed: {e}")

    # Verify portfolio health
    print("\n💰 VERIFYING PORTFOLIO HEALTH")
    capital = agent.state["capital_awareness"]
    portfolio = await agent.update_positions_awareness()

    print(f"Total Assets: ${capital['total_assets']:.2f}")
    print(f"USDT Balance: ${capital['usdt_available']:.2f}")
    print(f"Holdings Value: ${capital['holdings_value']:.2f}")
    print(f"Locked Capital: ${capital['usdt_locked_buy']:.2f}")
    print(
        f"Total PnL: ${portfolio['total_pnl']:.2f} ({portfolio['total_pnl_pct']:.2f}%)"
    )

    # Verify ADI order status
    print("\n📝 VERIFYING ADI ORDER")
    open_orders = await agent.client.get_open_orders()
    adi_order = None

    for order in open_orders:
        if order.get("symbol") == "ADI-USDT":
            adi_order = order
            break

    if adi_order:
        print(f"ADI Order: {adi_order.get('size')} @ {adi_order.get('price')}")
    else:
        print("ADI Order not found")

    print("\n" + "=" * 80)
    print("✅ ALL OPTIMIZATION TESTS COMPLETED!")
    print("=" * 80)


asyncio.run(final_optimization_test())
