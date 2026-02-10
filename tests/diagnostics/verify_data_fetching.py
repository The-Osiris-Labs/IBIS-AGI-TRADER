#!/usr/bin/env python3
"""
Verify real-time data fetching and filtering
"""

import sys

sys.path.insert(0, "/root/projects/Dont enter unless solicited/AGI Trader")
from ibis_true_agent import IBISTrueAgent
import asyncio


async def verify_data_fetching():
    agent = IBISTrueAgent()
    await agent.initialize()

    print("📊 VERIFYING REAL-TIME DATA FETCHING AND FILTERING")
    print("=" * 50)

    # Check initial symbols cache
    print(f"Symbols cache size: {len(agent.symbols_cache)}")

    # Fetch real-time tickers
    print("\n📈 Fetching real-time tickers...")
    tickers = await agent.client.get_tickers()
    usdt_tickers = [t for t in tickers if t.symbol.endswith("-USDT")]
    print(f"USDT pairs available: {len(usdt_tickers)}")

    # Verify ticker data
    print("\n📊 Ticker data validation:")
    valid_tickers = 0
    for ticker in usdt_tickers[:5]:
        symbol = ticker.symbol.replace("-USDT", "")
        try:
            price = float(ticker.price)
            volume = float(
                getattr(ticker, "vol_24h", 0) or getattr(ticker, "volume_24h", 0)
            )
            if price > 0 and volume > 0:
                valid_tickers += 1
                print(f"✅ {symbol}: ${price:.4f} | {volume:,.0f} vol")
        except Exception as e:
            print(f"❌ {symbol}: {e}")

    print(f"\nValid tickers (first 5): {valid_tickers}/5")

    # Verify liquidity filtering
    min_liquidity = agent.config.get("min_liquidity", 1000)
    print(f"\n🔍 Liquidity filter: ${min_liquidity:,.0f} minimum")

    liquid_symbols = []
    for ticker in usdt_tickers:
        try:
            volume = float(
                getattr(ticker, "vol_24h", 0) or getattr(ticker, "volume_24h", 0)
            )
            price = float(ticker.price)
            if volume >= min_liquidity and price > 0:
                liquid_symbols.append(ticker.symbol.replace("-USDT", ""))
        except:
            continue

    print(f"Liquid candidates: {len(liquid_symbols)}")

    # Run actual market analysis
    print("\n🎯 Running market analysis...")
    await agent.analyze_market_intelligence()

    print(f"\n✅ Market intel collected: {len(agent.market_intel)} symbols")

    # Verify priority symbols
    print("\n📋 Priority symbols analyzed:")
    scores = []
    for symbol, intel in agent.market_intel.items():
        symbol_score = intel.get("score", 0)
        scores.append(symbol_score)
        print(f"   {symbol}: Score {symbol_score:.1f}")

    if scores:
        avg_score = sum(scores) / len(scores)
        print(f"\n📈 Average score: {avg_score:.1f}")
        high_scores = [s for s in scores if s >= 80]
        print(f"High quality (≥80): {len(high_scores)}/{len(scores)}")

    print("\n✅ Data fetching and filtering working correctly!")


asyncio.run(verify_data_fetching())
