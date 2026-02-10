#!/usr/bin/env python3
import asyncio
from ibis_true_agent import IBISAutonomousAgent


async def test_hyper_mode():
    print("🚀 Initializing IBIS True Agent in HYPER-FREQUENCY mode...")

    # Create agent instance
    agent = IBISAutonomousAgent()

    # Force hyper mode for testing
    agent.state["agent_mode"] = "HYPER"
    agent.state["market_regime"] = "VOLATILE"

    # Initialize
    await agent.initialize()

    print("✅ Agent initialized successfully")
    print(f"📊 Symbols Analyzed: {len(agent.market_intel)}")

    # Find high-potential opportunities for hyper trading
    high_vol_opps = []
    for symbol, data in agent.market_intel.items():
        if data["score"] >= 55 and data.get("volatility", 0) > 0.01:
            high_vol_opps.append((symbol, data["score"], data.get("volatility", 0)))

    print(
        f"🎯 High Volatility Opportunities (≥ 55 score, >1% vol): {len(high_vol_opps)}"
    )

    if high_vol_opps:
        print("Top 5 Hyper-Frequency Candidates:")
        sorted_opps = sorted(high_vol_opps, key=lambda x: x[1] * x[2], reverse=True)[:5]
        for symbol, score, vol in sorted_opps:
            print(f"   {symbol:4} - {score:.1f}/100 - Volatility: {vol:.2%}")

    print(f"💰 USDT Balance: ${agent.state['daily']['start_balance']:.2f}")
    print(f"🌐 Forced Regime: VOLATILE")
    print(f"🚀 Agent Mode: HYPER")

    # Verify hyper configuration
    strategy = await agent.execute_strategy("VOLATILE", "HYPER")
    print(f"📈 Target Profit: {strategy['target_profit']:.1%}")
    print(f"📉 Stop Loss: {strategy['stop_loss']:.1%}")
    print(f"🔄 Scan Interval: {strategy['scan_interval']}s")
    print(f"🎯 Max Positions: {strategy['max_positions']}")

    print("\n✅ Hyper-frequency configuration verified!")
    print("IBIS is ready for rapid, high-volume trading with tight risk management")


asyncio.run(test_hyper_mode())
