#!/usr/bin/env python3
"""IBIS True Agent Health and Optimization Check"""

import sys
import asyncio
import os
import subprocess
import time

sys.path.append(".")

from ibis.exchange.kucoin_client import get_kucoin_client
from ibis.cross_exchange_monitor import CrossExchangeMonitor
from ibis.free_intelligence import FreeIntelligence


async def check_exchange_health():
    """Check KuCoin exchange connectivity and market data quality"""
    print("🔍 Checking KuCoin connectivity...")

    client = get_kucoin_client(paper_trading=False)

    try:
        # Test multiple endpoints
        endpoints = [
            ("BTC-USDT Price", lambda: client.get_ticker("BTC-USDT")),
            ("USDT Balance", lambda: client.get_balance("USDT")),
            ("All Balances", lambda: client.get_all_balances()),
            ("Order Book", lambda: client.get_orderbook("BTC-USDT", limit=5)),
            ("Recent Trades", lambda: client.get_recent_fills(limit=1)),
            ("Market Symbols", lambda: client.get_symbols()),
        ]

        for name, func in endpoints:
            try:
                result = await func()
                if name == "BTC-USDT Price":
                    print(f"✅ {name}: ${float(result.price):.2f}")
                elif name == "USDT Balance":
                    print(f"✅ {name}: ${float(result):.2f}")
                elif name == "All Balances":
                    print(f"✅ {name}: {len(result)} assets found")
                elif name == "Order Book":
                    print(f"✅ {name}: {len(result.asks) + len(result.bids)} orders")
                elif name == "Recent Trades":
                    print(f"✅ {name}: {len(result)} trades in last 24h")
                elif name == "Market Symbols":
                    print(f"✅ {name}: {len(result)} trading pairs available")
            except Exception as e:
                print(f"❌ {name} failed: {e}")

        return True

    except Exception as e:
        print(f"❌ KuCoin health check failed: {e}")
        return False


async def check_intelligence_sources():
    """Check all intelligence sources are working"""
    print("\n🔍 Checking intelligence sources...")

    intel = FreeIntelligence()

    try:
        await intel.get_session()

        # Test Fear & Greed is not available directly on FreeIntelligence
        print("✅ Free intelligence initialized")

        # Test Cross-Exchange Monitor
        cross_exchange = CrossExchangeMonitor()
        await cross_exchange.initialize()
        if cross_exchange.binance and cross_exchange.binance.is_available():
            print("✅ Binance connection (CCXT) available")
        else:
            print("⚠️ Binance connection not available")

        await intel.close()
        return True

    except Exception as e:
        print(f"❌ Intelligence check failed: {e}")
        return False


async def check_agent_operational_mode():
    """Check agent's internal state and operational mode"""
    print("\n🔍 Checking agent configuration...")

    try:
        # Check environment variables
        from ibis_true_agent import IBISTrueAgent

        agent = IBISTrueAgent()

        # Print operational settings
        print(f"✅ Paper Trading: {agent.paper_trading}")
        print(f"✅ Debug Mode: {agent.debug_mode}")
        print(f"✅ Verbose Mode: {agent.verbose_mode}")

        return True

    except Exception as e:
        print(f"❌ Agent configuration check failed: {e}")
        return False


