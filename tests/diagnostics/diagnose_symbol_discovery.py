#!/usr/bin/env python3
"""
Diagnostic script to verify symbol discovery and filtering logic
"""

import asyncio
import sys

sys.path.insert(0, "/root/projects/Dont enter unless solicited/AGI Trader")

from ibis_true_agent import IBISTrueAgent


async def diagnose_symbol_discovery():
    print("=== IBIS Symbol Discovery Diagnostic ===")
    print()

    agent = IBISTrueAgent()
    await agent.initialize()

    try:
        # Test symbol discovery
        print("1. Testing trading pair discovery...")
        await agent.discover_market()
        print(f"   Found {len(agent.symbols_cache)} trading pairs")
        if agent.symbols_cache:
            print(f"   First 10 symbols: {agent.symbols_cache[:10]}")

        print()

        # Test balance retrieval
        print("2. Testing balance retrieval...")
        balances = await agent.client.get_all_balances()
        holdings = [
            c
            for c in balances.keys()
            if c != "USDT" and float(balances.get(c, {}).get("balance", 0)) > 0
        ]
        print(f"   Holdings: {holdings}")

        print()

        # Test ticker data
        print("3. Testing ticker data fetch...")
        tickers = await agent.client.get_tickers()
        ticker_map = {
            t.symbol.replace("-USDT", ""): t for t in tickers if t.symbol.endswith("-USDT")
        }
        print(f"   Got {len(ticker_map)} USDT pairs")

        print()

        # Test filtering logic
        print("4. Testing symbol filtering logic...")
        min_liquidity = 100000  # $100k min
        qualified = []

        for sym in agent.symbols_cache:
            ticker = ticker_map.get(sym)
            if not ticker:
                continue

            try:
                price = float(ticker.price)
                volume_24h = float(
                    getattr(ticker, "vol_24h", 0) or getattr(ticker, "volume_24h", 0) or 0
                )
                change_24h = float(getattr(ticker, "change_24h", 0) or 0)
                high_24h = float(getattr(ticker, "high_24h", price * 1.01) or price * 1.01)
                low_24h = float(getattr(ticker, "low_24h", price * 0.99) or price * 0.99)

                volatility = (high_24h - low_24h) / price

                # Volatile market filtering
                if volume_24h >= min_liquidity * 0.8 and volatility > 0.02:
                    qualified.append(sym)

            except Exception as e:
                print(f"   ⚠️ Error analyzing {sym}: {e}")
                continue

        print(f"   Qualified symbols: {len(qualified)}")
        if qualified:
            print(f"   First 10 qualified: {qualified[:10]}")

        print()

        # Test scoring
        print("5. Testing symbol scoring...")
        scores = []
        for sym in qualified:
            ticker = ticker_map.get(sym)
            if not ticker:
                continue

            try:
                price = float(ticker.price)
                volume_24h = float(
                    getattr(ticker, "vol_24h", 0) or getattr(ticker, "volume_24h", 0) or 0
                )
                change_24h = float(getattr(ticker, "change_24h", 0) or 0)
                high_24h = float(getattr(ticker, "high_24h", price * 1.01) or price * 1.01)
                low_24h = float(getattr(ticker, "low_24h", price * 0.99) or price * 0.99)

                volatility = (high_24h - low_24h) / price

                volume_score = min(volume_24h / (min_liquidity * 10), 1) * 40
                volatility_score = min(volatility / 0.05, 1) * 30
                momentum_score = min(abs(change_24h) / 5.0, 1) * 30
                total_score = volume_score + volatility_score + momentum_score

                scores.append((sym, total_score))

            except Exception as e:
                print(f"   ⚠️ Error scoring {sym}: {e}")
                continue

        scores.sort(key=lambda x: x[1], reverse=True)
        print(f"   Scored {len(scores)} symbols")
        if scores:
            print("   Top 10 scores:")
            for sym, score in scores[:10]:
                print(f"   {sym}: {score:.1f}")

        print()

        # Test final priority list
        print("6. Testing priority symbol selection...")
        top_candidates = [sym for sym, score in scores[:25]]
        priority_symbols = holdings + top_candidates
        priority_symbols = priority_symbols[:30]
        print(f"   Priority symbols ({len(priority_symbols)}):")
        print(f"   {priority_symbols}")

        print()
        print("=== Diagnostics Complete ===")

    except Exception as e:
        print(f"❌ Diagnostic error: {e}")
        import traceback

        print(f"\n{traceback.format_exc()}")

    finally:
        # No shutdown method needed
        pass


if __name__ == "__main__":
    try:
        asyncio.run(diagnose_symbol_discovery())
    except KeyboardInterrupt:
        print("\nDiagnostic interrupted")
