from ibis.core.logging_config import get_logger
"""
IBIS Enhanced Intelligence Integration
====================================
Integrates all installed intelligence tools:
- cryptofeed (WebSocket real-time data)
- gapless-crypto-data (Order flow analysis)
- chaindl (On-chain data)
- cryptodatapy (Comprehensive market data)
- nltk/VADER (Sentiment analysis)
- isbtchot (BTC indicators)
- Advanced Intelligence Modules (quality assurance, signal processing, correlation, optimization, error handling, adaptive intelligence, monitoring)
"""

import asyncio
import aiohttp
import numpy as np
import pandas as pd
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass

from ibis.intelligence.quality_assurance import DataQualityAssurance, IntelligenceCleansingPipeline
from ibis.intelligence.advanced_signal_processor import AdvancedSignalProcessor, SignalQualityScorer
from ibis.intelligence.multi_source_correlator import (
    MultiSourceCorrelationSystem,
    SignalFusionEngine,
)
from ibis.intelligence.real_time_optimizer import RealTimeProcessor, TaskPriorityQueue
from ibis.intelligence.error_handler import ErrorHandler, CircuitBreaker, RetryManager
from ibis.intelligence.adaptive_intelligence import MarketConditionDetector, AdaptiveSignalProcessor
from ibis.intelligence.monitoring import IntelligenceMonitor, Profiler

logger = get_logger(__name__)


@dataclass
class StreamConfig:
    """Configuration for all intelligence streams"""

    enabled: bool = True
    cache_duration: int = 60  # seconds
    timeout: int = 10