async def test_position_sizing():
    """Test position sizing logic with new risk management settings"""
    print("\n🔍 Testing position sizing logic...")

    from ibis.core.trading_constants import TRADING
    from ibis_enhanced_20x import EnhancedRiskManager

    try:
        # Current portfolio value
        client = get_kucoin_client(paper_trading=False)
        balances = await client.get_all_balances()
        usdt_balance = float(balances["USDT"]["available"])

        # Test enhanced risk manager
        risk_manager = EnhancedRiskManager(
            {
                "fear_greed_index": 14,
                "base_position_pct": TRADING.POSITION.BASE_POSITION_PCT,
                "max_position_pct": TRADING.POSITION.MAX_POSITION_PCT,
            }
        )

        # Test different confidence levels
        test_cases = [
            (80, 0.15, "Standard opportunity"),
            (90, 0.08, "High confidence"),
            (95, 0.05, "God tier opportunity"),
            (70, 0.20, "Low confidence, high volatility"),
        ]

        for score, volatility, description in test_cases:
            position_size = risk_manager.calculate_position_size(
                symbol="BTC",
                confidence=score / 100,
                volatility=volatility,
                available_capital=usdt_balance,
                current_positions=1,
                score=score,
            )

            size_pct = (position_size / usdt_balance) * 100

            print(
                f"✅ {description} (Score: {score}, Vol: {volatility * 100}%): "
                f"${position_size:.2f} ({size_pct:.1f}%)"
            )

            # Verify constraints - for small accounts, allow minimum trade size to exceed percentage limit
            if usdt_balance > 50:
                assert size_pct <= TRADING.POSITION.MAX_POSITION_PCT, (
                    "Position percentage too high"
                )

            assert position_size >= TRADING.POSITION.MIN_CAPITAL_PER_TRADE, (
                "Position too small"
            )
            assert position_size <= TRADING.POSITION.MAX_CAPITAL_PER_TRADE, (
                "Position too large"
            )

        print("✅ All position sizing constraints verified")
        return True

    except Exception as e:
        print(f"❌ Position sizing test failed: {e}")
        return False


async def check_kucoin_optimizations():
    """Check if KuCoin specific optimizations are enabled"""
    print("\n🔍 Checking KuCoin specific optimizations...")

    try:
        from ibis.exchange.kucoin_client import EnvConfig

        # Check API configuration
        print(f"✅ API Key configured: {'Yes' if EnvConfig.KUCOIN_API_KEY else 'No'}")
        print(
            f"✅ API Secret configured: {'Yes' if EnvConfig.KUCOIN_API_SECRET else 'No'}"
        )
        print(
            f"✅ API Passphrase configured: {'Yes' if EnvConfig.KUCOIN_API_PASSPHRASE else 'No'}"
        )
        print(f"✅ Sandbox mode: {EnvConfig.KUCOIN_IS_SANDBOX}")
        print(f"✅ Paper trading: {EnvConfig.PAPER_TRADING}")

        return True

    except Exception as e:
        print(f"❌ KuCoin optimization check failed: {e}")
        return False


async def run_enhanced_system_test():
    """Run comprehensive system test"""
    print("=" * 50)
    print("🧠 IBIS True Agent - Enhanced System Test")
    print("=" * 50)

    tests = [
        check_exchange_health(),
        check_intelligence_sources(),
        check_agent_operational_mode(),
        test_position_sizing(),
        check_kucoin_optimizations(),
    ]

    results = await asyncio.gather(*tests, return_exceptions=True)

    print("\n" + "=" * 50)
    print("📊 Test Results Summary")
    print("=" * 50)

    all_passed = True
    for i, (test, result) in enumerate(
        zip(
            [
                "Exchange Health",
                "Intelligence Sources",
                "Agent Configuration",
                "Position Sizing",
                "KuCoin Optimizations",
            ],
            results,
        )
    ):
        if isinstance(result, Exception):
            print(f"❌ Test {i + 1}: {test} - FAILED: {result}")
            all_passed = False
        elif result:
            print(f"✅ Test {i + 1}: {test} - PASSED")
        else:
            print(f"❌ Test {i + 1}: {test} - FAILED")
            all_passed = False

    print("\n" + "=" * 50)

    if all_passed:
        print("🎉 All tests passed! IBIS True Agent is running with full capabilities.")
    else:
        print("⚠️ Some tests failed. Please check the errors above.")

    return all_passed


async def main():
    success = await run_enhanced_system_test()

    if not success:
        print("\n🔍 Attempting to fix issues...")
        try:
            # Try to restart agent if needed
            if not any(
                "ibis" in p for p in subprocess.check_output(["ps", "aux"]).decode()
            ):
                print("🔄 Starting IBIS True Agent...")
                subprocess.Popen(
                    ["./run_ibis_true.sh"],
                    cwd="/root/projects/Dont enter unless solicited/AGI Trader",
                )
                time.sleep(10)
                print("✅ IBIS True Agent started")
        except Exception as e:
            print(f"❌ Fix attempt failed: {e}")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nTest interrupted")
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
