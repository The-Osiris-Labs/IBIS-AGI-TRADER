#!/usr/bin/env python3
"""
Check potential scores for meme coins
"""

import sys

sys.path.insert(0, "/root/projects/Dont enter unless solicited/AGI Trader")
from ibis_true_agent import IBISTrueAgent
import asyncio


async def check_potential_scores():
    agent = IBISTrueAgent()
    await agent.initialize()

    print("📊 CHECKING POTENTIAL SCORES FOR MEME COINS")
    print("=" * 50)

    # Get all tickers
    tickers = await agent.client.get_tickers()
    usdt_tickers = [t for t in tickers if t.symbol.endswith("-USDT")]

    meme_coins = ["BABYDOGE", "VINU", "XEN", "MANYU", "SATS"]

    print("🔍 MEME COIN ANALYSIS:")
    for sym in meme_coins:
        ticker = next((t for t in usdt_tickers if t.symbol == f"{sym}-USDT"), None)
        if not ticker:
            print(f"   ❌ {sym}: Not found")
            continue

        try:
            price = float(ticker.price)
            volume_24h = float(ticker.volume_24h or 0)
            change_24h = float(ticker.change_24h or 0)

            # Calculate volatility
            high_24h = float(getattr(ticker, "high_24h", price * 1.01))
            low_24h = float(getattr(ticker, "low_24h", price * 0.99))
            volatility = (high_24h - low_24h) / price if high_24h > low_24h else 0.02

            min_liquidity = agent.config.get("min_liquidity", 1000)

            volume_score = min(volume_24h / (min_liquidity * 10), 1) * 40
            volatility_score = min(volatility / 0.05, 1) * 30
            momentum_score = min(abs(change_24h) / 5.0, 1) * 30
            total_score = volume_score + volatility_score + momentum_score

            print(f"   📈 {sym}:")
            print(f"      Price: ${price:.6f}")
            print(f"      Volume: ${volume_24h / 1e6:.1f}M")
            print(f"      24h Change: {change_24h:.2f}%")
            print(f"      Volatility: {volatility:.3f}")
            print(f"      Volume Score: {volume_score:.1f}")
            print(f"      Volatility Score: {volatility_score:.1f}")
            print(f"      Momentum Score: {momentum_score:.1f}")
            print(f"      Total Score: {total_score:.1f}")

        except Exception as e:
            print(f"   ❌ {sym}: Error - {e}")

    print("\n✅ Potential score calculation verified")


asyncio.run(check_potential_scores())
