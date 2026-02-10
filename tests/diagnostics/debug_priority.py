#!/usr/bin/env python3
"""
Debug priority symbols selection
"""

import sys

sys.path.insert(0, "/root/projects/Dont enter unless solicited/AGI Trader")
from ibis_true_agent import IBISTrueAgent
import asyncio


async def debug_priority_selection():
    agent = IBISTrueAgent()
    await agent.initialize()

    print("🐛 DEBUG PRIORITY SYMBOLS")
    print("=" * 50)

    # Manually replicate the symbol scoring logic
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

    holdings = list(agent.state["positions"].keys())
    top_candidates = [sym for sym, score in symbol_scores[:25]]
    priority_symbols = holdings + top_candidates
    priority_symbols = priority_symbols[:30]

    print(f"📊 Priority Symbols Construction:")
    print(f"   Holdings ({len(holdings)}): {holdings}")
    print(f"   Top Candidates ({len(top_candidates)}): {top_candidates[:5]}...")
    print(f"   Priority List ({len(priority_symbols)}):")

    for i, sym in enumerate(priority_symbols):
        if sym in holdings:
            print(f"   {i + 1}. 🛡️ {sym} (Holding)")
        elif sym in top_candidates:
            for score_sym, score in symbol_scores:
                if score_sym == sym:
                    print(f"   {i + 1}. 📈 {sym} (Score: {score:.1f})")
                    break

    print(f"\n🎯 Meme Coins in Priority List:")
    meme_coins = ["BABYDOGE", "VINU", "XEN", "MANYU", "SATS"]
    for sym in meme_coins:
        if sym in priority_symbols:
            print(f"   ✅ {sym} at position {priority_symbols.index(sym) + 1}")
        else:
            print(f"   ❌ {sym} not in priority list")

    print(f"\n✅ Priority symbols verification complete")


asyncio.run(debug_priority_selection())
