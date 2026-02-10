#!/usr/bin/env python3
"""
Debug potential score calculation for meme coins
"""

import sys

sys.path.insert(0, "/root/projects/Dont enter unless solicited/AGI Trader")
from ibis_true_agent import IBISTrueAgent
import asyncio


async def debug_score_calculation():
    agent = IBISTrueAgent()
    await agent.initialize()

    print("🧐 DEBUGGING POTENTIAL SCORE CALCULATION")
    print("=" * 50)

    tickers = await agent.client.get_tickers()
    usdt_tickers = [t for t in tickers if t.symbol.endswith("-USDT")]

    # Build ticker map
    ticker_map = {}
    for t in usdt_tickers:
        sym = t.symbol.replace("-USDT", "")
        ticker_map[sym] = t

    print(f"Processing {len(agent.symbols_cache)} symbols...")

    min_liquidity = agent.config.get("min_liquidity", 1000)
    symbol_scores = []

    for sym in agent.symbols_cache:
        ticker = ticker_map.get(sym)
        if not ticker:
            continue

        try:
            price = float(ticker.price)
            volume_24h = float(ticker.volume_24h or 0)
            change_24h = float(ticker.change_24h or 0)

            high_24h = float(getattr(ticker, "high_24h", price * 1.01))
            low_24h = float(getattr(ticker, "low_24h", price * 0.99))
            volatility = (high_24h - low_24h) / price if high_24h > low_24h else 0.02

            volume_score = min(volume_24h / (min_liquidity * 10), 1) * 40
            volatility_score = min(volatility / 0.05, 1) * 30
            momentum_score = min(abs(change_24h) / 5.0, 1) * 30
            total_score = volume_score + volatility_score + momentum_score

            symbol_scores.append((sym, total_score))

            # Print meme coin scores specifically
            if sym in ["BABYDOGE", "VINU", "XEN", "MANYU", "SATS"]:
                print(f"   📈 {sym}: Score {total_score:.1f}")

        except Exception as e:
            continue

    # Sort and check rankings
    symbol_scores.sort(key=lambda x: x[1], reverse=True)
    print(f"\nTop 30 Scores:")
    for i, (sym, score) in enumerate(symbol_scores[:30]):
        print(f"   {i + 1}. {sym}: {score:.1f}")

    print(f"\n✅ Debug complete")


asyncio.run(debug_score_calculation())
