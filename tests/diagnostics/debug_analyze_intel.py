#!/usr/bin/env python3
"""
Debug analyze_market_intelligence() priority symbols
"""

import sys

sys.path.insert(0, "/root/projects/Dont enter unless solicited/AGI Trader")
from ibis_true_agent import IBISTrueAgent
import asyncio


async def debug_analyze():
    agent = IBISTrueAgent()
    await agent.initialize()

    print("🎯 DEBUG ANALYZE MARKET INTELLIGENCE")
    print("=" * 50)

    # Run market intelligence gathering
    await agent.analyze_market_intelligence()

    print(f"📊 Market Intel Symbols:")
    for sym, intel in agent.market_intel.items():
        print(f"   📈 {sym}: Score {intel['score']:.1f}")

    print(f"\n🔍 Market Intel Count: {len(agent.market_intel)}")

    print(f"\n✅ Analyze market intelligence complete")


asyncio.run(debug_analyze())
