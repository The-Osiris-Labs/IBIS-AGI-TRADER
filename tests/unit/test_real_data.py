#!/usr/bin/env python3
"""Test script to verify if IBIS is connected to real KuCoin API"""

import sys
import asyncio

sys.path.append(".")

from ibis.exchange.kucoin_client import get_kucoin_client
from ibis.cross_exchange_monitor import CrossExchangeMonitor


async def test_kucoin_connection():
    print("🔍 Testing KuCoin connection...")
    client = get_kucoin_client(paper_trading=False)

    try:
        # Test getting ticker for BTC-USDT
        ticker = await client.get_ticker("BTC-USDT")
        if ticker:
            print(f"✅ BTC-USDT price: ${float(ticker.price):.2f}")
        else:
            print("❌ Failed to get BTC-USDT price")

        # Test getting account balances
        balances = await client.get_all_balances()
        print(f"✅ Account balances: {len(balances)} assets found")
        if "USDT" in balances:
            print(f"   USDT balance: {float(balances['USDT']['available']):.2f}")

        return True

    except Exception as e:
        print(f"❌ KuCoin connection failed: {e}")
        return False


async def test_binance_connection():
    print("\n🔍 Testing Binance connection...")
    cross_exchange = CrossExchangeMonitor()

    try:
        await cross_exchange.initialize()

        # Test getting BTC price from Binance
        client = get_kucoin_client(paper_trading=False)
        btc_ticker = await client.get_ticker("BTC-USDT")
        if btc_ticker:
            lead_signal = await cross_exchange.get_price_lead_signal(
                "BTC", float(btc_ticker.price)
            )
            if lead_signal and "binance_price" in lead_signal:
                print(f"✅ Binance BTC price: ${lead_signal['binance_price']:.2f}")
            else:
                print(f"✅ Binance connection working but no price data: {lead_signal}")

        return True

    except Exception as e:
        print(f"❌ Binance connection failed: {e}")
        return False


async def test_actual_vs_log_data():
    print("\n🔍 Testing actual market data vs log data...")

    client = get_kucoin_client(paper_trading=False)

    try:
        # Get current ADI price (from log)
        adi_ticker = await client.get_ticker("ADI-USDT")
        if adi_ticker:
            print(f"✅ ADI-USDT current price: ${float(adi_ticker.price):.4f}")
        else:
            print("❌ Failed to get ADI-USDT price")

        # Get current AIO price
        aio_ticker = await client.get_ticker("AIO-USDT")
        if aio_ticker:
            print(f"✅ AIO-USDT current price: ${float(aio_ticker.price):.4f}")
        else:
            print("❌ Failed to get AIO-USDT price")

        # Get current ALEPH price
        aleph_ticker = await client.get_ticker("ALEPH-USDT")
        if aleph_ticker:
            print(f"✅ ALEPH-USDT current price: ${float(aleph_ticker.price):.4f}")
        else:
            print("❌ Failed to get ALEPH-USDT price")

        # Get current AERGO price
        aergo_ticker = await client.get_ticker("AERGO-USDT")
        if aergo_ticker:
            print(f"✅ AERGO-USDT current price: ${float(aergo_ticker.price):.4f}")
        else:
            print("❌ Failed to get AERGO-USDT price")

    except Exception as e:
        print(f"❌ Error getting symbol prices: {e}")


async def main():
    print("=== IBIS True Agent Data Source Verification ===")

    # Test connections
    kucoin_ok = await test_kucoin_connection()
    binance_ok = await test_binance_connection()

    # Test actual market data
    if kucoin_ok:
        await test_actual_vs_log_data()

    print("\n=== Test Complete ===")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nTest interrupted")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
