#!/usr/bin/env python3
import sys
import asyncio

sys.path.append(".")
from ibis.exchange.kucoin_client import get_kucoin_client


async def test_kucoin_client():
    try:
        print("🔍 Testing KuCoin client connection...")
        client = get_kucoin_client()
        if client is None:
            print("❌ Error: get_kucoin_client() returned None")
            return

        print("✅ Client created successfully")

        # Test symbol discovery
        print("🔍 Testing symbol discovery...")
        symbols = await client.get_symbols()
        print(f"✅ Found {len(symbols)} symbols")

        # Test ticker
        print("📈 Testing BTC-USDT ticker...")
        ticker = await client.get_ticker("BTC-USDT")
        if ticker:
            print(f"✅ BTC-USDT: ${ticker.price:.2f}")
            print(f"   24h Change: {ticker.change_24h:.2f}%")
            print(f"   Volume: ${ticker.volume_24h:,}")
        else:
            print("❌ No ticker data received")

        # Test balances
        print("💰 Testing account balances...")
        balances = await client.get_all_balances()
        if balances:
            usdt_balance = balances.get("USDT", {})
            if usdt_balance:
                print(f"✅ USDT: {usdt_balance.get('balance', 0):.2f}")
                print(f"   Available: {usdt_balance.get('available', 0):.2f}")
                print(
                    f"   On Hold: {usdt_balance.get('balance', 0) - usdt_balance.get('available', 0):.2f}"
                )
            else:
                print("⚠️ No USDT balance found")
        else:
            print("❌ No balances found")

        await client.close()
        print("✅ KuCoin client test passed!")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback

        print(traceback.format_exc())


asyncio.run(test_kucoin_client())