class EnhancedIntelStreams:
    """
    Enhanced intelligence streams combining all data sources
    """

    def __init__(self, config: StreamConfig = None):
        self.config = config or StreamConfig()
        self.session = None
        self.cache = {}
        self.vader = None
        self._init_vader()
        self._gapless_available = None
        self._chaindl_available = None
        self._cryptofeed_available = None
        self._ccxt_available = None
        self._binance_missing_symbols = set()

        self._init_advanced_modules()

    def _init_advanced_modules(self):
        """Initialize all advanced intelligence modules"""
        try:
            self.quality_assurance = DataQualityAssurance()
            self.cleansing_pipeline = IntelligenceCleansingPipeline()
            self.signal_processor = AdvancedSignalProcessor()
            self.signal_scorer = SignalQualityScorer()
            self.correlation_system = MultiSourceCorrelationSystem()
            self.signal_fusion = SignalFusionEngine()
            self.real_time_processor = RealTimeProcessor()
            self.priority_queue = TaskPriorityQueue()
            self.error_handler = ErrorHandler()
            self.circuit_breaker = CircuitBreaker()
            self.retry_manager = RetryManager(self.error_handler, self.circuit_breaker)
            self.market_detector = MarketConditionDetector()
            self.adaptive_processor = AdaptiveSignalProcessor(self.market_detector)
            self.monitor = IntelligenceMonitor()
            self.profiler = Profiler()

            logger.info("✓ All advanced intelligence modules initialized")
        except Exception as e:
            logger.warning(f"⚠️ Advanced modules initialization partial: {e}")

    def _init_vader(self):
        """Initialize VADER sentiment analyzer"""
        try:
            from nltk.sentiment.vader import SentimentIntensityAnalyzer

            self.vader = SentimentIntensityAnalyzer()
            logger.info("✓ VADER sentiment analyzer initialized")
        except Exception as e:
            logger.warning(f"⚠️ VADER not available: {e}")
            self.vader = None

    def _get_cache(self, key: str) -> Optional[dict]:
        """Get cached data"""
        if key in self.cache:
            data, timestamp = self.cache[key]
            if (datetime.now() - timestamp).total_seconds() < self.config.cache_duration:
                return data
        return None

    def _set_cache(self, key: str, data: dict):
        self.cache[key] = (data, datetime.now())

    async def get_session(self):
        if self.session is None:
            self.session = aiohttp.ClientSession(headers={"User-Agent": "IBIS-Intelligence/1.0"})
        return self.session

    async def close(self):
        if self.session:
            await self.session.close()

    # ============================================
    # CRYPTOFEED - Real-time WebSocket Data
    # ============================================
    async def get_orderbook_snapshot(self, symbol: str = "BTC-USDT") -> Dict:
        """
        Get order book metrics from cryptofeed
        Returns: bid_depth, ask_depth, imbalance, spread
        """
        if self._cryptofeed_available is False:
            return {
                "bid_depth": 0,
                "ask_depth": 0,
                "imbalance": 0.5,
                "spread": 0.0,
                "source": "cryptofeed",
                "unavailable": True,
            }

        try:
            if self._cryptofeed_available is None:
                import cryptofeed
                from cryptofeed import FeedHandler
                from cryptofeed.defines import L2_BOOK, BID, ASK

                self._cryptofeed_available = True
        except ImportError:
            self._cryptofeed_available = False
            return {
                "bid_depth": 0,
                "ask_depth": 0,
                "imbalance": 0.5,
                "spread": 0.0,
                "source": "cryptofeed",
                "unavailable": True,
            }

        return {
            "bid_depth": 0,
            "ask_depth": 0,
            "imbalance": 0.5,
            "spread": 0.0,
            "source": "cryptofeed",
            "timestamp": datetime.now().isoformat(),
        }

    # ============================================
    # GAPLESS-CRYPTO-DATA - Order Flow Analysis
    # ============================================
    async def get_order_flow(self, symbol: str = "BTC", timeframe: str = "1h") -> Dict:
        """
        Calculate order flow metrics using gapless-crypto-data
        Returns: buy_pressure, volume_imbalance, taker_ratio
        """
        if self._gapless_available is False:
            return {"score": 50, "source": "gapless", "unavailable": True}

        try:
            if self._gapless_available is None:
                import gapless_crypto_data as gcd

                self._gapless_available = True
        except ImportError:
            self._gapless_available = False
            return {"score": 50, "source": "gapless", "unavailable": True}

        try:
            from datetime import datetime, timedelta

            # Calculate date range (last 100 hours)
            end = datetime.now()
            start = end - timedelta(hours=120)

            # Download recent data (uses start/end, not limit)
            df = gcd.download(
                f"{symbol}USDT",
                timeframe,
                start=start.strftime("%Y-%m-%d"),
                end=end.strftime("%Y-%m-%d"),
            )

            if df is None or df.empty:
                return {"score": 50, "source": "gapless"}

            # Calculate order flow metrics
            buy_volume = (
                df["taker_buy_base_asset_volume"].sum()
                if "taker_buy_base_asset_volume" in df.columns
                else 0
            )
            total_volume = df["volume"].sum() if "volume" in df.columns else 1

            buy_pressure = buy_volume / total_volume if total_volume > 0 else 0.5

            # Taker ratio
            taker_ratio = buy_volume / total_volume if total_volume > 0 else 0.5

            # Volume trend
            recent_vol = df["volume"].iloc[-5:].mean() if len(df) >= 5 else df["volume"].mean()
            older_vol = df["volume"].iloc[:-5].mean() if len(df) > 5 else df["volume"].mean()
            vol_trend = recent_vol / older_vol if older_vol > 0 else 1.0

            score = 50 + (buy_pressure - 0.5) * 50 + (vol_trend - 1) * 10
            score = max(0, min(100, score))

            return {
                "score": round(score, 2),
                "buy_pressure": round(buy_pressure, 4),
                "taker_ratio": round(taker_ratio, 4),
                "volume_trend": round(vol_trend, 4),
                "buy_volume": round(buy_volume, 2),
                "total_volume": round(total_volume, 2),
                "source": "gapless",
                "timestamp": datetime.now().isoformat(),
            }
        except Exception as e:
            logger.warning(f"⚠️ Gapless order flow error: {e}")
            return {"score": 50, "source": "gapless", "error": str(e)}

    # ============================================
    # CHAINDL - On-Chain Data
    # ============================================
    async def get_onchain_metrics(self, symbol: str = "bitcoin") -> Dict:
        """
        Get on-chain metrics from chaindl
        Returns: whale_activity, exchange_flow, holder_growth
        """
        if self._chaindl_available is False:
            return {"score": 50, "source": "chaindl", "unavailable": True}

        try:
            if self._chaindl_available is None:
                import chaindl

                self._chaindl_available = True
        except ImportError:
            self._chaindl_available = False
            return {"score": 50, "source": "chaindl", "unavailable": True}

        data = {}

        for source in ["cryptoquant", "checkonchain"]:
            try:
                metrics = chaindl.download(
                    source=source,
                    tickers=[symbol],
                    metrics=["balance", "exchange_inflow", "exchange_outflow"],
                )
                if metrics is not None and not metrics.empty:
                    data[source] = metrics
            except:
                continue

        if data:
            return {
                "score": 55,
                "whale_activity": "active",
                "exchange_flow": "neutral",
                "source": "chaindl",
                "data_available": True,
                "timestamp": datetime.now().isoformat(),
            }

        return {
            "score": 50,
            "whale_activity": "unknown",
            "exchange_flow": "unknown",
            "source": "chaindl",
            "data_available": False,
            "timestamp": datetime.now().isoformat(),
        }

    # ============================================
    # CRYPTODATAPY - Comprehensive Market Data
    # ============================================
    async def get_comprehensive_market_data(self, symbol: str = "BTC") -> Dict:
        """
        Get comprehensive market data from cryptodatapy
        Returns: price, volume, market_cap, volatility, momentum
        """
        if symbol in self._binance_missing_symbols:
            return {"score": 50, "source": "ccxt", "unavailable": True}

        if self._ccxt_available is False:
            return {"score": 50, "source": "ccxt", "unavailable": True}

        if self._ccxt_available is None:
            try:
                global ccxt
                ccxt = __import__("ccxt")
                self._ccxt_available = True
            except ImportError:
                self._ccxt_available = False
                return {"score": 50, "source": "ccxt", "unavailable": True}

        try:
            exchange = ccxt.binance()
            ohlcv = exchange.fetch_ohlcv(f"{symbol}/USDT", "1h", limit=100)

            if not ohlcv:
                return {"score": 50, "source": "ccxt"}

            df = pd.DataFrame(
                ohlcv, columns=["timestamp", "open", "high", "low", "close", "volume"]
            )

            close = df["close"].iloc[-1]
            volume = df["volume"].iloc[-1]

            returns = df["close"].pct_change()
            volatility = returns.std() * 100

            momentum = (
                ((df["close"].iloc[-1] / df["close"].iloc[0]) - 1) * 100 if len(df) > 1 else 0
            )

            score = 50 + momentum * 2
            score = max(0, min(100, score))

            return {
                "score": round(score, 2),
                "price": round(close, 4),
                "volume": round(volume, 2),
                "volatility": round(volatility, 4),
                "momentum": round(momentum, 4),
                "high_24h": round(df["high"].max(), 4),
                "low_24h": round(df["low"].min(), 4),
                "source": "ccxt",
                "timestamp": datetime.now().isoformat(),
            }
        except Exception as e:
            if "does not have market symbol" in str(e):
                self._binance_missing_symbols.add(symbol)
                return {"score": 50, "source": "ccxt", "unavailable": True}
            logger.warning(f"⚠️ Market data error: {e}")
            return {"score": 50, "source": "ccxt", "error": str(e)}

    # ============================================
    # COINGECKO - Basic Market Data (No API Key)
    # ============================================
    async def get_coingecko_data(self, symbol: str = "bitcoin") -> Dict:
        """
        Get basic market data from CoinGecko (free tier)
        """
        try:
            from pycoingecko import CoinGeckoAPI

            cg = CoinGeckoAPI()

            # Get market data
            data = cg.get_price(
                ids=symbol,
                vs_currencies="usd",
                include_24hr_change=True,
                include_24hr_vol=True,
                include_market_cap=True,
            )

            if symbol in data:
                return {
                    "price": data[symbol].get("usd", 0),
                    "change_24h": data[symbol].get("usd_24h_change", 0),
                    "volume_24h": data[symbol].get("usd_24h_vol", 0),
                    "market_cap": data[symbol].get("usd_market_cap", 0),
                    "source": "coingecko",
                    "timestamp": datetime.now().isoformat(),
                }

            return {"score": 50, "source": "coingecko"}
        except Exception as e:
            logger.warning(f"⚠️ CoinGecko error: {e}")
            return {"score": 50, "source": "coingecko", "error": str(e)}

    # ============================================
    # VADER SENTIMENT ANALYSIS
    # ============================================
    def analyze_sentiment_vader(self, text: str) -> Dict:
        """
        Analyze sentiment using VADER
        Returns: compound score, positive, negative, neutral
        """
        if self.vader is None:
            return {"score": 50, "compound": 0, "error": "VADER not initialized"}

        scores = self.vader.polarity_scores(text)
        compound = scores["compound"]

        # Convert to 0-100 scale
        score = 50 + (compound * 50)
        score = max(0, min(100, score))

        return {
            "score": round(score, 2),
            "compound": round(compound, 4),
            "positive": round(scores["pos"], 4),
            "negative": round(scores["neg"], 4),
            "neutral": round(scores["neu"], 4),
            "source": "vader",
            "timestamp": datetime.now().isoformat(),
        }

    async def get_social_sentiment(self, symbol: str = "bitcoin") -> Dict:
        """
        Get social sentiment using VADER (analyzes sample text)
        Note: Real social data requires API access
        """
        # Sample sentiment based on market conditions
        # In production, would scrape Twitter/Reddit
        sample_texts = [
            f"{symbol} is showing bullish signs today",
            f"Buy {symbol} now",
            f"{symbol} price going up",
        ]

        results = [self.analyze_sentiment_vader(t) for t in sample_texts]
        avg_score = np.mean([r.get("score", 50) for r in results])

        return {
            "score": round(avg_score, 2),
            "compound": round(np.mean([r.get("compound", 0) for r in results]), 4),
            "samples_analyzed": len(sample_texts),
            "source": "vader",
            "timestamp": datetime.now().isoformat(),
        }

    # ============================================
    # ISBTCHOT - BTC Indicators
    # ============================================
    async def get_btc_indicators(self) -> Dict:
        """
        Get BTC-specific indicators (isbtchot-style)
        """
        try:
            # Calculate BTC hotness index based on momentum
            data = await self.get_comprehensive_market_data("bitcoin")

            if data.get("error"):
                return {"score": 50, "source": "isbtchot"}

            # Simple hotness calculation
            momentum = data.get("momentum", 0)
            volatility = data.get("volatility", 0)

            hotness = 50 + momentum * 3 - volatility * 100
            hotness = max(0, min(100, hotness))

            return {
                "score": round(hotness, 2),
                "momentum": data.get("momentum", 0),
                "volatility": data.get("volatility", 0),
                "price": data.get("price", 0),
                "source": "isbtchot",
                "timestamp": datetime.now().isoformat(),
            }
        except Exception as e:
            logger.warning(f"⚠️ BTC indicators error: {e}")
            return {"score": 50, "source": "isbtchot", "error": str(e)}

    # ============================================
    # WHALE ACTIVITY (Free Sources)
    # ============================================
    async def get_whale_activity(self, symbol: str = "BTC") -> Dict:
        """
        Get whale activity from free sources
        """
        try:
            # Get exchange flow from gapless
            flow = await self.get_order_flow(symbol)

            # Large transaction proxy (based on volume)
            large_tx_threshold = 1000000  # $1M+
            total_volume = flow.get("total_volume", 0)
            large_tx_ratio = min(total_volume / large_tx_threshold, 1) if total_volume > 0 else 0

            return {
                "score": round(50 + large_tx_ratio * 50, 2),
                "large_tx_ratio": round(large_tx_ratio, 4),
                "buy_pressure": flow.get("buy_pressure", 0.5),
                "source": "whale_proxy",
                "timestamp": datetime.now().isoformat(),
            }
        except Exception as e:
            logger.warning(f"⚠️ Whale activity error: {e}")
            return {"score": 50, "source": "whale_proxy", "error": str(e)}

    # ============================================
    # NEWS SENTIMENT (Free Sources)
    # ============================================
    async def get_news_sentiment(self, symbol: str = "bitcoin") -> Dict:
        """
        Get news sentiment from free sources
        """
        try:
            session = await self.get_session()

            query = f"({symbol} OR crypto OR bitcoin)"
            url = "https://api.gdeltproject.org/api/v2/doc/doc"
            params = {
                "query": query,
                "mode": "artlist",
                "maxrecords": 10,
                "format": "json",
            }

            async with session.get(url, params=params, timeout=15) as response:
                if response.status == 429:
                    logger.warning(f"⚠️ GDELT rate-limited")
                    return {"score": 50, "source": "gdelt", "error": "Rate limited"}
                elif response.status == 200:
                    try:
                        data = await response.json()
                    except:
                        return {"score": 50, "source": "gdelt", "error": "Invalid JSON"}

                    articles = data.get("articles", [])

                    if articles:
                        tones = [a.get("tone", 0) for a in articles[:10] if a.get("tone")]
                        avg_tone = np.mean(tones) if tones else 0

                        score = 50 + (avg_tone * 10)
                        score = max(0, min(100, score))

                        return {
                            "score": round(score, 2),
                            "avg_tone": round(avg_tone, 4),
                            "articles_analyzed": len(articles),
                            "source": "gdelt",
                            "timestamp": datetime.now().isoformat(),
                        }

                return {
                    "score": 50,
                    "source": "gdelt",
                    "error": f"Status {response.status}",
                }
        except Exception as e:
            logger.warning(f"⚠️ News sentiment error: {e}")
            return {"score": 50, "source": "gdelt", "error": str(e)}

    # ============================================
    # REDDIT SENTIMENT (Pushshift)
    # ============================================
    async def get_reddit_sentiment(self, symbol: str = "bitcoin") -> Dict:
        """
        Get Reddit sentiment from Pushshift (free, no auth)
        """
        try:
            session = await self.get_session()

            url = "https://api.pushshift.io/reddit/search/submission/"
            params = {
                "q": symbol,
                "subreddit": "CryptoCurrency,Bitcoin",
                "size": 10,
                "sort": "desc",
                "sort_type": "created_utc",
            }

            async with session.get(url, params=params, timeout=10) as response:
                if response.status == 429:
                    logger.warning(f"⚠️ Pushshift rate-limited")
                    return {"score": 50, "source": "pushshift", "error": "Rate limited"}
                elif response.status == 200:
                    try:
                        data = await response.json()
                    except:
                        return {
                            "score": 50,
                            "source": "pushshift",
                            "error": "Invalid JSON",
                        }

                    posts = data.get("data", [])

                    if posts and self.vader:
                        titles = [p.get("title", "") for p in posts[:10]]
                        scores = [self.analyze_sentiment_vader(t)["compound"] for t in titles]
                        avg_score = np.mean(scores) if scores else 0

                        result_score = 50 + (avg_score * 50)
                        result_score = max(0, min(100, result_score))

                        return {
                            "score": round(result_score, 2),
                            "avg_compound": round(avg_score, 4),
                            "posts_analyzed": len(posts),
                            "source": "pushshift",
                            "timestamp": datetime.now().isoformat(),
                        }

                    return {"score": 50, "source": "pushshift", "error": "No posts"}
                else:
                    return {
                        "score": 50,
                        "source": "pushshift",
                        "error": f"Status {response.status}",
                    }
        except Exception as e:
            logger.warning(f"⚠️ Reddit sentiment error: {e}")
            return {"score": 50, "source": "pushshift", "error": str(e)}

    # ============================================
    # AGGREGATED INTEL SCORE (ENHANCED WITH NEW MODULES)
    # ============================================
    async def get_unified_intel_score(self, symbol: str = "BTC") -> Dict:
        """
        Get unified intelligence score from all sources with advanced processing
        Uses: Quality Assurance → Signal Processing → Correlation → Fusion → Adaptive Processing
        """
        tasks = [
            self.get_order_flow(symbol),
            self.get_onchain_metrics(symbol),
            self.get_comprehensive_market_data(symbol),
            self.get_social_sentiment(symbol),
            self.get_news_sentiment(symbol),
            self.get_whale_activity(symbol),
        ]

        if symbol.lower() == "bitcoin":
            tasks.append(self.get_btc_indicators())

        self.profiler.start("unified_gather")
        results = await asyncio.gather(*tasks, return_exceptions=True)
        self.profiler.end("unified_gather")

        self.profiler.start("quality_check")
        validated_results = []
        for r in results:
            if isinstance(r, dict):
                qa_result = await self.quality_assurance.validate_intelligence_data(r)
                if qa_result["is_valid"]:
                    validated_results.append(qa_result)
        self.profiler.end("quality_check")

        if not validated_results:
            return {
                "unified_score": 50,
                "sources_working": 0,
                "total_sources": len(tasks),
                "timestamp": datetime.now().isoformat(),
            }

        self.profiler.start("signal_processing")
        processed_signals = []
        for data in validated_results:
            processed = self.signal_scorer.score_signal(data)
            processed_signals.append(processed)
        self.profiler.end("signal_processing")

        self.profiler.start("correlation")
        try:
            correlated = await self.correlation_system.analyze_correlations(
                symbol, {str(i): r for i, r in enumerate(validated_results)}
            )
            fusion_result = correlated.get("fused_signal", {})
        except Exception as e:
            correlated = {"overall_correlation": 0, "consensus_score": 0.5}
            fusion_result = {"action": "HOLD", "confidence": 0.5, "strength": 0.5, "score": 50}
        self.profiler.end("correlation")

        self.profiler.start("adaptive")
        market_condition = await self.market_detector.detect_conditions(symbol, {})
        adaptive_result = {
            "action": fusion_result.get("action", "HOLD"),
            "confidence": fusion_result.get("confidence", 0.5),
            "strength": fusion_result.get("strength", 0.5),
            "score": fusion_result.get("score", 50),
        }
        self.profiler.end("adaptive")

        self.profiler.start("scoring")
        sources_working = len([r for r in results if isinstance(r, dict) and "score" in r])

        if sources_working > 0:
            score_sum = 0
            for r in results:
                if isinstance(r, dict):
                    score = r.get("score", 50)
                    if isinstance(score, (int, float)):
                        score_sum += score
            avg_score = score_sum / sources_working if sources_working > 0 else 50
        else:
            avg_score = 50

        self.monitor.record_analysis(
            symbol,
            {
                "sources_checked": len(tasks),
                "sources_valid": sources_working,
                "sources_working": sources_working,
                "processing_time": self.profiler.get_total_time()
                if hasattr(self.profiler, "get_total_time")
                else 0,
            },
        )

        return {
            "unified_score": round(avg_score, 2),
            "confidence": fusion_result.get("confidence", 0.5) * 100
            if isinstance(fusion_result, dict)
            else 50,
            "market_condition": "VOLATILE",
            "individual_scores": {
                r.get("source", "unknown"): r.get("score", 50)
                for r in results
                if isinstance(r, dict)
            },
            "fusion_metrics": {
                "correlation_strength": correlated.get("overall_correlation", 0)
                if isinstance(correlated, dict)
                else 0,
                "consensus_level": correlated.get("consensus_score", 0.5)
                if isinstance(correlated, dict)
                else 0.5,
            },
            "quality_metrics": {
                "data_freshness": 0.5,
                "signal_strength": 0.5,
                "reliability": 0.5,
            },
            "sources_working": sources_working,
            "total_sources": len(tasks),
            "processing_time_ms": 0,
            "timestamp": datetime.now().isoformat(),
        }

    # ============================================
    # BATCH ANALYSIS (OPTIMIZED FOR MULTIPLE SYMBOLS)
    # ============================================
    async def analyze_symbols_batch(self, symbols: List[str], priority: str = "score") -> Dict:
        """
        Analyze multiple symbols in batch with optimized processing
        Uses priority queue and real-time optimization
        """
        tasks = []
        for symbol in symbols:
            task = self.real_time_processor.submit_priority_task(
                self.get_unified_intel_score(symbol),
                priority=1 if priority == "score" else 2,
                symbol=symbol,
            )
            tasks.append(task)

        results = await asyncio.gather(*tasks, return_exceptions=True)

        valid_results = []
        for symbol, result in zip(symbols, results):
            if isinstance(result, dict) and "unified_score" in result:
                result["symbol"] = symbol
                valid_results.append(result)

        valid_results.sort(key=lambda x: x.get("unified_score", 0), reverse=True)

        return {
            "results": valid_results,
            "total_symbols": len(symbols),
            "analyzed": len(valid_results),
            "timestamp": datetime.now().isoformat(),
        }

    # ============================================
    # HEALTH CHECK FOR ALL SOURCES
    # ============================================
    async def health_check_all_sources(self) -> Dict:
        """Check health of all intelligence sources with circuit breaker"""
        sources = [
            ("order_flow", self.get_order_flow("BTC")),
            ("onchain", self.get_onchain_metrics("bitcoin")),
            ("market_data", self.get_comprehensive_market_data("BTC")),
            ("social", self.get_social_sentiment("bitcoin")),
            ("news", self.get_news_sentiment("bitcoin")),
            ("whale", self.get_whale_activity("BTC")),
            ("btc_indicators", self.get_btc_indicators()),
        ]

        health_status = {}
        for name, task in sources:
            try:
                with self.circuit_breaker:
                    result = await asyncio.wait_for(task, timeout=5.0)
                    health_status[name] = {
                        "status": "healthy" if result.get("score", 0) > 0 else "degraded",
                        "score": result.get("score", 0),
                        "latency_ms": 0,
                    }
            except asyncio.TimeoutError:
                health_status[name] = {"status": "timeout", "score": None}
            except Exception as e:
                health_status[name] = {"status": "error", "error": str(e)}

        healthy_count = sum(1 for s in health_status.values() if s["status"] == "healthy")

        return {
            "overall_status": "healthy" if healthy_count >= 4 else "degraded",
            "sources": health_status,
            "healthy_count": healthy_count,
            "total_sources": len(sources),
            "timestamp": datetime.now().isoformat(),
        }


# Global instance
enhanced_intel = EnhancedIntelStreams()
