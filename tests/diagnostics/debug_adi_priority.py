#!/usr/bin/env python3
"""
Debug why ADI is in priority symbols
"""

import sys

sys.path.insert(0, "/root/projects/Dont enter unless solicited/AGI Trader")
from ibis_true_agent import IBISTrueAgent
import asyncio


async def debug_adi_priority():
    agent = IBISTrueAgent()
    await agent.initialize()

    print("🐛 DEBUG ADI PRIORITY")
    print("=" * 50)

    print("📊 Hold positions:")
    for symbol, pos in agent.state["positions"].items():
        print(f"   🛡️ {symbol}")

    print(f"\n📋 Buy orders:")
    for symbol, order in agent.state["capital_awareness"]["buy_orders"].items():
        print(f"   📈 {symbol}: {order}")

    print(f"\n🎯 Calling analyze_market_intelligence():")

    await agent.analyze_market_intelligence()

    print(f"\n✅ Analysis complete")


asyncio.run(debug_adi_priority())
