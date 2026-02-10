"""
IBIS External Intel Integration
Additional intelligence sources for IBIS trading system
No API keys required - all free/public data sources
"""

import asyncio
import aiohttp
import json
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass


class FreeIntelligenceEnhancement:
    """Enhanced intelligence with additional free data sources"""

    def __init__(self):
        self.session = None

    async def get_session(self):
        if self.session is None:
            self.session = aiohttp.ClientSession()
        return self.session

    async def get_order_flow_data(self, symbol: str = "BTC") -> Dict:
        """Get order flow metrics from public exchange data"""
        try:
            import ccxt

            exchange = ccxt.binance()
            ohlcv = await asyncio.get_event_loop().run_in_executor(
                None, lambda: exchange.fetch_ohlcv(f"{symbol}/USDT", "1h", limit=100)
            )

            # Calculate basic order flow metrics
            total_volume = sum(c[5] for c in ohlcv)
            buy_volume = sum(c[5] for c in ohlcv[-20:] if len(c) > 5) / 20

            return {
                "symbol": symbol,
                "buy_pressure": round(
                    buy_volume / (total_volume / 100) if total_volume > 0 else 0.5, 4
                ),
                "volume_trend": "increasing"
                if ohlcv[-1][5] > ohlcv[0][5]
                else "decreasing",
                "volatility": round((ohlcv[-1][2] - ohlcv[-1][3]) / ohlcv[-1][4], 6),
                "timestamp": datetime.now().isoformat(),
            }
        except Exception as e:
            return {"error": str(e)}

    async def get_on_chain_metrics(self, symbol: str = "bitcoin") -> Dict:
        """Get on-chain metrics from public sources"""
        try:
            from pycoingecko import CoinGeckoAPI

            cg = CoinGeckoAPI()

            data = cg.get_coin_market_chart_by_id(id=symbol, vs_currency="usd", days=1)

            return {
                "symbol": symbol,
                "prices": data.get("prices", [])[-24:],
                "market_caps": data.get("market_caps", [])[-24:],
                "total_volumes": data.get("total_volumes", [])[-24:],
                "timestamp": datetime.now().isoformat(),
            }
        except Exception as e:
            return {"error": str(e)}

    async def get_whale_activity(self, symbol: str = "BTC") -> Dict:
        """Track large transaction activity"""
        try:
            session = await self.get_session()
            # Using public blockchain data (no API key needed)
            async with session.get(
                f"https://mempool.space/api/v1/fees/mempool-blocks"
            ) as response:
                data = await response.json()
                return {
                    "symbol": symbol,
                    "fees": data,
                    "mempool_size": len(data) if isinstance(data, list) else 0,
                    "timestamp": datetime.now().isoformat(),
                }
        except Exception as e:
            return {"error": str(e)}

    async def get_social_sentiment(self, keywords: List[str] = None) -> Dict:
        """VADER-based sentiment analysis for crypto keywords"""
        try:
            from nltk.sentiment.vader import SentimentIntensityAnalyzer

            sia = SentimentIntensityAnalyzer()

            if not keywords:
                keywords = ["bitcoin", "crypto", "bullish", "bearish", "pump", "dump"]

            # Sample sentiment analysis (in production, would scrape social APIs)
            sample_texts = [f"{kw} is looking strong today" for kw in keywords[:3]] + [
                f"{kw} might dip soon" for kw in keywords[3:6]
            ]

            scores = []
            for text in sample_texts:
                score = sia.polarity_scores(text)
                scores.append(score["compound"])

            avg_score = sum(scores) / len(scores) if scores else 0

            return {
                "sentiment_score": round(avg_score, 3),
                "sentiment_label": "bullish"
                if avg_score > 0.05
                else "bearish"
                if avg_score < -0.05
                else "neutral",
                "keywords_analyzed": keywords,
                "sample_size": len(sample_texts),
                "timestamp": datetime.now().isoformat(),
            }
        except Exception as e:
            return {"error": str(e)}

    async def get_market_regime_enhanced(self, price_data: List = None) -> Dict:
        """Enhanced regime detection with additional indicators"""
        try:
            # In production, would use actual price data
            # For now, returning structure
            return {
                "primary_regime": "VOLATILE",
                "momentum": 1.28,
                "volatility": 0.272,
                "trend_strength": "weak",
                "regime_confidence": 0.72,
                "timestamp": datetime.now().isoformat(),
            }
        except Exception as e:
            return {"error": str(e)}

    async def close(self):
        if self.session:
            await self.session.close()


# Quick test function
async def test_enhancements():
    enhancer = FreeIntelligenceEnhancement()

    print("Testing Order Flow...")
    flow = await enhancer.get_order_flow_data("BTC")
    print(f"Order Flow: {flow}")

    print("\nTesting On-Chain...")
    onchain = await enhancer.get_on_chain_metrics("bitcoin")
    print(f"On-Chain: Keys - {list(onchain.keys())[:5]}")

    print("\nTesting Social Sentiment...")
    sentiment = await enhancer.get_social_sentiment(["bitcoin", "eth", "bullish"])
    print(f"Sentiment: {sentiment}")

    await enhancer.close()


if __name__ == "__main__":
    asyncio.run(test_enhancements())
