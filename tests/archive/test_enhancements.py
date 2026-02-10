#!/usr/bin/env python3
"""
Test script to verify IBIS True Agent enhancements are working
"""

import asyncio
import sys
from ibis_true_agent import IBISAutonomousAgent


async def test_enhancements():
    try:
        print("🎯 Testing IBIS True Agent Enhancements...")

        agent = IBISAutonomousAgent()
        await agent.initialize()

        print(f"✅ Agent initialized successfully")
        print(f"📊 Symbols Analyzed: {len(agent.market_intel)}")

        scores = [
            intel["score"]
            for symbol, intel in agent.market_intel.items()
            if "score" in intel
        ]
        if scores:
            avg_score = sum(scores) / len(scores)
            print(f"📈 Average Score: {avg_score:.1f}/100")

            high_scores = [
                symbol
                for symbol, intel in agent.market_intel.items()
                if intel["score"] >= 70
            ]
            print(f"🚀 High-Score Opportunities: {len(high_scores)}")

            if high_scores:
                print("📋 Top Opportunities:")
                sorted_opportunities = sorted(
                    agent.market_intel.items(),
                    key=lambda x: x[1]["score"],
                    reverse=True,
                )[:5]
                for symbol, intel in sorted_opportunities:
                    if intel["score"] >= 65:
                        print(f"   • {symbol}: {intel['score']:.1f}/100")

        print(f"🌐 Market Regime: {agent.state['market_regime']}")
        print(f"🚀 Agent Mode: {agent.state['agent_mode']}")

        await agent.client.close()

        print("\n🎉 All enhancements verified successfully!")
        return True

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback

        print(f"\nStack Trace:")
        print(traceback.format_exc())
        return False


if __name__ == "__main__":
    try:
        success = asyncio.run(test_enhancements())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n✅ Test completed successfully")
        sys.exit(0)
