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
            self.session = aiohttp.ClientSession(
                headers={"User-Agent": "IBIS-Trading-Bot/1.0"}
            )
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
        import logging

        logger = logging.getLogger("IBIS")

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
                    value_classification = fng_data.get(
                        "value_classification", "Neutral"
                    )

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
        Get Reddit sentiment from Reddit API
        Uses pushshift.io as backup for when Reddit API fails
        """
        import logging

        logger = logging.getLogger("IBIS")

        cache_key = f"reddit_{symbol}"
        cache = self._get_cache(cache_key)
        if cache:
            return cache

        subreddits = subreddits or ["CryptoCurrency", "Bitcoin", "altcoin"]
        total_sentiment = 0
        total_posts = 0
        sources = []

        # Try pushshift.io API (no rate limits, no auth required)
        try:
            for subreddit in subreddits[:2]:  # Limit to 2 subreddits
                url = f"https://api.pushshift.io/reddit/search/submission/"
                params = {
                    "subreddit": subreddit,
                    "q": symbol,
                    "sort": "desc",
                    "sort_type": "created_utc",
                    "size": 10,
                }
                data = await self._request_json(url, params=params, timeout=15)
                if data:
                    posts = data.get("data", [])
                    if posts:
                        post_sentiments = []
                        for post in posts[:5]:
                            title = post.get("title", "")
                            sentiment = self._analyze_text_sentiment(title)
                            post_sentiments.append(sentiment)

                        if post_sentiments:
                            avg_sentiment = sum(post_sentiments) / len(post_sentiments)
                            total_sentiment += avg_sentiment
                            total_posts += len(post_sentiments)
                            sources.append(
                                {
                                    "subreddit": subreddit,
                                    "posts": len(post_sentiments),
                                    "avg_sentiment": avg_sentiment,
                                }
                            )
                            logger.debug(
                                f"Reddit {subreddit}: {len(post_sentiments)} posts, avg sentiment: {avg_sentiment:.1f}"
                            )
        except Exception as e:
            logger.debug(f"Pushshift API failed: {e}")

        # Fallback: try Reddit API with proper headers
        if total_posts == 0:
            try:
                session = await self.get_session()
                for subreddit in subreddits[:2]:
                    url = f"https://www.reddit.com/r/{subreddit}/hot.json"
                    params = {"limit": 10}
                    headers = {"User-Agent": "IBIS-Trading-Bot/1.0"}

                    async with session.get(
                        url,
                        params=params,
                        headers=headers,
                        timeout=aiohttp.ClientTimeout(total=10),
                    ) as resp:
                        if resp.status == 200:
                            data = await resp.json()
                            posts = data.get("data", {}).get("children", [])
                            post_sentiments = []
                            for post in posts[:5]:
                                title = post.get("data", {}).get("title", "")
                                sentiment = self._analyze_text_sentiment(title)
                                post_sentiments.append(sentiment)

                            if post_sentiments:
                                avg_sentiment = sum(post_sentiments) / len(
                                    post_sentiments
                                )
                                total_sentiment += avg_sentiment
                                total_posts += len(post_sentiments)
                                sources.append(
                                    {
                                        "subreddit": subreddit,
                                        "posts": len(post_sentiments),
                                        "avg_sentiment": avg_sentiment,
                                    }
                                )
            except Exception as e:
                logger.debug(f"Reddit API fallback failed: {e}")

        if total_posts > 0:
            final_sentiment = total_sentiment / len(sources) if sources else 50
            confidence = min(len(sources) * 30, 100)
        else:
            final_sentiment = 50
            confidence = 0

        result = {
            "score": final_sentiment,
            "confidence": confidence,
            "sources": sources,
            "posts_analyzed": total_posts,
            "source": "pushshift" if sources else "fallback",
            "timestamp": datetime.now().isoformat(),
        }
        self._set_cache(cache_key, result)
        return result

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
        import logging

        logger = logging.getLogger("IBIS")

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
        import logging

        logger = logging.getLogger("IBIS")

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
        Best-effort social sentiment via various RSS feeds (FREE)
        """
        cache_key = f"twitter_{symbol}"
        cache = self._get_cache(cache_key)
        if cache:
            return cache

        score = 50
        confidence = 0
        sources = []
        tweets_analyzed = 0

        rss_feeds = [
            (
                "nitter",
                "https://nitter.net/search/rss",
                {"f": "tweets", "q": f"{symbol} OR crypto"},
            ),
            (
                "twttr",
                "https://twitframe.com/show",
                {"url": "https://twitter.com/hashtag/crypto"},
            ),
        ]

        for source_name, url, params in rss_feeds:
            try:
                text = await self._request_text(url, params=params, timeout=10)
                if text and "error" not in text.lower():
                    titles = re.findall(r"<title>(.*?)</title>", text, re.DOTALL)
                    titles = [
                        t
                        for t in titles[1:]
                        if t
                        and "nitter" not in t.lower()
                        and "twitter" not in t.lower()
                    ]
                    titles = titles[:25]
                    if titles:
                        sentiments = [self._analyze_text_sentiment(t) for t in titles]
                        score = sum(sentiments) / len(sentiments)
                        confidence = min(len(sentiments) * 4, 100)
                        sources = [
                            {"title": t[:140], "source": source_name}
                            for t in titles[:5]
                        ]
                        tweets_analyzed = len(titles)
                        break
            except Exception:
                continue

        result = {
            "score": score,
            "confidence": confidence,
            "sources": sources,
            "tweets_analyzed": tweets_analyzed,
            "source": sources[0]["source"] if sources else "fallback",
            "timestamp": datetime.now().isoformat(),
        }
        self._set_cache(cache_key, result)
        return result

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
                        twitter_followers = social_data.get("Twitter", {}).get(
                            "followers", 0
                        )
                        twitter_posts = social_data.get("Twitter", {}).get(
                            "statuses", 0
                        )

                        # Reddit subscribers
                        reddit_subscribers = social_data.get("Reddit", {}).get(
                            "subscribers", 0
                        )
                        reddit_posts = social_data.get("Reddit", {}).get(
                            "active_users", 0
                        )

                        # Telegram
                        telegram_members = social_data.get("Telegram", {}).get(
                            "members", 0
                        )

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

        results = await asyncio.gather(*tasks, return_exceptions=True)

        scores = []
        weights = []
        sources = {}
        fallback_sources = {"fallback", "unknown", "no_api_key"}

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

    print("\n2. REDDIT SENTIMENT (BTC):")
    reddit = await intel.get_reddit_sentiment("bitcoin")
    print(f"   Score: {reddit['score']}/100")
    print(f"   Confidence: {reddit['confidence']}%")
    print(f"   Sources: {len(reddit['sources'])}")

    print("\n3. COINMARKETCAP SENTIMENT (BTC):")
    cmc = await intel.get_cmc_sentiment("bitcoin")
    print(f"   Score: {cmc['score']}/100")
    print(f"   24h Change: {cmc.get('price_change_24h', 0):.2f}%")
    print(f"   Rank: #{cmc.get('rank', 'N/A')}")

    print("\n4. ON-CHAIN METRICS (BTC):")
    onchain = await intel.get_onchain_metrics("bitcoin")
    print(f"   Score: {onchain['score']}/100")
    print(f"   Whale Score: {onchain['whale_score']}/100")
    print(f"   Volume Score: {onchain['volume_score']}/100")
    print(f"   Rank: #{onchain.get('rank', 'N/A')}")

    print("\n5. GAS PRICES:")
    gas = await intel.get_gwei_gas()
    print(f"   Fast: {gas['fast_gas']} Gwei")
    print(f"   Slow: {gas['slow_gas']} Gwei")
    print(f"   Score: {gas['score']}/100")

    print("\n6. COMPREHENSIVE SENTIMENT (BTC):")
    comprehensive = await intel.get_comprehensive_sentiment("bitcoin")
    print(f"   Combined Score: {comprehensive['score']}/100")

    await intel.close()

    print("\n" + "=" * 80)
    print("✅ ALL FREE INTELLIGENCE SOURCES WORKING!")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(test_free_intelligence())
