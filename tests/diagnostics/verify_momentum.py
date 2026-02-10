#!/usr/bin/env python3
"""
Verify momentum calculations and candle visibility
"""

import sys

sys.path.insert(0, "/root/projects/Dont enter unless solicited/AGI Trader")
from ibis_true_agent import IBISTrueAgent
import asyncio


async def verify_momentum_calculations():
    agent = IBISTrueAgent()
    await agent.initialize()

    print("📈 VERIFYING MOMENTUM CALCULATIONS")
    print("=" * 50)

    # Analyze opportunities
    await agent.analyze_market_intelligence()

    for symbol, intel in agent.market_intel.items():
        print(f"\n🔍 {symbol}:")
        print(f"   Price: ${intel.get('price', 0):.4f}")
        print(f"   1h Momentum: {intel.get('momentum_1h', 0):.3f}%")
        print(f"   24h Change: {intel.get('change_24h', 0):.3f}%")

        # Verify momentum calculation
        momentum_1h = intel.get("momentum_1h", 0)
        change_24h = intel.get("change_24h", 0)
        calculated_momentum = (change_24h + momentum_1h) / 2
        print(f"   Calculated Avg Momentum: {calculated_momentum:.3f}%")
        print(f"   Agent Momentum Score: {intel.get('momentum_score', 0):.1f}")

        # Check if agent used this momentum
        if "momentum" in intel:
            print(f"   Agent Momentum Field: {intel.get('momentum', 0):.3f}")


asyncio.run(verify_momentum_calculations())
