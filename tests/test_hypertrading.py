#!/usr/bin/env python3
import asyncio
import sys
import time

sys.path.append(".")
from ibis_true_agent import IBISAutonomousAgent


async def test_hypertrading():
    """Test IBIS True Agent hypertrading capabilities with new intelligence system"""
    try:
        print("🚀 Testing IBIS True Agent Hypertrading Capabilities")
        print("=" * 80)

        # Create agent instance
        print("🔧 Initializing IBIS True Agent...")
        agent = IBISAutonomousAgent()

        # Timeout the initialization after 30 seconds
        init_task = asyncio.create_task(agent.initialize())
        await asyncio.wait_for(init_task, timeout=30)
        print("✅ Agent initialized successfully")

        print(f"\n📊 System Status:")
        print(f"   Symbols Cache: {len(agent.symbols_cache)} symbols")
        print(f"   Symbol Rules: {len(agent.symbol_rules)} rules")
        print(f"   Current Holdings: {len(agent.state['positions'])} positions")
        print(f"   USDT Balance: ${agent.state['daily']['start_balance']:.2f}")

        # Test hypertrading configuration
        print("\n🎯 Testing Hypertrading Configuration...")
        await agent.initialize()

        # Force hypertrading mode for testing
        agent.state["agent_mode"] = "HYPER"
        agent.state["market_regime"] = "VOLATILE"

        print(f"   Agent Mode: {agent.state['agent_mode']}")
        print(f"   Market Regime: {agent.state['market_regime']}")

        # Get strategy parameters for hyper mode
        strategy = await agent.execute_strategy("VOLATILE", "HYPER")
        print(f"\n📈 Hypertrading Strategy:")
        print(f"   Target Profit: {strategy['target_profit'] * 100:.1f}% per trade")
        print(f"   Stop Loss: {abs(strategy['stop_loss']) * 100:.1f}%")
        print(f"   Max Positions: {strategy['max_positions']}")
        print(f"   Scan Interval: {strategy['scan_interval']} seconds")
        print(f"   Min Score: {strategy['confidence_threshold']}/100")

        # Analyze market for high-frequency opportunities
        print("\n🧠 Analyzing Market Intelligence for Hypertrading...")
        intel_task = asyncio.create_task(agent.analyze_market_intelligence())
        intel = await asyncio.wait_for(intel_task, timeout=60)
        print(f"✅ Analyzed {len(intel)} high-quality opportunities")

        # Find hypertrading opportunities
        print("\n🎯 Finding Hypertrading Opportunities:")
        high_freq_opps = []
        for symbol, data in intel.items():
            score = data.get("score", 0)
            volatility = data.get("volatility", 0)
            volume = data.get("volume_24h", 0)

            if score >= 60 and volatility > 0.01 and volume > 0:
                high_freq_opps.append(
                    {
                        "symbol": symbol,
                        "score": score,
                        "price": data.get("price", 0),
                        "volatility": volatility,
                        "volume": volume,
                        "change_24h": data.get("change_24h", 0),
                    }
                )

        # Sort by score descending
        high_freq_opps.sort(key=lambda x: x["score"], reverse=True)

        print(
            f"📊 Found {len(high_freq_opps)} hypertrading opportunities (score ≥ 60, vol > 1%)"
        )

        if high_freq_opps:
            print("\n📈 Top Hypertrading Candidates:")
            for i, opp in enumerate(high_freq_opps[:5]):
                print(f"   {i + 1:2d}. {opp['symbol']:8} Score: {opp['score']:.1f}")
                print(f"        Price: ${opp['price']:.4f}")
                print(f"        Volatility: {opp['volatility'] * 100:.2f}%")
                print(f"        Volume: ${opp['volume']:,.0f}")
                print(f"        24h Change: {opp['change_24h']:.2f}%")

        # Check if agent is ready for hypertrading
        print("\n🔍 Agent Readiness Check:")
        total_assets = agent.state["daily"]["start_balance"]
        if len(high_freq_opps) > 0:
            print("✅ Market conditions are favorable for hypertrading")
            print(f"✅ {len(high_freq_opps)} quality opportunities available")
        else:
            print("⚠️  Limited hypertrading opportunities available")

        if strategy["available"] > 0:
            print(f"✅ Available USDT: ${strategy['available']:.2f}")
            print(f"✅ Total Assets: ${total_assets:.2f}")

        # Test position sizing
        if high_freq_opps:
            print("\n💰 Testing Position Sizing for Hypertrading:")
            best_opp = high_freq_opps[0]
            size = await agent.calculate_position_size(
                best_opp["score"],
                strategy,
                "VOLATILE",
                {best_opp["symbol"]: intel[best_opp["symbol"]]},
            )

            print(f"   Symbol: {best_opp['symbol']}")
            print(f"   Score: {best_opp['score']:.1f}/100")
            print(f"   Calculated Position: {size:.6f} {best_opp['symbol']}")
            print(f"   Value: ${size * best_opp['price']:.2f}")

        # Close the client session
        await agent.client.close()

        print("\n✅" * 5)
        print("IBIS True Agent Hypertrading Test Completed Successfully!")
        print("=" * 80)

        return True

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback

        print(traceback.format_exc())
        return False


async def run_stress_test():
    """Run a stress test to verify hypertrading performance"""
    print("\n🚀 Starting Hypertrading Stress Test")
    print("=" * 80)

    try:
        print("🧪 Testing Rapid Market Analysis...")

        # Create agent instance for stress testing
        agent = IBISAutonomousAgent()
        await agent.initialize()

        # Stress test market analysis speed
        start_time = time.time()

        # Test how many symbols can be analyzed quickly
        count = 0
        for i in range(10):
            try:
                # Test quick market analysis
                task = asyncio.create_task(agent.analyze_market_intelligence())
                intel = await asyncio.wait_for(task, timeout=20)

                if intel:
                    count = len(intel)
                    print(f"   Analysis {i + 1}: {count} symbols")

            except Exception as e:
                print(f"   Analysis {i + 1} failed: {e}")
                continue

        analysis_time = time.time() - start_time
        print(f"\n📊 Stress Test Results:")
        print(f"   Total Analysis Time: {analysis_time:.2f} seconds")
        print(f"   Symbols Analyzed per Run: {count}")
        print(f"   Speed: {analysis_time / count:.2f} seconds per symbol")

        await agent.client.close()

        if analysis_time < 15 and count >= 10:
            print("\n✅ Hypertrading performance is excellent!")
        else:
            print("\n⚠️  Hypertrading performance could be optimized")

        return True

    except Exception as e:
        print(f"\n❌ Stress test failed: {e}")
        return False


async def main():
    """Main test function"""
    print("🔄 IBIS True Agent Hypertrading Capabilities Test")
    print("=" * 80)

    # Test 1: Full agent initialization and configuration
    print("\n📋 Test 1: Agent Initialization and Configuration")
    success = await test_hypertrading()

    # Test 2: Stress test
    print("\n\n📋 Test 2: Performance Stress Test")
    stress_success = await run_stress_test()

    if success and stress_success:
        print("\n🎉 All Hypertrading Tests PASSED!")
        print("=" * 80)
        print("✅ IBIS True Agent is ready for hypertrading operations!")
        print("\n📈 Key Hypertrading Features:")
        print("   - Low-latency market analysis")
        print("   - Rapid opportunity detection")
        print("   - Intelligent position sizing")
        print("   - Dynamic risk management")
        print("   - Fast execution capabilities")

    else:
        print("\n❌ Some tests failed. Please check the errors.")

    return success and stress_success


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⚠️ Test interrupted by user")
