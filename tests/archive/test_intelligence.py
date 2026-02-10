#!/usr/bin/env python3
import asyncio
from ibis.market_intelligence import MarketIntelligence


async def test_intelligence():
    mi = MarketIntelligence()

    # Test CoinGecko integration
    print("📊 Testing CoinGecko API...")
    symbols = ["bitcoin", "ethereum", "solana", "cardano", "ripple"]
    market_data = await mi.coingecko_get_market_data(symbols)

    if market_data:
        print(f"✅ Success! Got data for {len(market_data)} symbols")

        for symbol, data in market_data.items():
            print(f"\n🎯 {symbol.capitalize()}:")
            print(f"   Price: ${data['price']:.2f}")
            print(f"   Market Cap: ${data['market_cap']:,}")
            print(f"   Volume 24h: ${data['volume_24h']:,}")
            print(f"   24h Change: {data['change_24h']:.2f}%")
            print(f"   7d Change: {data['change_7d']:.2f}%")

            # Calculate intelligence score
            score = mi.calculate_intelligence_score(symbol, data)
            print(f"   Intelligence Score: {score:.1f}/100")

            # Generate insights
            insights = await mi.generate_insights({symbol: data})
            if insights.get(symbol):
                print("   Insights:")
                for insight in insights[symbol]:
                    print(f"     - {insight}")
    else:
        print("❌ Failed to get market data from CoinGecko")


asyncio.run(test_intelligence())
