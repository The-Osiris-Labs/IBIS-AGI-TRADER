#!/usr/bin/env python3
import asyncio
from ibis.exchange.kucoin_client import get_kucoin_client


async def quick_portfolio_check():
    client = get_kucoin_client(paper_trading=False)

    print("=== QUICK PORTFOLIO ANALYSIS ===")

    # Get balances
    balances = await client.get_all_balances()

    print(f"\n📊 Exchange Balances:")
    print(f"  USDT Total: ${balances.get('USDT', {}).get('balance', 0):.2f}")
    print(f"  USDT Available: ${balances.get('USDT', {}).get('available', 0):.2f}")

    holdings = []
    total_holdings_value = 0.0

    for currency, data in balances.items():
        if currency == "USDT":
            continue

        balance = data["balance"]
        available = data["available"]
        if balance > 0:
            try:
                ticker = await client.get_ticker(f"{currency}-USDT")
                price = ticker.price
                value = balance * price
                holdings.append(
                    {
                        "currency": currency,
                        "balance": balance,
                        "price": price,
                        "value": value,
                    }
                )
                total_holdings_value += value
                print(f"\n  {currency}:")
                print(f"    Balance: {balance:.8f}")
                print(f"    Price: ${price:.6f}")
                print(f"    Value: ${value:.2f}")
            except Exception as e:
                print(f"\n  ⚠️  {currency}: Error fetching price: {e}")

    total_account_value = (
        balances.get("USDT", {}).get("balance", 0) + total_holdings_value
    )
    print(f"\n💰 Total Account Value: ${total_account_value:.2f}")

    # Get open orders
    open_orders = await client.get_open_orders()
    print(f"\n📝 Open Orders: {len(open_orders)}")
    if open_orders:
        for order in open_orders:
            symbol = getattr(order, "symbol", "Unknown").replace("-USDT", "")
            side = getattr(order, "side", "Unknown")
            price = getattr(order, "price", 0)
            size = getattr(order, "size", 0)
            print(f"  • {symbol} {side}: {size} @ ${price}")

    # Get recent trades (last 24 hours)
    recent_trades = await client.get_recent_fills(limit=50)
    print(f"\n📈 Recent Trades: {len(recent_trades)}")

    await client.close()


asyncio.run(quick_portfolio_check())
