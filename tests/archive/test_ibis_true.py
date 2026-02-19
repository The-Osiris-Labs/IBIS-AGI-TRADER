#!/usr/bin/env python3
"""
🧪 IBIS TRUE TRADER - Comprehensive System Verification
=========================================================
Tests all core components of the IBIS True Trader system
"""

import asyncio
import sys
import os
from pathlib import Path
import pytest

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


@pytest.mark.asyncio
async def test_kucoin_client():
    """Test KuCoin API client functionality"""
    print("🔍 Testing KuCoin client...")

    try:
        from ibis.exchange.kucoin_client import get_kucoin_client

        client = get_kucoin_client()

        # Test connection
        print("   ✅ Client initialized")

        # Test symbol discovery
        symbols = await client.get_symbols()
        print(f"   ✅ Found {len(symbols)} trading pairs")

        # Test ticker data
        btc_ticker = await client.get_ticker("BTC-USDT")
        if btc_ticker and hasattr(btc_ticker, "price"):
            print(f"   ✅ BTC-USDT price: ${btc_ticker.price:.2f}")

        return True

    except Exception as e:
        print(f"   ❌ KuCoin client error: {e}")
        import traceback

        traceback.print_exc()
        return False


@pytest.mark.asyncio
async def test_ibis_true_agent():
    """Test IBIS True Agent initialization"""
    print("\n🔍 Testing IBIS True Agent...")

    try:
        from ibis_true_agent import IBISAutonomousAgent

        agent = IBISAutonomousAgent()

        # Test initialization
        assert agent is not None
        print("   ✅ Agent initialized")

        # Test memory loading
        assert agent.agent_memory is not None
        print("   ✅ Memory loaded")

        # Test state management
        assert agent.state is not None
        print("   ✅ State loaded")

        return True

    except Exception as e:
        print(f"   ❌ Agent initialization error: {e}")
        import traceback

        traceback.print_exc()
        return False


@pytest.mark.asyncio
async def test_symbol_rules():
    """Test symbol rules loading"""
    print("\n🔍 Testing symbol rules...")

    try:
        from ibis.exchange.kucoin_client import get_kucoin_client

        client = get_kucoin_client()
        symbols = await client.get_symbols()

        assert symbols is not None
        assert isinstance(symbols, list)
        assert len(symbols) > 0

        print(f"   ✅ Loaded rules for {len(symbols)} symbols")

        # Test specific symbol rules
        test_symbols = ["BTC-USDT", "ETH-USDT", "SOL-USDT"]
        found_count = 0
        for sym in symbols:
            symbol = sym.get("symbol", "")
            if symbol in test_symbols:
                print(
                    f"   ✅ {symbol}: Min: {sym.get('baseMinSize')}, Inc: {sym.get('baseIncrement')}"
                )
                found_count += 1

        assert found_count == len(test_symbols)
        print(f"   ✅ All {found_count} test symbols found")

        return True

    except Exception as e:
        print(f"   ❌ Symbol rules error: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_configuration():
    """Test configuration file validity"""
    print("\n🔍 Testing configuration...")

    try:
        # Test keys.env file
        keys_path = PROJECT_ROOT / "ibis" / "keys.env"
        assert keys_path.exists()

        with open(keys_path, "r") as f:
            content = f.read()

        assert "KUCOIN_API_KEY" in content
        assert "KUCOIN_API_SECRET" in content
        assert "KUCOIN_API_PASSPHRASE" in content

        print("   ✅ API keys configured")

        # Test requirements file
        requirements_path = PROJECT_ROOT / "requirements.txt"
        assert requirements_path.exists()

        print("   ✅ Dependencies configured")

    except Exception as e:
        print(f"   ❌ Configuration error: {e}")
        import traceback

        traceback.print_exc()
        assert False


def test_file_structure():
    """Test project file structure"""
    print("\n🔍 Testing file structure...")

    required_files = [
        "ibis_true_agent.py",
        "requirements.txt",
        "README.md",
        "ibis/keys.env",
        "ibis/exchange/kucoin_client.py",
        "ibis/exchange/__init__.py",
        ".gitignore",
    ]

    all_valid = True

    for file_path in required_files:
        full_path = PROJECT_ROOT / file_path
        if full_path.exists():
            print(f"   ✅ {file_path} exists")
        else:
            print(f"   ❌ {file_path} missing")
            all_valid = False

    assert all_valid


async def main():
    """Main verification function"""
    print("=" * 60)
    print("🧪 IBIS TRUE TRADER - SYSTEM VERIFICATION")
    print("=" * 60)

    tests = [
        test_configuration(),
        await test_kucoin_client(),
        await test_ibis_true_agent(),
        await test_symbol_rules(),
        test_file_structure(),
    ]

    passed = sum(1 for test in tests if test)
    failed = len(tests) - passed

    print("\n" + "=" * 60)
    print(f"📊 VERIFICATION SUMMARY: {passed}/{len(tests)} tests passed")
    print("=" * 60)

    if failed == 0:
        print("\n✅ IBIS TRUE TRADER SYSTEM IS FULLY OPERATIONAL!")
        print("\n🎉 ALL TESTS PASSED! THE SACRED BIRD IS READY TO TRADE!")
        return True
    else:
        print(f"\n❌ SYSTEM VERIFICATION FAILED: {failed} tests failed")
        print("\n⚠️  Please fix the failed tests before running the true trader")
        return False


if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Verification interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Critical error during verification: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
