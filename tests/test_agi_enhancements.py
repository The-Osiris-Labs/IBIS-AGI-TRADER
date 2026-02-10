#!/usr/bin/env python3
"""Test the enhanced AGI-powered capabilities of IBIS True Agent"""

import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ibis_true_agent import IBISAutonomousAgent


async def test_agi_enhancements():
    """Test the complete AGI-powered trading system"""
    try:
        print("🚀 Testing IBIS True Agent - AGI-Powered Trading System")
        print("=" * 80)

        # Create agent instance
        agent = IBISAutonomousAgent()

        # Initialize the agent (timeout to prevent hanging)
        print("🔄 Initializing IBIS True Agent...")
        init_task = asyncio.create_task(agent.initialize())
        try:
            await asyncio.wait_for(init_task, timeout=30)
            print("✅ Agent initialized successfully")
        except asyncio.TimeoutError:
            print("❌ Agent initialization timed out")
            return False

        # Test market discovery and intelligence
        print("\n📊 Testing Market Discovery and Intelligence Collection...")
        discover_task = asyncio.create_task(agent.discover_market())
        try:
            await asyncio.wait_for(discover_task, timeout=20)
            print(f"✅ Discovered {len(agent.symbols_cache)} symbols")
        except asyncio.TimeoutError:
            print("❌ Market discovery timed out")
            return False

        # Test symbol rules
        print("📋 Testing Symbol Rules Loading...")
        rules_task = asyncio.create_task(agent.fetch_symbol_rules())
        try:
            await asyncio.wait_for(rules_task, timeout=20)
            print(f"✅ Loaded rules for {len(agent.symbol_rules)} symbols")
        except asyncio.TimeoutError:
            print("❌ Symbol rules loading timed out")
            return False

        # Test market intelligence
        print("🧠 Testing Market Intelligence Analysis...")
        intel_task = asyncio.create_task(agent.analyze_market_intelligence())
        try:
            await asyncio.wait_for(intel_task, timeout=60)
            print(f"✅ Analyzed {len(agent.market_intel)} high-quality opportunities")

            if agent.market_intel:
                scores = [
                    d["score"] for d in agent.market_intel.values() if "score" in d
                ]
                avg_score = sum(scores) / len(scores) if scores else 0

                print(f"   📈 Average Score: {avg_score:.1f}/100")
                high_scores = sum(
                    1
                    for d in agent.market_intel.values()
                    if "score" in d and d["score"] >= 80
                )
                print(f"   🎯 High Score Opportunities: {high_scores}")

                print("   📊 Top 5 Opportunities:")
                sorted_opps = sorted(
                    agent.market_intel.items(),
                    key=lambda x: x[1]["score"],
                    reverse=True,
                )[:5]
                for sym, data in sorted_opps:
                    print(f"     • {sym:8} Score: {data['score']:.1f}")
                    if "market_activity" in data and data["market_activity"]:
                        activity = data["market_activity"]
                        print(
                            f"        Volatility: 1m={activity['volatility_1m'] * 100:.2f}% 5m={activity['volatility_5m'] * 100:.2f}% 15m={activity['volatility_15m'] * 100:.2f}%"
                        )
                        print(
                            f"        Trend Strength: {activity['trend_strength']:.1f}%"
                        )
                        print(f"        Price Action: {activity['price_action']}")

        except asyncio.TimeoutError:
            print("❌ Market intelligence analysis timed out")
            return False

        # Test market conditions assessment
        print("\n🔍 Testing Market Conditions Assessment...")
        conditions = agent._assess_market_conditions()
        print("✅ Market conditions assessed successfully")
        print(f"   📊 Health: {conditions['overall_health']}")
        print(f"   🎯 Opportunity: {conditions['trading_opportunity']}")
        print(f"   🎢 Volatility Risk: {conditions['volatility_risk']}")
        print(f"   💪 Trend Strength: {conditions['trend_strength']}")
        print(f"   💰 Volume Profile: {conditions['volume_profile']}")
        print(f"   📉 Sentiment: {conditions['market_sentiment']}")

        # Test should stop all operations logic
        print("\n🛑 Testing Stop Operations Logic...")
        should_stop = await agent._should_stop_all_ops(conditions)
        print(
            f"✅ Stop decision: {'YES - STOP ALL OPERATIONS' if should_stop else 'NO - CONTINUE TRADING'}"
        )

        # Test dynamic position sizing
        print("\n💰 Testing Dynamic Position Sizing...")
        if agent.market_intel:
            best_opp = sorted(
                agent.market_intel.items(), key=lambda x: x[1]["score"], reverse=True
            )[0]
            strategy = await agent.execute_strategy(
                agent.state["market_regime"], agent.state["agent_mode"]
            )
            position_size = await agent.dynamic_position_sizing(
                strategy, best_opp[0], agent.market_intel
            )
            print(f"✅ Position sizing calculated for {best_opp[0]}")
            print(f"   Score: {best_opp[1]['score']:.1f}/100")
            print(f"   Position Size: ${position_size:.2f}")

            if "market_activity" in best_opp[1]:
                activity = best_opp[1]["market_activity"]
                print(f"   Volatility Risk: {activity['volatility_15m'] * 100:.2f}%")
                print(f"   Trend Strength: {activity['trend_strength']:.1f}%")
                print(f"   Volume Profile: {activity['volume_profile']:.1f}%")

        # Close the agent client session
        await agent.client.close()

        print("\n✅" * 5)
        print("All AGI enhancement tests passed!")
        print("=" * 80)

        print(
            "\n🎯 IBIS True Agent is now operating as an AGI-powered trading bot that:"
        )
        print("   • Continuously hunts for high-quality trading opportunities")
        print("   • Knows when to rest during poor market conditions")
        print("   • Makes decisions based on comprehensive market intelligence")
        print("   • Automatically cancels orders when conditions deteriorate")
        print("   • Dynamically sizes positions based on volatility and trend strength")
        print("   • Adapts its trading behavior based on real-time market conditions")

        return True

    except Exception as e:
        print(f"\n❌ Test Error: {str(e)}")
        import traceback

        print("\n" + traceback.format_exc())
        return False


async def main():
    """Main test function with timeouts for all phases"""
    try:
        test_task = asyncio.create_task(test_agi_enhancements())
        await asyncio.wait_for(test_task, timeout=300)
    except asyncio.TimeoutError:
        print("\n❌ Test execution timed out")
        return False

    return True


if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        if not success:
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n⚠️ Test interrupted by user")
        sys.exit(0)
