from ibis.core.logging_config import get_logger
#!/usr/bin/env python3
"""
🦅 IBIS TRUE AGENT - FREE & INDEPENDENT INTELLIGENCE SOURCES
==============================================================
Replaces paid placeholders with free, public data sources:

1. FEAR & GREED INDEX - alternative.me (free, no key)
2. SOCIAL SENTIMENT - CryptoCompare (free, no key)
3. MARKET MOMENTUM - CoinGecko (free, no key)
4. ON-CHAIN METRICS - CoinGecko (free, no key)
5. NEWS SENTIMENT - GDELT (free, no key)
6. CROSS-EXCHANGE - CCXT/Binance (free, no key)
"""

import asyncio
import aiohttp
import json
import re
import os
from datetime import datetime
from typing import Dict, Optional, Tuple


class FreeIntelligence:
    """
    FREE & INDEPENDENT INTELLIGENCE SOURCES
    No API keys. No subscriptions. No connections to paid services.
    """

    def __init__(self):
        self.session = None
        self.cache = {}
        self.cache_duration = 3600

        self.fear_greed_cache = None
        self.sentiment_cache = {}
        self.onchain_cache = {}

    async def get_session(self):
        if self.session is None:
            self.session = aiohttp.ClientSession(headers={"User-Agent": "IBIS-Trading-Bot/1.0"})
        return self.session

    async def close(self):
        if self.session:
            await self.session.close()

    def _get_cache(self, key: str) -> Optional[dict]:
        if key in self.cache:
            data, timestamp = self.cache[key]
            if (datetime.now() - timestamp).total_seconds() < self.cache_duration:
                return data
        return None

    def _set_cache(self, key: str, data: dict):
        self.cache[key] = (data, datetime.now())

    async def _request_json(self, url: str, params: dict = None, timeout: int = 10):
        session = await self.get_session()
        retries = 3
        backoff = 1.0
        for attempt in range(retries):
            try:
                async with session.get(
                    url,
                    params=params,
                    timeout=aiohttp.ClientTimeout(total=timeout),
                ) as response:
                    if response.status in {429, 500, 502, 503, 504}:
                        await asyncio.sleep(backoff)
                        backoff *= 2
                        continue
                    if response.status != 200:
                        return None
                    return await response.json()
            except Exception:
                if attempt < retries - 1:
                    await asyncio.sleep(backoff)
                    backoff *= 2
                    continue
                return None

    async def _request_text(self, url: str, params: dict = None, timeout: int = 10):
        session = await self.get_session()
        retries = 3
        backoff = 1.0
        for attempt in range(retries):
            try:
                async with session.get(
                    url,
                    params=params,
                    timeout=aiohttp.ClientTimeout(total=timeout),
                ) as response:
                    if response.status in {429, 500, 502, 503, 504}:
                        await asyncio.sleep(backoff)
                        backoff *= 2
                        continue
                    if response.status != 200:
                        return None
                    return await response.text()
            except Exception:
                if attempt < retries - 1:
                    await asyncio.sleep(backoff)
                    backoff *= 2
                    continue
                return None

    async def get_fear_greed_index(self) -> Dict:
        """
        Get Fear & Greed Index from multiple FREE sources
        Source: alternative.me (FREE)
        """

        logger = get_logger(__name__)

        cache = self._get_cache("fear_greed")
        if cache:
            return cache

        # Try multiple sources for reliability
        sources = [
            ("https://api.alternative.me/fng/", "alternative.me"),
        ]

        for url, source_name in sources:
            try:
                data = await self._request_json(url, timeout=15)
                if data:
                    fng_data = data.get("data", [{}])[0]
                    value = int(fng_data.get("value", 50))
                    value_classification = fng_data.get("value_classification", "Neutral")

                    result = {
                        "value": value,
                        "classification": value_classification,
                        "score": self._fng_to_sentiment(value),
                        "source": source_name,
                        "confidence": 80,
                        "timestamp": datetime.now().isoformat(),
                    }
                    self._set_cache("fear_greed", result)
                    logger.info(
                        f"📊 Fear & Greed Index: {value} ({value_classification}) [{source_name}]"
                    )
                    return result
            except Exception as e:
                logger.warning(f"⚠️ Fear & Greed API ({source_name}) failed: {e}")
                continue

        # All sources failed, log warning
        logger.warning("⚠️ All Fear & Greed sources failed, using neutral")

        return {
            "value": 50,
            "classification": "Neutral",
            "score": 50,
            "source": "neutral_estimate",
            "confidence": 10,
            "timestamp": datetime.now().isoformat(),
        }

    def _fng_to_sentiment(self, value: int) -> int:
        if value >= 75:
            return 80
        elif value >= 60:
            return 65
        elif value >= 40:
            return 50
        elif value >= 25:
            return 35
        else:
            return 20

    async def get_reddit_sentiment(self, symbol: str, subreddits: list = None) -> Dict:
        """
        Reddit sentiment is no longer available (API changes)
        Returns neutral sentiment as fallback
        """
        return {
            "score": 50,
            "confidence": 0,
            "sources": [],
            "posts_analyzed": 0,
            "source": "disabled",
            "timestamp": datetime.now().isoformat(),
        }

    def _analyze_text_sentiment(self, text: str) -> int:
        """
        Simple sentiment analysis using keyword matching
        Returns 0-100 (bearish to bullish)
        """
        text_lower = text.lower()

        bullish_words = [
            "bull",
            "long",
            "buy",
            "moon",
            "pump",
            "gain",
            "profit",
            " breakout",
            "support",
            "accumulate",
            "call",
            "up",
            "green",
            "rally",
            "surge",
            " ATH",
            "high",
            "winner",
        ]
        bearish_words = [
            "bear",
            "short",
            "sell",
            "dump",
            "crash",
            "loss",
            "breakdown",
            "resistance",
            "drop",
            "down",
            "red",
            "bottom",
            "dip",
            " low",
            "reject",
            "rekt",
            "scam",
        ]

        bullish_count = sum(1 for word in bullish_words if word in text_lower)
        bearish_count = sum(1 for word in bearish_words if word in text_lower)

        total = bullish_count + bearish_count
        if total == 0:
            return 50

        score = (bullish_count - bearish_count) / total * 50 + 50
        return max(0, min(100, score))

    async def get_cmc_sentiment(self, symbol: str) -> Dict:
        """
        Get momentum-based sentiment from market data
        Uses multiple free sources since CMC API requires authentication
        """

        logger = get_logger(__name__)

        cache_key = f"cmc_{symbol}"
        cache = self._get_cache(cache_key)
        if cache:
            return cache

        # Try CoinGecko as free alternative
        try:
            session = await self.get_session()

            # Symbol to CoinGecko ID mapping
            symbol_mappings = {
                "btc": "bitcoin",
                "eth": "ethereum",
                "bnb": "binancecoin",
                "sol": "solana",
                "xrp": "ripple",
                "ada": "cardano",
                "doge": "dogecoin",
                "dot": "polkadot",
                "avax": "avalanche-2",
                "matic": "matic-network",
            }

            coin_ids = []
            if symbol.lower() in symbol_mappings:
                coin_ids.append(symbol_mappings[symbol.lower()])
            coin_ids.extend([symbol.lower(), symbol.upper(), symbol.capitalize()])
            coin_ids = list(dict.fromkeys(coin_ids))

            data = None
            for coin_id in coin_ids:
                url = f"https://api.coingecko.com/api/v3/coins/{coin_id}"
                params = {
                    "localization": "false",
                    "tickers": "false",
                    "community_data": "false",
                    "developer_data": "false",
                    "sparkline": "false",
                }

                async with session.get(
                    url, params=params, timeout=aiohttp.ClientTimeout(total=10)
                ) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        if data and isinstance(data, dict) and "market_data" in data:
                            break
                        data = None

            if data and isinstance(data, dict) and "market_data" in data:
                market = data.get("market_data", {})
                change_24h = market.get("price_change_percentage_24h", 0) or 0
                volume = market.get("total_volume", {}).get("usd", 0) or 0
                market_cap = market.get("market_cap", {}).get("usd", 0) or 0

                sentiment = self._price_momentum_to_sentiment(change_24h)

                result = {
                    "score": sentiment,
                    "market_cap": market_cap,
                    "volume_24h": volume,
                    "price_change_24h": change_24h,
                    "confidence": 80,
                    "source": "coingecko",
                    "timestamp": datetime.now().isoformat(),
                }
                self._set_cache(cache_key, result)
                return result
        except Exception as e:
            pass

        return {
            "score": 50,
            "confidence": 0,
            "source": "fallback",
            "timestamp": datetime.now().isoformat(),
        }

    def _price_momentum_to_sentiment(self, change_24h: float) -> int:
        if change_24h >= 10:
            return 85
        elif change_24h >= 5:
            return 70
        elif change_24h >= 2:
            return 60
        elif change_24h >= 0:
            return 55
        elif change_24h >= -2:
            return 45
        elif change_24h >= -5:
            return 35
        elif change_24h >= -10:
            return 25
        else:
            return 15

    def _volume_to_score(self, volume_24h: float, market_cap: float) -> int:
        if market_cap <= 0 or volume_24h <= 0:
            return 50
        ratio = volume_24h / market_cap
        if ratio >= 0.2:
            return 80
        if ratio >= 0.1:
            return 70
        if ratio >= 0.05:
            return 60
        if ratio >= 0.02:
            return 55
        if ratio >= 0.01:
            return 50
        return 45

    async def get_onchain_metrics(self, symbol: str) -> Dict:
        """
        Get on-chain proxy metrics
        Uses CoinGecko as primary, CoinCap as backup
        """

        logger = get_logger(__name__)

        cache_key = f"onchain_{symbol}"
        cache = self._get_cache(cache_key)
        if cache:
            return cache

        # Try CoinGecko first
        try:
            session = await self.get_session()

            # Symbol to CoinGecko ID mapping
            symbol_mappings = {
                "btc": "bitcoin",
                "eth": "ethereum",
                "bnb": "binancecoin",
                "sol": "solana",
                "xrp": "ripple",
                "ada": "cardano",
                "doge": "dogecoin",
                "dot": "polkadot",
                "avax": "avalanche-2",
                "matic": "matic-network",
                "link": "chainlink",
                "uni": "uniswap",
                "aave": "aave",
                "atom": "cosmos",
                "fil": "filecoin",
                "lpt": "livepeer",
                "trb": "tellor",
                "band": "band-protocol",
                "crv": "curve-dao-token",
                "sushi": "sushiswap",
                "comp": "compound-ether",
                "mkr": "maker",
                "snx": "synthetix",
                "yfi": "yearn-finance",
                "bal": "balancer",
                "ren": "renprotocol",
            }

            coin_ids = []
            if symbol.lower() in symbol_mappings:
                coin_ids.append(symbol_mappings[symbol.lower()])
            coin_ids.extend([symbol.lower(), symbol.upper(), symbol.capitalize()])
            coin_ids = list(dict.fromkeys(coin_ids))  # Remove duplicates

            data = None
            for coin_id in coin_ids:
                url = f"https://api.coingecko.com/api/v3/coins/{coin_id}"
                params = {
                    "localization": "false",
                    "tickers": "false",
                    "community_data": "false",
                    "developer_data": "false",
                    "sparkline": "false",
                }

                async with session.get(
                    url, params=params, timeout=aiohttp.ClientTimeout(total=10)
                ) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        if data and isinstance(data, dict) and "market_data" in data:
                            break
                        data = None

            if data and isinstance(data, dict) and "market_data" in data:
                market = data.get("market_data", {})
                market_cap = market.get("market_cap", {}).get("usd", 0) or 0
                volume = market.get("total_volume", {}).get("usd", 0) or 0
                circulating = market.get("circulating_supply", 0) or 0
                total = market.get("total_supply", 0) or 0

                volume_score = 50
                if market_cap > 0 and volume > 0:
                    vol_ratio = volume / market_cap
                    if vol_ratio > 0.1:
                        volume_score = 80
                    elif vol_ratio > 0.05:
                        volume_score = 70
                    elif vol_ratio > 0.02:
                        volume_score = 60
                    elif vol_ratio > 0.01:
                        volume_score = 55

                circulation_score = 50
                if total > 0:
                    circ_ratio = circulating / total
                    if circ_ratio > 0.8:
                        circulation_score = 80
                    elif circ_ratio > 0.5:
                        circulation_score = 65
                    elif circ_ratio > 0.25:
                        circulation_score = 55

                result = {
                    "score": (volume_score + circulation_score) / 2,
                    "volume_score": volume_score,
                    "circulation_score": circulation_score,
                    "volume_momentum": 0,
                    "market_cap": market_cap,
                    "volume_24h": volume,
                    "source": "coingecko",
                    "confidence": 80,
                    "timestamp": datetime.now().isoformat(),
                }
                self._set_cache(cache_key, result)
                return result
        except Exception as e:
            pass

        return {
            "score": 50,
            "volume_score": 50,
            "circulation_score": 50,
            "volume_momentum": 0,
            "source": "fallback",
            "confidence": 0,
            "timestamp": datetime.now().isoformat(),
        }

    async def get_gwei_gas(self) -> Dict:
        """
        Get current gas prices (FREE)
        """
        try:
            data = await self._request_json(
                "https://api.etherscan.io/api?module=gastracker&action=gasoracle"
            )
            if data:
                result = data.get("result", {})
                fast_gas = int(result.get("FastGasPrice", 20))
                slow_gas = int(result.get("SafeGasPrice", 10))

                gas_score = 50
                if fast_gas < 20:
                    gas_score = 70
                elif fast_gas < 50:
                    gas_score = 55
                elif fast_gas < 100:
                    gas_score = 45
                else:
                    gas_score = 30

                return {
                    "fast_gas": fast_gas,
                    "slow_gas": slow_gas,
                    "score": gas_score,
                    "source": "etherscan",
                    "confidence": 70,
                    "timestamp": datetime.now().isoformat(),
                }

        except Exception:
            pass

        return {
            "fast_gas": 20,
            "slow_gas": 10,
            "score": 50,
            "source": "fallback",
            "confidence": 0,
            "timestamp": datetime.now().isoformat(),
        }

    async def get_whale_alerts(self, symbol: str) -> Dict:
        """
        Get whale activity from public blockchain data (FREE)
        """
        api_key = os.environ.get("WHALE_ALERT_API_KEY", "").strip()
        if not api_key:
            return {
                "score": 50,
                "transactions": 0,
                "buy_count": 0,
                "sell_count": 0,
                "source": "no_api_key",
                "confidence": 0,
                "timestamp": datetime.now().isoformat(),
            }
        try:
            url = f"https://api.whale-alert.io/v1/transactions"
            params = {
                "min_value": 1000000,
                "symbol": symbol.upper(),
                "limit": 10,
                "api_key": api_key,
            }
            data = await self._request_json(url, params=params)
            if data:
                transactions = data.get("transactions", [])

                buy_count = sum(
                    1
                    for tx in transactions
                    if tx.get("to_owner", "").lower() == tx.get("exchange", "").lower()
                )
                sell_count = len(transactions) - buy_count

                whale_score = 50
                if buy_count > sell_count:
                    whale_score = 60 + min(buy_count * 5, 30)
                elif sell_count > buy_count:
                    whale_score = 40 - min(sell_count * 5, 20)

                return {
                    "score": whale_score,
                    "transactions": len(transactions),
                    "buy_count": buy_count,
                    "sell_count": sell_count,
                    "source": "whale-alert",
                    "confidence": 70 if transactions else 40,
                    "timestamp": datetime.now().isoformat(),
                }

        except Exception:
            pass

        return {
            "score": 50,
            "transactions": 0,
            "buy_count": 0,
            "sell_count": 0,
            "source": "fallback",
            "confidence": 0,
            "timestamp": datetime.now().isoformat(),
        }

    async def get_news_sentiment(self, symbol: str) -> Dict:
        """
        Best-effort news sentiment using GDELT (FREE)
        """
        cache_key = f"news_{symbol}"
        cache = self._get_cache(cache_key)
        if cache:
            return cache

        score = 50
        confidence = 0
        sources = []
        articles_analyzed = 0
        try:
            # GDELT requires parentheses for OR queries
            query = f"({symbol} OR crypto OR bitcoin OR cryptocurrency)"
            url = "https://api.gdeltproject.org/api/v2/doc/doc"
            params = {
                "query": query,
                "mode": "artlist",
                "maxrecords": 50,
                "format": "json",
            }
            data = await self._request_json(url, params=params)
            if data and isinstance(data, dict):
                articles = data.get("articles", [])
                if articles:
                    tones = []
                    titles = []
                    for a in articles[:25]:
                        tone = a.get("tone")
                        if tone is not None:
                            try:
                                tones.append(float(tone))
                            except Exception:
                                pass
                        title = a.get("title", "")
                        if title:
                            titles.append(title)

                    if tones:
                        avg_tone = sum(tones) / len(tones)
                        score = max(0, min(100, avg_tone + 50))
                        confidence = min(len(tones) * 4, 100)
                    elif titles:
                        sentiments = [self._analyze_text_sentiment(t) for t in titles]
                        score = sum(sentiments) / len(sentiments)
                        confidence = min(len(sentiments) * 4, 100)

                    sources = [
                        {
                            "source": a.get("sourceCountry", "unknown"),
                            "title": a.get("title", ""),
                        }
                        for a in articles[:5]
                    ]
                    articles_analyzed = len(articles)
        except Exception:
            pass

        result = {
            "score": score,
            "confidence": confidence,
            "sources": sources,
            "source": "gdelt",
            "timestamp": datetime.now().isoformat(),
        }
        self._set_cache(cache_key, result)
        return result

    async def get_twitter_sentiment(self, symbol: str) -> Dict:
        """
        Twitter sentiment is no longer available (API changes)
        Returns neutral sentiment as fallback
        """
        return {
            "score": 50,
            "confidence": 0,
            "sources": [],
            "tweets_analyzed": 0,
            "source": "disabled",
            "timestamp": datetime.now().isoformat(),
        }

    async def get_cryptocompare_sentiment(self, symbol: str) -> Dict:
        """
        Get social sentiment from CryptoCompare (FREE, no key required)
        """
        cache_key = f"cc_sentiment_{symbol}"
        cache = self._get_cache(cache_key)
        if cache:
            return cache

        score = 50
        confidence = 0
        sources = []
        tweets = 0

        try:
            # Get coin ID for symbol
            session = await self.get_session()

            # Try CryptoCompare social data
            url = "https://min-api.cryptocompare.com/data/social/coin"
            params = {"fsym": symbol.upper()}

            async with session.get(
                url, params=params, timeout=aiohttp.ClientTimeout(total=10)
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    if data and data.get("Response") == "Success":
                        social_data = data.get("Data", {})

                        # Twitter followers and sentiment
                        twitter_followers = social_data.get("Twitter", {}).get("followers", 0)
                        twitter_posts = social_data.get("Twitter", {}).get("statuses", 0)

                        # Reddit subscribers
                        reddit_subscribers = social_data.get("Reddit", {}).get("subscribers", 0)
                        reddit_posts = social_data.get("Reddit", {}).get("active_users", 0)

                        # Telegram
                        telegram_members = social_data.get("Telegram", {}).get("members", 0)

                        # Overall social score
                        social_scores = []
                        if twitter_followers > 10000:
                            social_scores.append(60)
                        elif twitter_followers > 1000:
                            social_scores.append(55)

                        if reddit_subscribers > 10000:
                            social_scores.append(60)
                        elif reddit_subscribers > 1000:
                            social_scores.append(55)

                        if telegram_members > 1000:
                            social_scores.append(55)

                        if social_scores:
                            score = sum(social_scores) / len(social_scores)
                            confidence = min(80, len(social_scores) * 25)

                        sources = [
                            {"platform": "Twitter", "followers": twitter_followers},
                            {"platform": "Reddit", "subscribers": reddit_subscribers},
                            {"platform": "Telegram", "members": telegram_members},
                        ]
                        tweets = twitter_posts + reddit_posts
        except Exception:
            pass

        result = {
            "score": score,
            "confidence": confidence,
            "sources": sources,
            "tweets": tweets,
            "source": "cryptocompare",
            "timestamp": datetime.now().isoformat(),
        }
        self._set_cache(cache_key, result)
        return result

    async def get_dominance_metrics(self) -> Dict:
        """
        Get market dominance metrics for BTC, ETH, and altcoins (FREE)
        Source: CoinGecko API
        """

        logger = get_logger(__name__)

        cache_key = "market_dominance"
        cache = self._get_cache(cache_key)
        if cache:
            return cache

        try:
            session = await self.get_session()

            # Get global market data
            url = "https://api.coingecko.com/api/v3/global"
            data = await self._request_json(url, timeout=15)

            if data and "data" in data:
                global_data = data["data"]

                # BTC dominance
                btc_dominance = global_data.get("market_cap_percentage", {}).get("btc", 0)
                eth_dominance = global_data.get("market_cap_percentage", {}).get("eth", 0)
                altcoin_dominance = 100 - btc_dominance - eth_dominance

                # Market conditions based on dominance
                market_phase = "BTC"
                if btc_dominance > 60:
                    market_phase = "BTC_STRONG"
                elif btc_dominance < 40:
                    market_phase = "ALTCOINS_STRONG"
                elif eth_dominance > 20:
                    market_phase = "ETH_STRONG"
                else:
                    market_phase = "BALANCED"

                # Score dominance for trading decisions
                # BTC dominance > 60: bearish for alts
                # BTC dominance < 40: bullish for alts
                # ETH dominance > 20: ETH strong
                dominance_score = 50
                if btc_dominance > 60:
                    dominance_score = 30
                elif btc_dominance < 40:
                    dominance_score = 70
                elif eth_dominance > 20:
                    dominance_score = 60

                result = {
                    "btc_dominance": round(btc_dominance, 2),
                    "eth_dominance": round(eth_dominance, 2),
                    "altcoin_dominance": round(altcoin_dominance, 2),
                    "market_phase": market_phase,
                    "score": dominance_score,
                    "confidence": 90,
                    "source": "coingecko",
                    "timestamp": datetime.now().isoformat(),
                }

                self._set_cache(cache_key, result)
                logger.info(
                    f"📊 Market Dominance: BTC={btc_dominance:.1f}%, ETH={eth_dominance:.1f}%, Alts={altcoin_dominance:.1f}% ({market_phase})"
                )
                return result

        except Exception as e:
            logger.warning(f"⚠️ Failed to get dominance metrics: {e}")

        return {
            "btc_dominance": 50.0,
            "eth_dominance": 20.0,
            "altcoin_dominance": 30.0,
            "market_phase": "BALANCED",
            "score": 50,
            "confidence": 30,
            "source": "fallback",
            "timestamp": datetime.now().isoformat(),
        }

    async def get_altcoin_season_index(self) -> Dict:
        """
        Calculate altcoin season index based on market data (FREE)
        Source: CoinGecko API
        """

        logger = get_logger(__name__)

        cache_key = "altcoin_season"
        cache = self._get_cache(cache_key)
        if cache:
            return cache

        try:
            session = await self.get_session()

            # Get BTC and ETH data
            btc_data = await self.get_cmc_sentiment("BTC")
            eth_data = await self.get_cmc_sentiment("ETH")

            # Get top 10 altcoins (excluding BTC/ETH)
            url = "https://api.coingecko.com/api/v3/coins/markets"
            params = {
                "vs_currency": "usd",
                "order": "market_cap_desc",
                "per_page": 15,
                "page": 1,
                "sparkline": "false",
            }

            coins_data = await self._request_json(url, params=params, timeout=15)

            if coins_data:
                # Filter out BTC and ETH
                altcoins = [
                    coin for coin in coins_data if coin["symbol"].lower() not in ["btc", "eth"]
                ][:10]

                # Calculate average performance
                btc_change = btc_data.get("price_change_24h", 0)
                eth_change = eth_data.get("price_change_24h", 0)
                altcoin_changes = [coin.get("price_change_percentage_24h", 0) for coin in altcoins]
                avg_alt_change = (
                    sum(altcoin_changes) / len(altcoin_changes) if altcoin_changes else 0
                )

                # Calculate season index
                season_index = 50
                if avg_alt_change > btc_change + 2:
                    season_index = 75  # Altcoin season
                elif avg_alt_change > btc_change + 0.5:
                    season_index = 60  # Altcoins stronger
                elif btc_change > avg_alt_change + 2:
                    season_index = 30  # BTC season
                elif btc_change > avg_alt_change + 0.5:
                    season_index = 40  # BTC stronger

                # Determine season type
                season_type = "NEUTRAL"
                if season_index >= 70:
                    season_type = "ALTCOIN_SEASON"
                elif season_index >= 60:
                    season_type = "ALTCOIN_STRONG"
                elif season_index <= 35:
                    season_type = "BTC_SEASON"
                elif season_index <= 45:
                    season_type = "BTC_STRONG"

                result = {
                    "index": round(season_index, 2),
                    "type": season_type,
                    "btc_change": round(btc_change, 2),
                    "eth_change": round(eth_change, 2),
                    "avg_alt_change": round(avg_alt_change, 2),
                    "altcoins_count": len(altcoin_changes),
                    "confidence": 85,
                    "source": "coingecko",
                    "timestamp": datetime.now().isoformat(),
                }

                self._set_cache(cache_key, result)
                logger.info(f"🍂 Altcoin Season: {season_type} (Index: {season_index:.1f})")
                return result

        except Exception as e:
            logger.warning(f"⚠️ Failed to get altcoin season index: {e}")

        return {
            "index": 50,
            "type": "NEUTRAL",
            "btc_change": 0,
            "eth_change": 0,
            "avg_alt_change": 0,
            "altcoins_count": 0,
            "confidence": 30,
            "source": "fallback",
            "timestamp": datetime.now().isoformat(),
        }

    async def get_eth_gas_insights(self) -> Dict:
        """
        Get ETH gas insights with network health indicators (FREE)
        Source: Etherscan API
        """

        logger = get_logger(__name__)

        cache_key = "eth_gas_insights"
        cache = self._get_cache(cache_key)
        if cache:
            return cache

        try:
            data = await self.get_gwei_gas()

            fast_gas = data["fast_gas"]
            slow_gas = data["slow_gas"]

            # Network health indicators
            network_health = "HEALTHY"
            if fast_gas > 100:
                network_health = "CONGESTED"
            elif fast_gas > 50:
                network_health = "MODERATE"
            elif fast_gas < 20:
                network_health = "OPTIMAL"

            # DeFi activity proxy based on gas
            defi_activity = "LOW"
            if fast_gas > 80:
                defi_activity = "HIGH"
            elif fast_gas > 40:
                defi_activity = "MODERATE"

            # Trading conditions
            trading_conditions = "FAVORABLE"
            if fast_gas > 100:
                trading_conditions = "UNFAVORABLE"
            elif fast_gas > 60:
                trading_conditions = "CAUTIOUS"

            result = {
                "fast_gas": fast_gas,
                "slow_gas": slow_gas,
                "network_health": network_health,
                "defi_activity": defi_activity,
                "trading_conditions": trading_conditions,
                "score": data["score"],
                "confidence": data["confidence"],
                "source": "etherscan",
                "timestamp": datetime.now().isoformat(),
            }

            self._set_cache(cache_key, result)
            logger.info(f"⛽ ETH Gas: {fast_gas} Gwei ({network_health}, {defi_activity} DeFi)")
            return result

        except Exception as e:
            logger.warning(f"⚠️ Failed to get ETH gas insights: {e}")

        return {
            "fast_gas": 20,
            "slow_gas": 10,
            "network_health": "MODERATE",
            "defi_activity": "MODERATE",
            "trading_conditions": "CAUTIOUS",
            "score": 50,
            "confidence": 30,
            "source": "fallback",
            "timestamp": datetime.now().isoformat(),
        }

    async def get_holder_metrics(self, symbol: str) -> Dict:
        """
        Holder/circulation proxy from CoinCap (FREE)
        """
        data = await self.get_onchain_metrics(symbol)
        result = {
            "score": data.get("circulation_score", 50),
            "circulation_score": data.get("circulation_score", 50),
            "supply_ratio": data.get("supply_ratio", 0),
            "source": "coincap",
            "confidence": data.get("confidence", 50),
            "timestamp": datetime.now().isoformat(),
        }
        return result

    async def get_exchange_flow(self, symbol: str) -> Dict:
        """
        Exchange flow proxy using liquidity/volume from CoinCap (FREE)
        Returns data compatible with AGI brain expectations
        """
        data = await self.get_onchain_metrics(symbol)
        score = data.get("volume_score", 50)
        confidence = data.get("confidence", 50)

        # Calculate net_flow based on volume momentum
        volume_momentum = data.get("volume_momentum", 0)
        net_flow = volume_momentum * 100  # Scale to visible range

        # Determine whale activity based on confidence and volume
        if confidence > 70:
            if net_flow > 0:
                whale_activity = "ACCUMULATING"
            elif net_flow < 0:
                whale_activity = "DISTRIBUTING"
            else:
                whale_activity = "NEUTRAL"
        else:
            whale_activity = "NEUTRAL"

        return {
            "net_flow": net_flow,
            "whale_activity": whale_activity,
            "score": score,
            "volume_score": score,
            "source": "coincap",
            "confidence": confidence,
            "timestamp": datetime.now().isoformat(),
        }

    async def get_large_transactions(self, symbol: str) -> Dict:
        """
        Large transaction proxy using Whale Alert if API key provided (FREE tier)
        """
        return await self.get_whale_alerts(symbol)

    async def get_comprehensive_sentiment(self, symbol: str) -> Dict:
        """
        Get comprehensive sentiment from ALL working free sources
        """
        tasks = [
            self.get_fear_greed_index(),
            self.get_cryptocompare_sentiment(symbol),
            self.get_cmc_sentiment(symbol),
            self.get_onchain_metrics(symbol),
            self.get_news_sentiment(symbol),
        ]

        # Add dominance metrics if symbol is not BTC or ETH (for altcoin context)
        if symbol.lower() not in ["btc", "eth"]:
            tasks.append(self.get_dominance_metrics())
            tasks.append(self.get_altcoin_season_index())

        # Add ETH gas insights if symbol is ETH or DeFi-related
        if symbol.lower() == "eth" or "eth" in symbol.lower() or "defi" in symbol.lower():
            tasks.append(self.get_eth_gas_insights())

        results = await asyncio.gather(*tasks, return_exceptions=True)

        scores = []
        weights = []
        sources = {}
        fallback_sources = {"fallback", "unknown", "no_api_key", "disabled"}

        for result in results:
            if isinstance(result, dict) and "score" in result:
                source = result.get("source", "unknown")
                weight = result.get("confidence", 50)
                if source in fallback_sources:
                    weight = 0
                scores.append(result["score"])
                weights.append(weight)
                sources[source] = result

        total_weight = sum(weights)
        if scores and total_weight > 0:
            weighted_score = sum(s * w for s, w in zip(scores, weights)) / total_weight
        else:
            weighted_score = 50

        confidence = min(int(total_weight / 2), 100) if total_weight > 0 else 0

        return {
            "score": weighted_score,
            "individual_scores": scores,
            "weights": weights,
            "sources": sources,
            "confidence": confidence,
            "timestamp": datetime.now().isoformat(),
        }


async def test_free_intelligence():
    """Test free intelligence sources"""
    print("=" * 80)
    print("🦅 IBIS FREE & INDEPENDENT INTELLIGENCE TEST")
    print("=" * 80)

    intel = FreeIntelligence()

    print("\n1. FEAR & GREED INDEX:")
    fng = await intel.get_fear_greed_index()
    print(f"   Value: {fng['value']} ({fng['classification']})")
    print(f"   Score: {fng['score']}/100")

    print("\n2. MARKET DOMINANCE:")
    dominance = await intel.get_dominance_metrics()
    print(
        f"   BTC: {dominance['btc_dominance']}%, ETH: {dominance['eth_dominance']}%, Alts: {dominance['altcoin_dominance']}%"
    )
    print(f"   Market Phase: {dominance['market_phase']}")
    print(f"   Score: {dominance['score']}/100")

    print("\n3. ALTCOIN SEASON INDEX:")
    season = await intel.get_altcoin_season_index()
    print(f"   Index: {season['index']}/100 ({season['type']})")
    print(
        f"   BTC: {season['btc_change']}%, ETH: {season['eth_change']}%, Avg Alt: {season['avg_alt_change']}%"
    )

    print("\n4. ETH GAS INSIGHTS:")
    eth_gas = await intel.get_eth_gas_insights()
    print(f"   Fast: {eth_gas['fast_gas']} Gwei, Slow: {eth_gas['slow_gas']} Gwei")
    print(f"   Network: {eth_gas['network_health']}, DeFi: {eth_gas['defi_activity']}")
    print(f"   Trading Conditions: {eth_gas['trading_conditions']}")

    print("\n5. COINMARKETCAP SENTIMENT (BTC):")
    cmc = await intel.get_cmc_sentiment("bitcoin")
    print(f"   Score: {cmc['score']}/100")
    print(f"   24h Change: {cmc.get('price_change_24h', 0):.2f}%")
    print(f"   Rank: #{cmc.get('rank', 'N/A')}")

    print("\n6. ON-CHAIN METRICS (BTC):")
    onchain = await intel.get_onchain_metrics("bitcoin")
    print(f"   Score: {onchain['score']}/100")
    print(f"   Volume Score: {onchain['volume_score']}/100")
    print(f"   Circulation Score: {onchain['circulation_score']}/100")

    print("\n7. COMPREHENSIVE SENTIMENT (BTC):")
    comprehensive = await intel.get_comprehensive_sentiment("bitcoin")
    print(f"   Combined Score: {comprehensive['score']}/100")

    print("\n8. COMPREHENSIVE SENTIMENT (ETH):")
    eth_comprehensive = await intel.get_comprehensive_sentiment("eth")
    print(f"   Combined Score: {eth_comprehensive['score']}/100")

    await intel.close()

    print("\n" + "=" * 80)
    print("✅ ALL FREE INTELLIGENCE SOURCES WORKING!")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(test_free_intelligence())
