"""
IBIS True Agent - Comprehensive Market Intelligence Module
=========================================================
Integrates with leading cryptocurrency market intelligence APIs to provide
deep, high-quality market insights for better trading decisions.
"""

import os
import requests
import aiohttp
import asyncio
import json
import time
from datetime import datetime, timedelta


class MarketIntelligence:
    """
    Comprehensive market intelligence aggregator that combines data from
    multiple premium sources to provide deep market insights.
    """

    def __init__(self):
        # API endpoints
        self.COINGECKO_API = "https://api.coingecko.com/api/v3"
        self.COINGECKO_PRO_API = "https://pro-api.coingecko.com/api/v3"
        self.GLASSNODE_API = "https://api.glassnode.com/v1"
        self.MESSARI_API = "https://api.messari.io/api/v1"
        self.COINAPI_BASE = "https://rest.coinapi.io"
        self.NANSEN_API = "https://api.nansen.ai/v1"

        # API keys (from environment or configuration)
        self.api_keys = {
            "coingecko": "",
            "glassnode": os.environ.get("GLASSNODE_API_KEY", ""),
            "messari": os.environ.get("MESSARI_API_KEY", ""),
            "coinapi": os.environ.get("COINAPI_API_KEY", ""),
            "nansen": os.environ.get("NANSEN_API_KEY", ""),
        }

        # Cache for API responses
        self.cache = {}
        self.cache_timeout = 60  # 60 seconds cache
        self._session = None

    async def _get_session(self):
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession()
        return self._session

    async def close(self):
        if self._session and not self._session.closed:
            await self._session.close()

    async def _make_request(
        self, url, params=None, headers=None, timeout=10, max_retries=3
    ):
        """Make asynchronous HTTP request with retry logic and maximum retries"""
        session = await self._get_session()
        for attempt in range(max_retries):
            try:
                async with session.get(
                    url,
                    params=params,
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=timeout),
                ) as response:
                    if response.status == 200:
                        return await response.json()
                    elif response.status == 429:
                        # Rate limit - wait and retry
                        if attempt < max_retries - 1:
                            wait_time = 10 * (attempt + 1)
                            await asyncio.sleep(wait_time)
                            continue
                        raise Exception("Rate limit exceeded - too many retries")
                    elif response.status == 403:
                        raise Exception(f"Access forbidden: {await response.text()}")
                    elif response.status == 404:
                        raise Exception(f"Resource not found: {await response.text()}")
                    else:
                        raise Exception(
                            f"HTTP error {response.status}: {await response.text()}"
                        )
            except Exception as e:
                if attempt < max_retries - 1:
                    await asyncio.sleep(1 * (attempt + 1))
                    continue
                raise Exception(
                    f"Request failed after {max_retries} attempts: {str(e)}"
                )

    async def coingecko_get_market_data(self, symbols, currency="usd"):
        """
        Get comprehensive market data from CoinGecko - handles symbol mapping to IDs
        """
        mapping = {
            "BTC": "bitcoin",
            "ETH": "ethereum",
            "KCS": "kucoin-shares",
            "SOL": "solana",
            "BNB": "binancecoin",
            "XRP": "ripple",
            "ADA": "cardano",
            "DOT": "polkadot",
            "AVAX": "avalanche-2",
            "LINK": "chainlink",
            "MATIC": "polygon",
            "LTC": "litecoin",
        }

        results = {}
        missing_ids = []
        id_to_orig = {}

        for s in symbols:
            base = s.split("-")[0].upper()
            cg_id = mapping.get(base, base.lower())

            cache_key = f"cg_{cg_id}"
            if cache_key in self.cache and (
                time.time() - self.cache[cache_key]["timestamp"] < 300
            ):  # 5m cache
                results[s] = self.cache[cache_key]["data"]
            else:
                missing_ids.append(cg_id)
                id_to_orig[cg_id] = s

        if not missing_ids:
            return results

        try:
            params = {
                "vs_currency": currency,
                "ids": ",".join(missing_ids),
                "price_change_percentage": "1h,24h,7d,30d",
            }

            url = f"{self.COINGECKO_API}/coins/markets"
            data = await self._make_request(url, params=params)

            for item in data:
                cg_id = item["id"]
                orig_s = id_to_orig.get(cg_id)
                if not orig_s:
                    continue

                processed = {
                    "price": item["current_price"],
                    "market_cap": item["market_cap"],
                    "volume_24h": item["total_volume"],
                    "change_1h": item.get("price_change_percentage_1h_in_currency", 0)
                    or 0,
                    "change_24h": item.get("price_change_percentage_24h_in_currency", 0)
                    or 0,
                    "change_7d": item.get("price_change_percentage_7d_in_currency", 0)
                    or 0,
                    "change_30d": item.get("price_change_percentage_30d_in_currency", 0)
                    or 0,
                    "high_24h": item.get("high_24h", 0) or 0,
                    "low_24h": item.get("low_24h", 0) or 0,
                    "sparkline": item.get("sparkline_in_7d"),
                    "last_updated": item.get("last_updated"),
                }

                # Cache per symbol
                self.cache[f"cg_{cg_id}"] = {
                    "data": processed,
                    "timestamp": time.time(),
                }
                results[orig_s] = processed

            return results

        except Exception as e:
            print(f"CG Batch error: {e}")
            return results  # Return whatever we got from cache

    async def coingecko_get_coin_details(self, coin_id):
        """Get detailed coin information from CoinGecko"""
        cache_key = f"coingecko_details_{coin_id}"
        if cache_key in self.cache and (
            time.time() - self.cache[cache_key]["timestamp"] < self.cache_timeout * 10
        ):
            return self.cache[cache_key]["data"]

        try:
            url = f"{self.COINGECKO_API}/coins/{coin_id}"
            data = await self._make_request(url)

            processed_data = {
                "name": data["name"],
                "symbol": data["symbol"],
                "description": data["description"]["en"],
                "categories": data["categories"],
                "market_data": data["market_data"],
                "developer_data": data["developer_data"],
                "community_data": data["community_data"],
                "links": data["links"],
            }

            self.cache[cache_key] = {"data": processed_data, "timestamp": time.time()}

            return processed_data

        except Exception as e:
            print(f"CoinGecko details error: {e}")
            return {}

    async def glassnode_get_onchain_data(self, symbol, metric, frequency="24h"):
        """Get on-chain metrics from Glassnode"""
        if not self.api_keys["glassnode"]:
            return None

        cache_key = f"glassnode_{symbol}_{metric}_{frequency}"
        if cache_key in self.cache and (
            time.time() - self.cache[cache_key]["timestamp"] < self.cache_timeout
        ):
            return self.cache[cache_key]["data"]

        try:
            url = f"{self.GLASSNODE_API}/metrics/{metric}"
            params = {"a": symbol.upper(), "i": frequency}
            headers = {"X-Api-Key": self.api_keys["glassnode"]}

            data = await self._make_request(url, params=params, headers=headers)

            self.cache[cache_key] = {"data": data, "timestamp": time.time()}

            return data

        except Exception as e:
            # Silence expected API failures for non-critical data
            return None

    async def messari_get_asset_data(self, symbol):
        """Get institutional-grade metrics from Messari"""
        cache_key = f"messari_{symbol}"
        if cache_key in self.cache and (
            time.time() - self.cache[cache_key]["timestamp"] < self.cache_timeout
        ):
            return self.cache[cache_key]["data"]

        try:
            url = f"{self.MESSARI_API}/assets/{symbol}/metrics"
            params = {"metrics": "price,marketcap,volume,returns"}

            if self.api_keys["messari"]:
                headers = {"x-messari-api-key": self.api_keys["messari"]}
            else:
                headers = None

            data = await self._make_request(url, params=params, headers=headers)

            processed_data = {
                "price": data["data"]["metrics"]["market_data"]["price"],
                "market_cap": data["data"]["metrics"]["market_data"]["marketcap"],
                "volume_24h": data["data"]["metrics"]["market_data"]["volume"],
                "returns": data["data"]["metrics"]["market_data"]["returns"],
                "supply": data["data"]["metrics"]["supply"],
                "rank": data["data"]["metrics"]["rank"],
            }

            self.cache[cache_key] = {"data": processed_data, "timestamp": time.time()}

            return processed_data

        except Exception as e:
            # Silence expected API failures for non-critical data
            return {}

    async def coinapi_get_orderbook(self, symbol, limit=20):
        """Get real-time order book data from CoinAPI"""
        if not self.api_keys["coinapi"]:
            return None

        cache_key = f"coinapi_orderbook_{symbol}"
        if cache_key in self.cache and (
            time.time() - self.cache[cache_key]["timestamp"] < self.cache_timeout / 2
        ):
            return self.cache[cache_key]["data"]

        try:
            url = f"{self.COINAPI_BASE}/v1/orderbooks/{symbol}/latest"
            params = {"limit": limit}
            headers = {"X-CoinAPI-Key": self.api_keys["coinapi"]}

            data = await self._make_request(url, params=params, headers=headers)

            processed_data = {
                "symbol": data["symbol_id"],
                "timestamp": data["time_exchange"],
                "asks": data["asks"],
                "bids": data["bids"],
                "spread": data["asks"][0][0] - data["bids"][0][0],
            }

            self.cache[cache_key] = {"data": processed_data, "timestamp": time.time()}

            return processed_data

        except Exception as e:
            # Silence expected API failures for non-critical data
            return None

    async def nansen_get_smart_money(self, symbol):
        """Get smart money tracking data from Nansen"""
        if not self.api_keys["nansen"]:
            return None

        cache_key = f"nansen_smartmoney_{symbol}"
        if cache_key in self.cache and (
            time.time() - self.cache[cache_key]["timestamp"] < self.cache_timeout * 5
        ):
            return self.cache[cache_key]["data"]

        try:
            url = f"{self.NANSEN_API}/smart-money-flow"
            params = {"symbol": symbol, "timeframe": "24h"}
            headers = {"Authorization": f"Bearer {self.api_keys['nansen']}"}

            data = await self._make_request(url, params=params, headers=headers)

            self.cache[cache_key] = {"data": data, "timestamp": time.time()}

            return data

        except Exception as e:
            # Silence expected API failures for non-critical data
            return None

    async def get_combined_intelligence(self, symbols):
        """
        Get comprehensive, combined intelligence for multiple symbols
        """
        intelligence = {}

        # Get CoinGecko market data
        coingecko_data = await self.coingecko_get_market_data(symbols)

        # Process each symbol
        for symbol in symbols:
            if symbol in coingecko_data:
                # Base intelligence from CoinGecko
                base = coingecko_data[symbol]
                base_sym = symbol.split("-")[0].upper()  # Extract BTC from BTC-USDT

                intelligence[symbol] = {
                    "price": base["price"],
                    "market_cap": base["market_cap"],
                    "volume_24h": base["volume_24h"],
                    "change_1h": base["change_1h"],
                    "change_24h": base["change_24h"],
                    "change_7d": base["change_7d"],
                    "change_30d": base["change_30d"],
                    "high_24h": base["high_24h"],
                    "low_24h": base["low_24h"],
                    "last_updated": base["last_updated"],
                    "sparkline": base["sparkline"],
                    "metrics": {},
                }

                # Get additional metrics using base symbol
                glassnode_data = await self.glassnode_get_onchain_data(
                    base_sym, "market/price_usd"
                )
                if glassnode_data:
                    intelligence[symbol]["metrics"]["glassnode"] = glassnode_data

                messari_data = await self.messari_get_asset_data(base_sym)
                if messari_data:
                    intelligence[symbol]["metrics"]["messari"] = messari_data

                nansen_data = await self.nansen_get_smart_money(base_sym)
                if nansen_data:
                    intelligence[symbol]["metrics"]["nansen"] = nansen_data

        return intelligence

    async def generate_insights(self, intelligence):
        """
        Generate comprehensive insights based on combined intelligence
        """
        insights = {}

        for symbol, data in intelligence.items():
            symbol_insights = []

            # Trend analysis
            if data["change_24h"] > 5:
                symbol_insights.append("📈 Strong uptrend detected")
            elif data["change_24h"] < -5:
                symbol_insights.append("📉 Strong downtrend detected")
            elif -1 < data["change_24h"] < 1:
                symbol_insights.append("➡️ Sideways consolidation")

            # Volume analysis
            if data["volume_24h"] > data["market_cap"] * 0.1:
                symbol_insights.append("💥 High trading activity")
            elif data["volume_24h"] < data["market_cap"] * 0.01:
                symbol_insights.append("🔄 Low trading volume")

            # Momentum analysis
            if data["change_1h"] > 1 and data["change_24h"] > 2:
                symbol_insights.append("🚀 Building momentum")
            elif data["change_1h"] < -1 and data["change_24h"] < -2:
                symbol_insights.append("💨 Losing momentum")

            # Volatility analysis
            range_24h = data["high_24h"] - data["low_24h"]
            volatility = range_24h / data["price"]
            if volatility > 0.1:
                symbol_insights.append("🎢 High volatility")
            elif volatility < 0.02:
                symbol_insights.append("📊 Low volatility")

            # Market structure
            if data["price"] > data["high_24h"] * 0.95:
                symbol_insights.append("🎯 Near resistance")
            elif data["price"] < data["low_24h"] * 1.05:
                symbol_insights.append("🛡️ Near support")

            insights[symbol] = symbol_insights

        return insights

    def calculate_intelligence_score(self, symbol, intelligence):
        """Calculate comprehensive intelligence score (0-100)"""

        data = (
            intelligence.get(symbol)
            if isinstance(intelligence, dict) and symbol in intelligence
            else intelligence
        )

        if not isinstance(data, dict) or "change_24h" not in data:
            return 50.0

        score = 0
        base_score = 0

        chg_24h = data.get("change_24h", 0)
        chg_7d = data.get("change_7d", 0)
        chg_1h = data.get("change_1h", 0)

        if chg_24h > 5:
            base_score += 20
        elif chg_24h > 2:
            base_score += 15
        elif chg_24h > 0:
            base_score += 10
        elif chg_24h > -2:
            base_score += 5
        elif chg_24h > -5:
            base_score += 2

        if chg_7d > 10:
            base_score += 15
        elif chg_7d > 5:
            base_score += 10
        elif chg_7d > 0:
            base_score += 5

        mcap = data.get("market_cap", 0)
        vol = data.get("volume_24h", 0)
        if mcap > 0:
            vol_ratio = vol / mcap
            if vol_ratio > 0.1:
                base_score += 20
            elif vol_ratio > 0.05:
                base_score += 15
            elif vol_ratio > 0.02:
                base_score += 10
            elif vol_ratio > 0.01:
                base_score += 5

        if chg_1h > 1 and chg_24h > 1:
            base_score += 15
        elif chg_1h > 0.5 and chg_24h > 0:
            base_score += 10
        elif chg_1h > 0 and chg_24h > 0:
            base_score += 5

        price = data.get("price", 0)
        if price > 0:
            high_24h = data.get("high_24h", price)
            low_24h = data.get("low_24h", price)
            volatility = (high_24h - low_24h) / price if high_24h > low_24h else 0
            if 0.03 < volatility < 0.08:
                base_score += 10
            elif volatility < 0.05:
                base_score += 5

        if "metrics" in data:
            metrics = data["metrics"]
            if "messari" in metrics:
                messari = metrics["messari"]
                base_score += 5
                mcap = messari.get("marketcap", 0)
                if mcap > 1000000000:
                    base_score += 3
                if messari.get("price", 0) > 0:
                    base_score += 2
            if "glassnode" in metrics:
                glassnode = metrics["glassnode"]
                base_score += 5
                if glassnode.get("whale_tx_count", 0) > 100:
                    base_score += 3
            if "nansen" in metrics:
                nansen = metrics["nansen"]
                base_score += 5
                if nansen.get("smart_money_balance_change", 0) > 0:
                    base_score += 5
                elif nansen.get("smart_money_balance_change", 0) < 0:
                    base_score -= 5
            if "social" in metrics:
                base_score += 5
                social = metrics["social"]
                if social.get("sentiment", 0) > 0.6:
                    base_score += 3
                elif social.get("sentiment", 0) < 0.4:
                    base_score -= 3

        score = max(0, min(100, base_score))
        return float(score)


# Global instance for singleton pattern
market_intelligence = MarketIntelligence()
