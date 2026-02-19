#!/usr/bin/env python3
import asyncio
from ibis_true_agent import IBISAutonomousAgent


async def test_intelligence():
    print("🔍 Testing new comprehensive intelligence system...")

    agent = IBISAutonomousAgent()
    await agent.initialize()

    print(f"📊 Symbols analyzed: {len(agent.market_intel)}")

    # Check if we have insights for all symbols
    symbols_with_insights = 0
    for symbol, data in agent.market_intel.items():
        if "insights" in data and len(data["insights"]) > 0:
            symbols_with_insights += 1
            print(
                f"   ✅ {symbol}: {data['score']:.1f}/100 - {data['risk_level']} - {data['opportunity_type']}"
            )
            if len(data["insights"]) > 0:
                for insight in data["insights"]:
                    print(f"       - {insight}")

    print(f"📈 {symbols_with_insights}/{len(agent.market_intel)} symbols with insights")

    # Check score distribution
    scores = [data["score"] for data in agent.market_intel.values()]
    if scores:
        print(f"📊 Score range: {min(scores):.1f} - {max(scores):.1f}/100")
        print(f"📊 Average score: {sum(scores) / len(scores):.1f}/100")
    else:
        print(f"📊 No scores available (market intel is empty)")

    # Find top opportunities with detailed insights
    top_opps = sorted(agent.market_intel.items(), key=lambda x: x[1]["score"], reverse=True)[:5]
    print(f"🎯 Top 5 opportunities with comprehensive insights:")
    for symbol, data in top_opps:
        print(f"   {symbol}:")
        print(f"       Score: {data['score']:.1f}/100")
        print(f"       Price: ${data['price']:.4f}")
        print(f"       Risk Level: {data['risk_level']}")
        print(f"       Type: {data['opportunity_type']}")
        print(f"       Liquidity: {data['liquidity_score']}")
        print(f"       Technical Strength: {data['technical_strength']}")
        print(f"       Support: ${data['support_level']:.4f}")
        print(f"       Resistance: ${data['resistance_level']:.4f}")
        if data["insights"]:
            print(f"       Insights: {' | '.join(data['insights'])}")


asyncio.run(test_intelligence())
