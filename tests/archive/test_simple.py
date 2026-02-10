#!/usr/bin/env python3
import asyncio
import sys

sys.path.append(".")
from ibis_true_agent import IBISAutonomousAgent


async def simple_test():
    try:
        print("🔍 Testing IBIS True Agent...")
        agent = IBISAutonomousAgent()
        print("✅ Agent created successfully")

        # Timeout the initialization after 30 seconds
        task = asyncio.create_task(agent.initialize())
        await asyncio.wait_for(task, timeout=30)
        print("✅ Agent initialized successfully")

        await agent.discover_market()
        print(f"✅ Market discovery: {len(agent.symbols_cache)} symbols")

        await agent.fetch_symbol_rules()
        print(f"✅ Symbol rules: {len(agent.symbol_rules)} rules")

        # Timeout intelligence analysis after 60 seconds
        intel_task = asyncio.create_task(agent.analyze_market_intelligence())
        intel = await asyncio.wait_for(intel_task, timeout=60)
        print(f"✅ Intelligence: {len(intel)} symbols analyzed")

        if intel:
            scores = [data["score"] for data in intel.values()]
            print(
                f"📊 Scores: {min(scores):.1f}-{max(scores):.1f}/100 (avg: {sum(scores) / len(scores):.1f})"
            )

            high_scores = [sym for sym, data in intel.items() if data["score"] > 60]
            print(f"🎯 High-score opportunities: {len(high_scores)} (score > 60)")

            best_symbols = sorted(
                intel.items(), key=lambda x: x[1]["score"], reverse=True
            )[:5]
            print("📈 Top 5 opportunities:")
            for sym, data in best_symbols:
                print(f"   {sym}: {data['score']:.1f}/100 - ${data['price']:.2f}")

        await agent.client.close()
        print("✅ All tests passed")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback

        print(traceback.format_exc())


if __name__ == "__main__":
    try:
        asyncio.run(simple_test())
    except KeyboardInterrupt:
        print("⚠️ Test interrupted")
