#!/usr/bin/env python3
"""
Debug why meme coins aren't being analyzed
"""

import sys

sys.path.insert(0, "/root/projects/Dont enter unless solicited/AGI Trader")
from ibis_true_agent import IBISTrueAgent
import asyncio


async def debug_analysis():
    agent = IBISTrueAgent()
    await agent.initialize()

    print("🐛 DEBUGGING ANALYSIS EXECUTION")
    print("=" * 50)

    # Get all symbols and their potential scores
    tickers = await agent.client.get_tickers()
    usdt_tickers = [t for t in tickers if t.symbol.endswith("-USDT")]

    ticker_map = {}
    for t in usdt_tickers:
        sym = t.symbol.replace("-USDT", "")
        ticker_map[sym] = t

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

        except Exception as e:
            continue

    symbol_scores.sort(key=lambda x: x[1], reverse=True)
    print(f"Top 30 Potential Scores:")
    for i, (sym, score) in enumerate(symbol_scores[:30]):
        print(f"   {i + 1}. {sym}: {score:.1f}")

    meme_coins = ["BABYDOGE", "VINU", "XEN", "MANYU", "SATS"]
    print(f"\nMeme Coin Rankings:")
    for sym in meme_coins:
        for i, (s, score) in enumerate(symbol_scores):
            if s == sym:
                print(f"   {sym}: Rank #{i + 1} (Score: {score:.1f})")
                break

    print(f"\n=== STARTING ACTUAL ANALYSIS ===")

    await agent.analyze_market_intelligence()

    print(f"\n=== ANALYSIS COMPLETED ===")
    print(f"Number of symbols analyzed: {len(agent.market_intel)}")

    print(f"\nSymbols Analyzed:")
    for sym, data in agent.market_intel.items():
        print(f"   {sym}: Score {data.get('score', 'N/A'):.1f}")

    print(f"\n✅ Debug complete")


asyncio.run(debug_analysis())
