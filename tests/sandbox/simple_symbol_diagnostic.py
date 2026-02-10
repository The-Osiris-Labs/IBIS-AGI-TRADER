#!/usr/bin/env python3
"""
Simple diagnostic to test KuCoin API and symbol discovery
"""

import asyncio
import sys

sys.path.insert(0, "/root/projects/Dont enter unless solicited/AGI Trader")

from ibis.exchange.kucoin_client import get_kucoin_client


async def simple_diagnostic():
    print("=== Simple Symbol Discovery Diagnostic ===")
    print()

    try:
        client = get_kucoin_client()

        print("1. Fetching all trading symbols...")
        symbols = await client.get_symbols()
        usdt_pairs = [
            s.get("symbol", "")
            for s in symbols
            if s.get("symbol", "").endswith("-USDT")
        ]
        print(f"   Total symbols: {len(symbols)}")
        print(f"   USDT pairs: {len(usdt_pairs)}")
        if usdt_pairs:
            print(f"   First 10 USDT pairs: {usdt_pairs[:10]}")

        print()

        print("2. Fetching tickers...")
        tickers = await client.get_tickers()
        ticker_map = {
            t.symbol.replace("-USDT", ""): t
            for t in tickers
            if t.symbol.endswith("-USDT")
        }
        print(f"   Tickers received: {len(ticker_map)}")

        print()

        print("3. Fetching balances...")
        balances = await client.get_all_balances()
        holdings = [
            c
            for c in balances.keys()
            if c != "USDT" and float(balances.get(c, {}).get("balance", 0)) > 0
        ]
        print(f"   Holdings: {holdings}")

        print()

        print("4. Testing filtering logic with volatility > 2% and volume > $80k...")
        qualified = []
        min_liquidity = 100000

        for sym in ticker_map:
            ticker = ticker_map[sym]

            try:
                price = float(ticker.price)
                volume_24h = float(
                    getattr(ticker, "vol_24h", 0)
                    or getattr(ticker, "volume_24h", 0)
                    or 0
                )
                change_24h = float(getattr(ticker, "change_24h", 0) or 0)
                high_24h = float(
                    getattr(ticker, "high_24h", price * 1.01) or price * 1.01
                )
                low_24h = float(
                    getattr(ticker, "low_24h", price * 0.99) or price * 0.99
                )

                volatility = (high_24h - low_24h) / price

                if volume_24h >= min_liquidity * 0.8 and volatility > 0.02:
                    score = (
                        min(volume_24h / (min_liquidity * 10), 1) * 40
                        + min(volatility / 0.05, 1) * 30
                        + min(abs(change_24h) / 5.0, 1) * 30
                    )
                    qualified.append((sym, score, volume_24h, volatility, change_24h))

            except Exception as e:
                print(f"   ⚠️ Error with {sym}: {e}")
                continue

        qualified.sort(key=lambda x: x[1], reverse=True)
        print(f"   Qualified symbols: {len(qualified)}")
        if qualified:
            print("\n   Top 20 qualified symbols:")
            print("   Symbol     Score   Volume($)  Volatility  Change(24h)")
            print("   ---------  ------  ----------  ----------  -----------")
            for sym, score, vol, volat, change in qualified[:20]:
                print(
                    f"   {sym:9} {score:6.1f}  {vol:9,.0f}  {volat:8.2%}  {change:9.2f}%"
                )

        print()

        print("=== Diagnostic Complete ===")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback

        print(f"\n{traceback.format_exc()}")


if __name__ == "__main__":
    try:
        asyncio.run(simple_diagnostic())
    except KeyboardInterrupt:
        print("\nDiagnostic interrupted")
