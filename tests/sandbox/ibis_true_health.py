#!/usr/bin/env python3
"""
🦅 IBIS True Agent - Comprehensive Health Check Module
=====================================================
Validates all components are functioning correctly.
"""

import asyncio
import sys
from datetime import datetime


async def check_all():
    """Run comprehensive health check"""
    print("=" * 60)
    print("🦅 IBIS HEALTH CHECK")
    print("=" * 60)
    print(f"Timestamp: {datetime.now().isoformat()}")
    print()

    all_passed = True

    # Check 1: Core Imports
    print("📦 Checking Core Imports...")
    try:
        from ibis_true_agent import IBISTrueAgent
        from ibis.free_intelligence import FreeIntelligence
        from ibis.core.config import Config
        from ibis.cross_exchange_monitor import CrossExchangeMonitor

        print("   ✅ All imports successful")
    except Exception as e:
        print(f"   ❌ Import failed: {e}")
        all_passed = False

    # Check 2: Configuration
    print("\n⚙️ Checking Configuration...")
    try:
        assert Config.MIN_CAPITAL_PER_TRADE == 5.0, "MIN_CAPITAL_PER_TRADE should be $5"
        assert Config.MAX_POSITIONS == 20, "MAX_POSITIONS should be 20"
        assert Config.MIN_VIABLE_TARGET == 0.008, "MIN_VIABLE_TARGET should be 0.8%"
        print(f"   ✅ MIN_CAPITAL_PER_TRADE: ${Config.MIN_CAPITAL_PER_TRADE}")
        print(f"   ✅ MAX_POSITIONS: {Config.MAX_POSITIONS}")
        print(f"   ✅ MIN_VIABLE_TARGET: {Config.MIN_VIABLE_TARGET * 100}%")
    except AssertionError as e:
        print(f"   ⚠️ Configuration mismatch: {e}")
        all_passed = False

    # Check 3: Agent Initialization
    print("\n🤖 Checking Agent Initialization...")
    try:
        agent = IBISTrueAgent()
        assert hasattr(agent, "update_positions_awareness"), (
            "Missing position awareness"
        )
        assert hasattr(agent, "learn_from_experience"), "Missing self-learning"
        assert hasattr(agent, "update_adaptive_risk"), "Missing adaptive risk"
        assert hasattr(agent, "detect_market_regime"), "Missing regime detection"
        assert hasattr(agent, "get_holdings_intelligence"), (
            "Missing holdings intelligence"
        )
        print("   ✅ All AGI methods present")
    except Exception as e:
        print(f"   ❌ Agent initialization failed: {e}")
        all_passed = False

    # Check 4: Free Intelligence
    print("\n🧠 Checking Free Intelligence...")
    try:
        intel = FreeIntelligence()
        assert hasattr(intel, "get_fear_greed_index"), "Missing Fear & Greed"
        assert hasattr(intel, "get_reddit_sentiment"), "Missing Reddit sentiment"
        assert hasattr(intel, "get_cmc_sentiment"), "Missing CMC sentiment"
        assert hasattr(intel, "get_onchain_metrics"), "Missing on-chain metrics"
        print("   ✅ All intelligence methods present")
    except Exception as e:
        print(f"   ❌ Free intelligence check failed: {e}")
        all_passed = False

    # Check 5: Cross-Exchange Monitor
    print("\n🔗 Checking Cross-Exchange Monitor...")
    try:
        monitor = CrossExchangeMonitor()
        assert hasattr(monitor, "initialize"), "Missing initialize"
        assert hasattr(monitor, "get_price_lead_signal"), "Missing price lead signal"
        assert hasattr(monitor, "close"), "Missing close"
        print("   ✅ Cross-Exchange methods present")
    except Exception as e:
        print(f"   ❌ Cross-exchange check failed: {e}")
        all_passed = False

    # Check 6: Symbol Format Helpers
    print("\n🔄 Checking Symbol Format Helpers...")
    try:
        agent = IBISTrueAgent()
        assert agent.to_full_symbol("BTC") == "BTC-USDT", "to_full_symbol failed"
        assert agent.to_full_symbol("BTC-USDT") == "BTC-USDT", (
            "to_full_symbol already USDT failed"
        )
        assert agent.to_currency("BTC-USDT") == "BTC", "to_currency failed"
        print("   ✅ Symbol format helpers working")
    except AssertionError as e:
        print(f"   ❌ Symbol format error: {e}")
        all_passed = False

    # Summary
    print("\n" + "=" * 60)
    if all_passed:
        print("✅ ALL HEALTH CHECKS PASSED")
        print("🦅 IBIS IS READY FOR DEPLOYMENT")
    else:
        print("⚠️ SOME CHECKS FAILED - REVIEW ABOVE")
    print("=" * 60)

    return all_passed


async def check_exchange_connection():
    """Check if exchange is accessible"""
    print("\n" + "=" * 60)
    print("🌐 EXCHANGE CONNECTION CHECK")
    print("=" * 60)

    try:
        from ibis.exchange.kucoin_client import get_kucoin_client

        client = get_kucoin_client()
        balances = await client.get_all_balances()
        print(f"   ✅ Connected to KuCoin")
        print(f"   ✅ Balances accessible: {len(balances)} assets")

        await client.close()
        return True
    except Exception as e:
        print(f"   ❌ Exchange connection failed: {e}")
        return False


async def check_database():
    """Check database integrity"""
    print("\n" + "=" * 60)
    print("🗄️ DATABASE INTEGRITY CHECK")
    print("=" * 60)

    try:
        from ibis.database.db import IbisDB

        db = IbisDB()
        positions = db.get_open_positions()
        trades = db.get_trades(limit=10)

        print(f"   ✅ Database accessible")
        print(f"   ✅ Open positions: {len(positions)}")
        print(f"   ✅ Recent trades: {len(trades)}")

        return True
    except Exception as e:
        print(f"   ❌ Database check failed: {e}")
        return False


async def full_check():
    """Run complete system check"""
    print("\n" + "=" * 60)
    print("🦅 IBIS COMPREHENSIVE SYSTEM CHECK")
    print("=" * 60)

    results = []

    # Run all checks
    results.append(("Core Imports", await check_all()))
    results.append(("Exchange", await check_exchange_connection()))
    results.append(("Database", await check_database()))

    # Summary
    print("\n" + "=" * 60)
    print("📊 CHECK SUMMARY")
    print("=" * 60)

    passed = 0
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {status}: {name}")
        if result:
            passed += 1

    print()
    print(f"Total: {passed}/{len(results)} checks passed")
    print("=" * 60)

    return passed == len(results)


if __name__ == "__main__":
    success = asyncio.run(full_check())
    sys.exit(0 if success else 1)
