#!/usr/bin/env python3
"""
Check market intelligence structure and candle visibility
"""

import sys

sys.path.insert(0, "/root/projects/Dont enter unless solicited/AGI Trader")
from ibis_true_agent import IBISTrueAgent
import asyncio


async def check_intel_structure():
    agent = IBISTrueAgent()
    await agent.initialize()

    print("📊 CHECKING MARKET INTELLIGENCE STRUCTURE")
    print("=" * 50)

    await agent.analyze_market_intelligence()

    print(f"Total opportunities: {len(agent.market_intel)}")
    print()

    for symbol, intel in agent.market_intel.items():
        print(f"🔍 {symbol} Market Intel:")

        # Check basic fields
        print(f"   Price: ${intel.get('price', 0):.4f}")
        print(f"   Score: {intel.get('score', 0):.1f}")
        print(f"   Signal: {intel.get('signal', 'NO SIGNAL')}")

        # Check momentum fields
        print(f"   1h Momentum: {intel.get('momentum_1h', 0):.3f}%")
        print(f"   24h Change: {intel.get('change_24h', 0):.3f}%")

        # Check volatility
        print(f"   1m Volatility: {intel.get('volatility_1m', 0):.4f}")

        # Check candle analysis
        if "candle_analysis" in intel:
            print(
                f"   Candle Action: {intel['candle_analysis'].get('price_action', 'N/A')}"
            )
            patterns = intel["candle_analysis"].get("candle_patterns", [])
            if patterns:
                print(f"   Candle Patterns: {', '.join(patterns)}")

        # Check AGI analysis
        if "agi_signal" in intel:
            print(f"   AGI Action: {intel['agi_signal'].get('agi_action', 'N/A')}")
            print(
                f"   AGI Confidence: {intel['agi_signal'].get('agi_confidence', 0):.1f}%"
            )

        # Check cross-exchange
        if "lead_signal" in intel:
            lead = intel["lead_signal"]
            if lead.get("has_lead"):
                print(
                    f"   X-Lead: {lead.get('direction')} (+{lead.get('lead_pct', 0):.2f}%, boost +{lead.get('boost', 0)})"
                )
            else:
                print(f"   X-Lead: Neutral")

        print()


asyncio.run(check_intel_structure())
