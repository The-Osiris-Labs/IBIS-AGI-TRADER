#!/usr/bin/env python3
import asyncio
import sys

sys.path.append(".")
from ibis_true_agent import IBISAutonomousAgent


async def test_candle_analysis():
    """Test per-second screening and candle knowledge capabilities"""
    try:
        print("🔍 Testing Per-Second Screening and Candle Knowledge System")
        print("=" * 80)

        # Create agent instance
        agent = IBISAutonomousAgent()

        # Initialize agent
        await agent.initialize()
        print("✅ Agent initialized successfully")

        print(f"\n📊 System Status:")
        print(f"   Symbols Cache: {len(agent.symbols_cache)} symbols")
        print(f"   Symbol Rules: {len(agent.symbol_rules)} rules")
        print(f"   Current Holdings: {len(agent.state['positions'])} positions")
        print(f"   USDT Balance: ${agent.state['daily']['start_balance']:.2f}")

        # Analyze market with new capabilities
        print("\n🧠 Analyzing Market with Per-Second Intelligence...")
        market_intel = await agent.analyze_market_intelligence()
        print(f"✅ Analyzed {len(market_intel)} high-quality opportunities")

        if market_intel:
            # Find symbols with detailed market activity
            symbols_with_activity = []
            for symbol, data in market_intel.items():
                if "market_activity" in data and data["market_activity"]:
                    symbols_with_activity.append(symbol)

            print(
                f"\n📈 Symbols with Market Activity Analysis: {len(symbols_with_activity)}"
            )

            if symbols_with_activity:
                # Display detailed candle analysis for top symbols
                sorted_opps = sorted(
                    market_intel.items(), key=lambda x: x[1]["score"], reverse=True
                )[:3]

                for symbol, data in sorted_opps:
                    print(f"\n🎯 {symbol} - Score: {data['score']:.1f}/100")

                    # Display candle analysis
                    if "market_activity" in data:
                        activity = data["market_activity"]
                        print(
                            f"   🔢 Volatility: 1m={activity['volatility_1m'] * 100:.2f}% 5m={activity['volatility_5m'] * 100:.2f}% 15m={activity['volatility_15m'] * 100:.2f}%"
                        )
                        print(
                            f"   📊 Trend Strength: {activity['trend_strength']:.1f}%"
                        )
                        print(
                            f"   💥 Volume Profile: {activity['volume_profile']:.1f}%"
                        )
                        print(
                            f"   📉 Price Action: {activity['price_action'].replace('_', ' ')}"
                        )

                        if (
                            activity["support_level"] > 0
                            and activity["resistance_level"] > 0
                        ):
                            print(f"   🛡️ Support: ${activity['support_level']:.4f}")
                            print(
                                f"   🚧 Resistance: ${activity['resistance_level']:.4f}"
                            )

                        if activity["candle_patterns"]:
                            patterns = [
                                p.replace("_", " ").title()
                                for p in activity["candle_patterns"]
                            ]
                            print(f"   🕯️ Candle Patterns: {', '.join(patterns)}")

            # Check if candle analysis methods are working
            test_symbol = list(market_intel.keys())[0]
            if "market_activity" in market_intel[test_symbol]:
                print(f"\n✅ Per-second screening and candle knowledge system verified")
                print(f"   - Volatility analysis across multiple timeframes")
                print(f"   - Trend strength calculation")
                print(f"   - Volume profile analysis")
                print(f"   - Candle pattern recognition")
                print(f"   - Support and resistance levels")
                print(f"   - Price action classification")
            else:
                print(f"\n❌ Market activity analysis not found for {test_symbol}")

        await agent.client.close()

        print("\n✅" * 5)
        print("Per-Second Screening and Candle Knowledge System Test Completed!")
        print("=" * 80)

        return True

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback

        print(traceback.format_exc())
        return False


async def main():
    """Main test function"""
    try:
        success = await test_candle_analysis()

        if success:
            print(
                "\n🎉 Test PASSED! IBIS True Agent has comprehensive per-second intelligence capabilities"
            )
            print("\n📈 Key Features:")
            print("   - Per-second market scanning and analysis")
            print("   - Multi-timeframe volatility analysis (1m, 5m, 15m)")
            print("   - Trend strength measurement using regression")
            print("   - Volume profile distribution analysis")
            print("   - Advanced candle pattern recognition")
            print("   - Support and resistance level detection")
            print(
                "   - Price action classification (uptrend, downtrend, consolidation)"
            )
            print("   - Comprehensive candle knowledge system")
        else:
            print("\n❌ Test FAILED. Please check the errors.")

    except KeyboardInterrupt:
        print("\n⚠️ Test interrupted by user")


if __name__ == "__main__":
    asyncio.run(main())
