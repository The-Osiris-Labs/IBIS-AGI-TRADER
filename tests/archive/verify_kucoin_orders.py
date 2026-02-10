#!/usr/bin/env python3
import asyncio
from ibis.exchange.kucoin_client import get_kucoin_client


async def verify_kucoin_app_orders():
    client = get_kucoin_client()

    print("🔍 Verifying KuCoin API state:")
    print("=" * 60)

    # Get detailed order history
    orders = await client.get_recent_fills(limit=10)

    print(f"📊 Last 10 Order History:")
    for i, order in enumerate(orders[:10], 1):
        symbol = order.get("symbol", "N/A")
        side = order.get("side", "N/A").upper()
        price = order.get("price", 0)
        size = float(order.get("size", 0))
        deal_size = float(order.get("dealSize", 0))
        is_active = order.get("isActive", False)
        status = "Active" if is_active else "Completed"

        print(f"{i:2d}. {symbol:<10} {side:<4} ${price:>8.2f} x {size:>8.4f}")
        print(f"    Status: {status} | Filled: {deal_size:.4f}/{size:.4f}")
        print(
            f"    Fee: {float(order.get('fee', 0)):.8f} {order.get('feeCurrency', 'USDT')}"
        )
        print()

    # Check current prices
    print("📈 Current Prices:")
    for symbol in ["AAVE-USDT", "KCS-USDT", "BTC-USDT"]:
        try:
            ticker = await client.get_ticker(symbol)
            print(f"{symbol:<10} ${float(ticker.price):.2f}")
        except Exception as e:
            print(f"{symbol:<10} ❌ Error: {e}")

    # Check market data
    print("\n🏦 Account Overview:")
    balances = await client.get_all_balances()
    for currency, data in balances.items():
        if currency != "USDT":
            try:
                ticker = await client.get_ticker(f"{currency}-USDT")
                price = float(ticker.price)
                value = data["balance"] * price
                print(
                    f"{currency:<5} {data['balance']:>15.8f} @ ${price:>8.2f} = ${value:>12.2f}"
                )
            except:
                print(f"{currency:<5} {data['balance']:>15.8f}")


asyncio.run(verify_kucoin_app_orders())
