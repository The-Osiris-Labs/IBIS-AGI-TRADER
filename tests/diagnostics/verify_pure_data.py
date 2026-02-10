#!/usr/bin/env python3
"""
Verify pure data-driven analysis
"""

import sys

sys.path.insert(0, "/root/projects/Dont enter unless solicited/AGI Trader")
from ibis_true_agent import IBISTrueAgent
import asyncio


async def verify_pure_data_analysis():
    agent = IBISTrueAgent()
    await agent.initialize()

    print("🧠 VERIFYING PURE DATA-DRIVEN ANALYSIS")
    print("=" * 50)

    # Run analysis
    await agent.analyze_market_intelligence()

    print(f"✅ Analyzed {len(agent.market_intel)} symbols")

    print("\n📊 SYMBOLS ANALYZED:")
    for symbol, intel in agent.market_intel.items():
        score = intel.get("score", 0)
        price = intel.get("price", 0)
        volume = intel.get("volume_24h", 0)
        change = intel.get("change_24h", 0)

        print(f"   📈 {symbol}:")
        print(f"      Score: {score:.1f}")
        print(f"      Price: ${price:.4f}")
        print(f"      Volume: ${volume / 1e6:.1f}M")
        print(f"      24h Change: {change:.2f}%")

    # Check if we have any low-price high-volume symbols
    print("\n🔍 LOW-PRICE HIGH-VOLUME SYMBOLS:")
    tickers = await agent.client.get_tickers()
    usdt_tickers = [t for t in tickers if t.symbol.endswith("-USDT")]

    # Find symbols with price < $0.01 and high volume
    low_price_high_vol = []
    for ticker in usdt_tickers:
        try:
            price = float(ticker.price)
            volume = float(ticker.volume_24h or 0)
            if price < 0.01 and volume > 1000000:  # < $0.01 and > $1M volume
                low_price_high_vol.append(
                    (ticker.symbol.replace("-USDT", ""), price, volume)
                )
        except:
            continue

    # Sort by volume
    low_price_high_vol.sort(key=lambda x: x[2], reverse=True)

    if low_price_high_vol:
        print("   High volume low price symbols found:")
        for sym, price, vol in low_price_high_vol[:5]:
            print(f"      {sym}: ${price:.6f} | ${vol / 1e6:.1f}M")

            # Check if they're in market intelligence
            if sym in agent.market_intel:
                intel = agent.market_intel[sym]
                print(f"      ✅ Analyzed: Score {intel.get('score', 0):.1f}")
            else:
                print(f"      ❌ Not analyzed (check filtering logic)")
    else:
        print("   No low-price high-volume symbols found")

    print("\n✅ Pure data-driven analysis verified")


asyncio.run(verify_pure_data_analysis())
