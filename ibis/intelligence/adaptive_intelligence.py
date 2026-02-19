from ibis.core.logging_config import get_logger
"""
IBIS Adaptive Intelligence System
=================================
Context-aware intelligence that adapts to changing market conditions
"""

import asyncio
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import json
from collections import defaultdict, deque

import numpy as np

logger = get_logger(__name__)


class MarketConditionDetector:
    """
    Detects and categorizes market conditions based on comprehensive data
    """

    def __init__(self):
        self.condition_history = deque(maxlen=100)
        self._condition_cache = {}
        self._detector_thresholds = self._init_detector_thresholds()

    def _init_detector_thresholds(self) -> Dict:
        """Initialize market condition detection thresholds"""
        return {
            "volatility": {
                "low": 0.02,  # < 2% daily volatility
                "medium": 0.05,  # 2-5% daily volatility
                "high": 0.10,  # > 10% daily volatility
            },
            "trend_strength": {
                "weak": 0.2,  # R-squared < 0.2
                "moderate": 0.5,  # R-squared 0.2-0.5
                "strong": 0.8,  # R-squared > 0.8
            },
            "volume": {
                "low": 0.5,  # Volume < 50% of avg
                "normal": 2.0,  # Volume 0.5-2x avg
                "high": 3.0,  # Volume > 3x avg
            },
            "sentiment": {
                "fear": 30,  # Fear & Greed < 30
                "neutral": 70,  # Fear & Greed 30-70
                "greed": 100,  # Fear & Greed > 70
            },
            "liquidity": {
                "low": 100000,  # < $100K 24h volume
                "medium": 1000000,  # $100K-$1M 24h volume
                "high": 10000000,  # > $10M 24h volume
            },
        }

    async def detect_conditions(self, symbol: str, market_data: Dict) -> Dict:
        """
        Detect comprehensive market conditions for a specific symbol
        """
        logger.debug(f"Detecting conditions for {symbol}")

        # Get cached conditions if available
        cache_key = await self._generate_cache_key(symbol, market_data)
        if cache_key in self._condition_cache:
            cached = self._condition_cache[cache_key]
            if (time.time() - cached["timestamp"]) < 300:  # 5-minute cache
                return cached["conditions"]

        conditions = await self._analyze_market_data(symbol, market_data)

        # Cache conditions
        self._condition_cache[cache_key] = {
            "timestamp": time.time(),
            "conditions": conditions,
        }

        # Update history
        self.condition_history.append(
            {
                "symbol": symbol,
                "timestamp": datetime.now().isoformat(),
                "conditions": conditions,
                "market_data": self._extract_key_metrics(market_data),
            }
        )

        logger.debug(
            f"Conditions detected for {symbol}: {self._format_condition_summary(conditions)}"
        )

        return conditions

    async def _generate_cache_key(self, symbol: str, market_data: Dict) -> str:
        """Generate cache key from market data"""
        key_parts = [symbol]

        if "timestamp" in market_data:
            timestamp = market_data["timestamp"]
            if isinstance(timestamp, str):
                timestamp = datetime.fromisoformat(timestamp)
            elif isinstance(timestamp, int):
                # Handle both second and millisecond timestamps
                if timestamp > 9999999999:  # Milliseconds
                    timestamp = datetime.fromtimestamp(timestamp / 1000)
                else:  # Seconds
                    timestamp = datetime.fromtimestamp(timestamp)
            key_parts.append(str(timestamp.timestamp() // 300))

        return "|".join(key_parts)

    async def _analyze_market_data(self, symbol: str, market_data: Dict) -> Dict:
        """Analyze market data to determine conditions"""
        conditions = {
            "volatility": await self._detect_volatility(market_data),
            "trend": await self._detect_trend(market_data),
            "volume": await self._detect_volume(market_data),
            "sentiment": await self._detect_sentiment(market_data),
            "liquidity": await self._detect_liquidity(market_data),
            "regime": await self._detect_regime(market_data),
            "opportunity_score": await self._calculate_opportunity_score(market_data),
            "risk_level": await self._calculate_risk_level(market_data),
            "confidence": await self._calculate_confidence(market_data),
        }

        return conditions

    async def _detect_volatility(self, market_data: Dict) -> Dict:
        """Detect volatility conditions"""
        volatility_1h = market_data.get("volatility_1h", 0.0)
        volatility_24h = market_data.get("volatility_24h", 0.0)

        levels = self._detector_thresholds["volatility"]

        if volatility_24h < levels["low"]:
            volatility_level = "LOW"
        elif volatility_24h < levels["medium"]:
            volatility_level = "MEDIUM"
        elif volatility_24h < levels["high"]:
            volatility_level = "HIGH"
        else:
            volatility_level = "EXTREME"

        return {
            "level": volatility_level,
            "value_1h": volatility_1h,
            "value_24h": volatility_24h,
            "is_rising": volatility_1h > volatility_24h / 24,
        }

    async def _detect_trend(self, market_data: Dict) -> Dict:
        """Detect trend conditions"""
        trend_strength = market_data.get("trend_strength", 0.5)
        trend_direction = market_data.get("trend_direction", "NEUTRAL")

        levels = self._detector_thresholds["trend_strength"]

        if trend_strength < levels["weak"]:
            trend_strength = "WEAK"
        elif trend_strength < levels["moderate"]:
            trend_strength = "MODERATE"
        elif trend_strength < levels["strong"]:
            trend_strength = "STRONG"
        else:
            trend_strength = "VERY_STRONG"

        return {
            "strength": trend_strength,
            "direction": trend_direction,
            "confidence": market_data.get("trend_confidence", 0.5),
        }

    async def _detect_volume(self, market_data: Dict) -> Dict:
        """Detect volume conditions"""
        volume_24h = market_data.get("volume_24h", 0)
        avg_volume = market_data.get("avg_volume", volume_24h)

        if avg_volume <= 0:
            return {
                "level": "UNKNOWN",
                "value": volume_24h,
                "ratio": 1.0,
                "is_anomalous": False,
            }

        volume_ratio = volume_24h / avg_volume

        levels = self._detector_thresholds["volume"]

        if volume_ratio < levels["low"]:
            level = "LOW"
        elif volume_ratio < levels["normal"]:
            level = "NORMAL"
        elif volume_ratio < levels["high"]:
            level = "HIGH"
        else:
            level = "EXTREME"

        return {
            "level": level,
            "value": volume_24h,
            "ratio": volume_ratio,
            "is_anomalous": volume_ratio > levels["high"] or volume_ratio < levels["low"] * 0.5,
        }

    async def _detect_sentiment(self, market_data: Dict) -> Dict:
        """Detect sentiment conditions"""
        fear_greed_index = market_data.get("fear_greed_index", 50)
        sentiment_score = market_data.get("sentiment_score", 0.5)

        levels = self._detector_thresholds["sentiment"]

        if fear_greed_index < levels["fear"]:
            sentiment_level = "FEAR"
        elif fear_greed_index < levels["neutral"]:
            sentiment_level = "NEUTRAL"
        else:
            sentiment_level = "GREED"

        return {
            "level": sentiment_level,
            "fear_greed_index": fear_greed_index,
            "sentiment_score": sentiment_score,
            "confidence": market_data.get("sentiment_confidence", 0.5),
        }

    async def _detect_liquidity(self, market_data: Dict) -> Dict:
        """Detect liquidity conditions"""
        volume_24h = market_data.get("volume_24h", 0)
        market_cap = market_data.get("market_cap", 0)

        levels = self._detector_thresholds["liquidity"]

        if volume_24h < levels["low"]:
            liquidity_level = "LOW"
        elif volume_24h < levels["medium"]:
            liquidity_level = "MEDIUM"
        elif volume_24h < levels["high"]:
            liquidity_level = "HIGH"
        else:
            liquidity_level = "EXCELLENT"

        # Calculate liquidity ratio (volume/market cap)
        liquidity_ratio = volume_24h / market_cap if market_cap > 0 else 0

        return {
            "level": liquidity_level,
            "volume_24h": volume_24h,
            "market_cap": market_cap,
            "ratio": liquidity_ratio,
            "is_liquid": liquidity_level in ["HIGH", "EXCELLENT"],
        }

    async def _detect_regime(self, market_data: Dict) -> Dict:
        """Detect market regime"""
        volatility = await self._detect_volatility(market_data)
        trend = await self._detect_trend(market_data)
        volume = await self._detect_volume(market_data)
        sentiment = await self._detect_sentiment(market_data)

        # Determine regime based on combinations of conditions
        if volatility["level"] == "EXTREME" and sentiment["level"] in ["FEAR", "GREED"]:
            regime = (
                "CRASH"
                if sentiment["level"] == "FEAR" and trend["direction"] == "DOWN"
                else "BUBBLE"
            )
        elif volatility["level"] == "HIGH" and trend["strength"] in ["WEAK", "MODERATE"]:
            regime = "VOLATILE"
        elif trend["strength"] in ["STRONG", "VERY_STRONG"]:
            regime = "TRENDING" if volatility["level"] == "MEDIUM" else "TREND_WITH_VOLATILITY"
        elif volatility["level"] == "LOW" and sentiment["level"] == "NEUTRAL":
            regime = "CALM"
        else:
            regime = "UNCERTAIN"

        return {
            "name": regime,
            "characteristics": self._get_regime_characteristics(regime),
            "confidence": self._calculate_regime_confidence(volatility, trend, volume, sentiment),
        }

    def _get_regime_characteristics(self, regime: str) -> List[str]:
        """Get regime characteristics"""
        characteristics = {
            "TRENDING": ["Strong trend", "Medium volatility", "Healthy volume"],
            "VOLATILE": ["High volatility", "Weak trend", "Erratic movement"],
            "CALM": ["Low volatility", "Stable prices", "Low volume"],
            "CRASH": ["Extreme fear", "High volatility", "Selling pressure"],
            "BUBBLE": ["Extreme greed", "High volatility", "Buying pressure"],
            "TREND_WITH_VOLATILITY": ["Strong trend", "High volatility", "Breakout potential"],
            "UNCERTAIN": ["Mixed signals", "Changing conditions", "Wait for confirmation"],
        }

        return characteristics.get(regime, ["Unknown"])

    def _calculate_regime_confidence(
        self, volatility: Dict, trend: Dict, volume: Dict, sentiment: Dict
    ) -> float:
        """Calculate regime classification confidence"""
        # Simple weighted average of contributing factors
        weights = {
            "volatility": 0.3,
            "trend": 0.3,
            "volume": 0.2,
            "sentiment": 0.2,
        }

        scores = {
            "volatility": self._condition_score_to_confidence(volatility["level"]),
            "trend": trend["confidence"],
            "volume": self._condition_score_to_confidence(volume["level"]),
            "sentiment": sentiment["confidence"],
        }

        total_score = sum(scores[k] * weights[k] for k in scores)
        return min(1.0, max(0.0, total_score))

    def _condition_score_to_confidence(self, level: str) -> float:
        """Convert condition level to confidence score"""
        level_scores = {
            "LOW": 0.3,
            "MEDIUM": 0.5,
            "HIGH": 0.7,
            "EXTREME": 0.9,
            "WEAK": 0.3,
            "MODERATE": 0.6,
            "STRONG": 0.8,
            "VERY_STRONG": 0.95,
            "FEAR": 0.6,
            "NEUTRAL": 0.4,
            "GREED": 0.6,
            "NORMAL": 0.5,
            "UNKNOWN": 0.2,
        }

        return level_scores.get(level.upper(), 0.5)

    async def _calculate_opportunity_score(self, market_data: Dict) -> float:
        """Calculate opportunity score based on market conditions"""
        # Don't call _analyze_market_data here - it causes infinite recursion
        # Use market_data directly to extract regime info
        regime = market_data.get("regime", {}).get("name", "UNCERTAIN")

        if regime == "TRENDING":
            return await self._calculate_trending_opportunity({})
        elif regime == "VOLATILE":
            return await self._calculate_volatile_opportunity({})
        elif regime == "CALM":
            return await self._calculate_calm_opportunity({})
        elif regime == "CRASH" or regime == "BUBBLE":
            return await self._calculate_extreme_opportunity({})
        else:
            return 0.5

    async def _calculate_trending_opportunity(self, conditions: Dict) -> float:
        """Calculate opportunity score in trending markets"""
        trend_strength = self._condition_score_to_confidence(conditions["trend"]["strength"])
        volatility_score = self._condition_score_to_confidence(conditions["volatility"]["level"])
        volume_score = self._condition_score_to_confidence(conditions["volume"]["level"])

        return trend_strength * 0.5 + volatility_score * 0.25 + volume_score * 0.25

    async def _calculate_volatile_opportunity(self, conditions: Dict) -> float:
        """Calculate opportunity score in volatile markets"""
        volatility_score = self._condition_score_to_confidence(conditions["volatility"]["level"])
        sentiment_score = self._condition_score_to_confidence(conditions["sentiment"]["level"])

        return volatility_score * 0.6 + sentiment_score * 0.4

    async def _calculate_calm_opportunity(self, conditions: Dict) -> float:
        """Calculate opportunity score in calm markets"""
        volatility_score = self._condition_score_to_confidence(conditions["volatility"]["level"])
        volume_score = self._condition_score_to_confidence(conditions["volume"]["level"])

        return (1 - volatility_score) * 0.7 + volume_score * 0.3

    async def _calculate_extreme_opportunity(self, conditions: Dict) -> float:
        """Calculate opportunity score in extreme markets"""
        sentiment_score = self._condition_score_to_confidence(conditions["sentiment"]["level"])
        trend_strength = self._condition_score_to_confidence(conditions["trend"]["strength"])

        return min(0.95, sentiment_score * 0.7 + trend_strength * 0.3)

    async def _calculate_risk_level(self, market_data: Dict) -> str:
        """Calculate overall risk level based on conditions"""
        # Don't call _analyze_market_data here - it causes infinite recursion
        volatility = market_data.get("volatility_24h", 0.0)
        trend = market_data.get("change_24h", 0.0)
        regime = market_data.get("regime", {}).get("name", "UNCERTAIN")

        if volatility > 10 or abs(trend) > 15:
            return "HIGH"
        elif volatility > 5 or abs(trend) > 8:
            return "MEDIUM"
        else:
            return "LOW"

        risk_factors = []

        # Volatility risk
        if conditions["volatility"]["level"] in ["HIGH", "EXTREME"]:
            risk_factors.append(0.3)

        # Liquidity risk
        if conditions["liquidity"]["level"] in ["LOW", "MEDIUM"]:
            risk_factors.append(0.25)

        # Sentiment risk
        if conditions["sentiment"]["level"] in ["FEAR", "GREED"]:
            risk_factors.append(0.2)

        # Trend risk
        if conditions["trend"]["strength"] in ["WEAK"]:
            risk_factors.append(0.15)

        # Volume risk
        if conditions["volume"]["level"] in ["LOW", "EXTREME"]:
            risk_factors.append(0.1)

        total_risk = sum(risk_factors)

        if total_risk > 0.7:
            return "EXTREME"
        elif total_risk > 0.5:
            return "HIGH"
        elif total_risk > 0.3:
            return "MEDIUM"
        else:
            return "LOW"

    async def _calculate_confidence(self, market_data: Dict) -> float:
        """Calculate confidence in condition assessment"""
        # Don't call _analyze_market_data here - it causes infinite recursion
        return 0.7  # Default confidence

    def _extract_key_metrics(self, market_data: Dict) -> Dict:
        """Extract key metrics for history storage"""
        return {
            "price": market_data.get("price"),
            "volume": market_data.get("volume_24h"),
            "market_cap": market_data.get("market_cap"),
            "volatility": market_data.get("volatility_24h"),
            "sentiment": market_data.get("sentiment_score"),
            "fear_greed": market_data.get("fear_greed_index"),
        }

    def _format_condition_summary(self, conditions: Dict) -> str:
        """Format conditions for logging"""
        parts = [
            f"Regime: {conditions['regime']['name']}",
            f"Volatility: {conditions['volatility']['level']}",
            f"Trend: {conditions['trend']['direction']} ({conditions['trend']['strength']})",
            f"Sentiment: {conditions['sentiment']['level']}",
            f"Liquidity: {conditions['liquidity']['level']}",
        ]

        return ", ".join(parts)


class AdaptiveSignalProcessor:
    """
    Adaptive signal processor that adjusts to market conditions
    """

    def __init__(self, market_condition_detector: MarketConditionDetector):
        self.condition_detector = market_condition_detector
        self.processing_strategies = self._init_processing_strategies()
        self.strategy_history = deque(maxlen=100)
        self._strategy_cache = {}

    def _init_processing_strategies(self) -> Dict:
        """Initialize market condition to strategy mapping"""
        return {
            "TRENDING": {
                "name": "Trend Following",
                "params": {
                    "signal_quality_threshold": 0.85,
                    "volume_weight": 0.3,
                    "trend_weight": 0.4,
                    "sentiment_weight": 0.2,
                    "noise_filter": "strong",
                },
            },
            "VOLATILE": {
                "name": "Volatility Trading",
                "params": {
                    "signal_quality_threshold": 0.75,
                    "volume_weight": 0.4,
                    "trend_weight": 0.2,
                    "sentiment_weight": 0.3,
                    "noise_filter": "moderate",
                },
            },
            "CALM": {
                "name": "Mean Reversion",
                "params": {
                    "signal_quality_threshold": 0.7,
                    "volume_weight": 0.2,
                    "trend_weight": 0.3,
                    "sentiment_weight": 0.4,
                    "noise_filter": "light",
                },
            },
            "CRASH": {
                "name": "Crash Protection",
                "params": {
                    "signal_quality_threshold": 0.9,
                    "volume_weight": 0.5,
                    "trend_weight": 0.3,
                    "sentiment_weight": 0.1,
                    "noise_filter": "very_strong",
                },
            },
            "BUBBLE": {
                "name": "Bubble Detection",
                "params": {
                    "signal_quality_threshold": 0.85,
                    "volume_weight": 0.4,
                    "trend_weight": 0.2,
                    "sentiment_weight": 0.3,
                    "noise_filter": "strong",
                },
            },
            "UNCERTAIN": {
                "name": "Conservative",
                "params": {
                    "signal_quality_threshold": 0.8,
                    "volume_weight": 0.3,
                    "trend_weight": 0.3,
                    "sentiment_weight": 0.3,
                    "noise_filter": "strong",
                },
            },
        }

    async def process_signals(self, symbol: str, raw_signals: Dict, market_data: Dict) -> Dict:
        """
        Process signals with adaptive configuration based on market conditions
        """
        logger.debug(f"Processing signals for {symbol}")

        # Detect market conditions
        conditions = await self.condition_detector.detect_conditions(symbol, market_data)

        # Determine processing strategy
        strategy = await self._determine_processing_strategy(conditions)

        # Apply strategy to process signals
        processed_signals = await self._apply_processing_strategy(
            symbol, raw_signals, strategy, conditions
        )

        # Cache strategy choice
        self._strategy_cache[symbol] = {
            "timestamp": time.time(),
            "strategy": strategy["name"],
            "conditions": conditions,
        }

        # Update history
        self.strategy_history.append(
            {
                "symbol": symbol,
                "timestamp": datetime.now().isoformat(),
                "strategy": strategy["name"],
                "conditions": conditions,
                "signal_count": len(raw_signals),
            }
        )

        logger.debug(f"Applied strategy: {strategy['name']} to {len(raw_signals)} signals")

        return processed_signals

    async def _determine_processing_strategy(self, conditions: Dict) -> Dict:
        """Determine optimal processing strategy based on conditions"""
        regime = conditions["regime"]["name"]

        if regime in self.processing_strategies:
            strategy = self.processing_strategies[regime]
        else:
            strategy = self.processing_strategies["UNCERTAIN"]

        # Adjust strategy based on specific conditions
        strategy = await self._adjust_strategy_for_conditions(strategy, conditions)

        return strategy

    async def _adjust_strategy_for_conditions(self, strategy: Dict, conditions: Dict) -> Dict:
        """Adjust strategy parameters based on specific conditions"""
        adjusted = strategy.copy()
        params = strategy["params"].copy()

        # Adjust based on volatility
        if conditions["volatility"]["level"] == "EXTREME":
            params["signal_quality_threshold"] = min(params["signal_quality_threshold"] + 0.1, 0.95)
            params["noise_filter"] = "very_strong"

        # Adjust based on liquidity
        if conditions["liquidity"]["level"] == "LOW":
            params["volume_weight"] = min(params["volume_weight"] + 0.2, 0.6)
            params["signal_quality_threshold"] = min(params["signal_quality_threshold"] + 0.05, 0.9)

        # Adjust based on trend strength
        if conditions["trend"]["strength"] == "WEAK":
            params["trend_weight"] = max(params["trend_weight"] - 0.1, 0.1)
            params["volume_weight"] = min(params["volume_weight"] + 0.1, 0.5)

        adjusted["params"] = params
        return adjusted

    async def _apply_processing_strategy(
        self, symbol: str, raw_signals: Dict, strategy: Dict, conditions: Dict
    ) -> Dict:
        """Apply processing strategy to raw signals"""
        from ibis.intelligence.advanced_signal_processor import AdvancedSignalProcessor

        processor = AdvancedSignalProcessor()

        # Get strategy-specific parameters
        quality_threshold = strategy["params"]["signal_quality_threshold"]
        volume_weight = strategy["params"]["volume_weight"]
        trend_weight = strategy["params"]["trend_weight"]
        sentiment_weight = strategy["params"]["sentiment_weight"]
        noise_filter = strategy["params"]["noise_filter"]

        # Apply quality filtering based on conditions
        filtered_signals = await self._filter_signals_by_quality(
            raw_signals, quality_threshold, conditions
        )

        # Adjust signal weights based on strategy
        weighted_signals = await self._weight_signals(
            filtered_signals, volume_weight, trend_weight, sentiment_weight
        )

        # Apply noise filtering
        processed_signals = await self._apply_noise_filtering(
            weighted_signals, noise_filter, conditions
        )

        return {
            "processed_signals": processed_signals,
            "strategy": strategy,
            "conditions": conditions,
            "signal_count": len(raw_signals),
            "filtered_count": len(filtered_signals),
            "quality_threshold": quality_threshold,
        }

    async def _filter_signals_by_quality(
        self, raw_signals: Dict, quality_threshold: float, conditions: Dict
    ) -> Dict:
        """Filter signals by quality threshold"""
        filtered = {}

        for source, signal in raw_signals.items():
            quality_score = await self._calculate_signal_quality(signal, conditions)
            if quality_score >= quality_threshold:
                filtered[source] = {**signal, "quality_score": quality_score}

        return filtered

    async def _calculate_signal_quality(self, signal: Dict, conditions: Dict) -> float:
        """Calculate signal quality score based on conditions"""
        # Base quality score
        base_score = signal.get("confidence", 0.5)

        # Adjust for market conditions
        adjustments = 0.0

        if conditions["volatility"]["level"] == "EXTREME":
            adjustments += 0.1  # Higher volatility reduces quality

        if conditions["liquidity"]["level"] == "LOW":
            adjustments += 0.05  # Lower liquidity reduces quality

        final_score = max(0.0, min(1.0, base_score - adjustments))

        return final_score

    async def _weight_signals(
        self, signals: Dict, volume_weight: float, trend_weight: float, sentiment_weight: float
    ) -> Dict:
        """Apply condition-specific weights to signals"""
        weighted = {}

        for source, signal in signals.items():
            weight = 1.0

            # Adjust weight based on signal type
            if "volume" in source.lower() or "liquidity" in source.lower():
                weight *= volume_weight
            elif "trend" in source.lower() or "momentum" in source.lower():
                weight *= trend_weight
            elif "sentiment" in source.lower() or "social" in source.lower():
                weight *= sentiment_weight

            weighted[source] = {**signal, "weight": weight}

        return weighted

    async def _apply_noise_filtering(
        self, signals: Dict, noise_filter: str, conditions: Dict
    ) -> Dict:
        """Apply noise filtering to signals"""
        if noise_filter == "light":
            return signals

        filtered = {}

        for source, signal in signals.items():
            should_keep = True

            if noise_filter == "moderate":
                should_keep = signal.get("quality_score", 0.5) > 0.6

            elif noise_filter == "strong":
                should_keep = (
                    signal.get("quality_score", 0.5) > 0.7 and signal.get("confidence", 0.5) > 0.8
                )

            elif noise_filter == "very_strong":
                should_keep = (
                    signal.get("quality_score", 0.5) > 0.8 and signal.get("confidence", 0.5) > 0.9
                )

            if should_keep:
                filtered[source] = signal

        return filtered


class AdaptiveSourceAllocator:
    """
    Adaptive source allocator that dynamically prioritizes intelligence sources
    based on market conditions
    """

    def __init__(self, market_condition_detector: MarketConditionDetector):
        self.condition_detector = market_condition_detector
        self.source_priorities = self._init_source_priorities()
        self.allocation_history = deque(maxlen=100)

    def _init_source_priorities(self) -> Dict:
        """Initialize source priority configurations per market condition"""
        return {
            "TRENDING": {
                "coingecko": 0.25,
                "glassnode": 0.2,
                "messari": 0.18,
                "twitter": 0.15,
                "reddit": 0.12,
                "onchain": 0.1,
            },
            "VOLATILE": {
                "glassnode": 0.3,
                "coingecko": 0.2,
                "twitter": 0.2,
                "onchain": 0.15,
                "messari": 0.1,
                "reddit": 0.05,
            },
            "CALM": {
                "coingecko": 0.2,
                "messari": 0.2,
                "onchain": 0.15,
                "twitter": 0.15,
                "reddit": 0.15,
                "glassnode": 0.15,
            },
            "CRASH": {
                "glassnode": 0.35,
                "onchain": 0.3,
                "coingecko": 0.2,
                "messari": 0.1,
                "twitter": 0.05,
            },
            "BUBBLE": {
                "twitter": 0.3,
                "reddit": 0.25,
                "glassnode": 0.2,
                "coingecko": 0.15,
                "onchain": 0.1,
            },
            "UNCERTAIN": {
                "coingecko": 0.2,
                "glassnode": 0.2,
                "messari": 0.15,
                "twitter": 0.15,
                "reddit": 0.15,
                "onchain": 0.15,
            },
        }

    async def allocate_sources(
        self, symbol: str, available_sources: List[str], market_data: Dict
    ) -> List[Dict]:
        """
        Allocate intelligence sources with optimal priorities based on market conditions
        """
        logger.debug(f"Allocating sources for {symbol}")

        # Detect market conditions
        conditions = await self.condition_detector.detect_conditions(symbol, market_data)

        # Get base priorities for current regime
        regime = conditions["regime"]["name"]
        base_priorities = self.source_priorities.get(regime, self.source_priorities["UNCERTAIN"])

        # Adjust priorities based on specific conditions
        adjusted_priorities = await self._adjust_priorities_for_conditions(
            base_priorities, conditions
        )

        # Filter to available sources
        filtered_priorities = {
            source: weight
            for source, weight in adjusted_priorities.items()
            if source in available_sources
        }

        # Normalize priorities to sum to 1
        total_weight = sum(filtered_priorities.values())
        normalized_priorities = {
            source: weight / total_weight for source, weight in filtered_priorities.items()
        }

        # Create allocation list with sorted priorities
        allocation = [
            {"source": source, "weight": weight}
            for source, weight in sorted(
                normalized_priorities.items(), key=lambda x: x[1], reverse=True
            )
        ]

        # Update allocation history
        self.allocation_history.append(
            {
                "symbol": symbol,
                "timestamp": datetime.now().isoformat(),
                "regime": regime,
                "allocation": allocation,
                "conditions": conditions,
            }
        )

        logger.debug(
            f"Source allocation: {[f'{s}: {w:.2f}' for s, w in normalized_priorities.items()]}"
        )

        return allocation

    async def _adjust_priorities_for_conditions(
        self, base_priorities: Dict, conditions: Dict
    ) -> Dict:
        """Adjust source priorities based on specific market conditions"""
        adjusted = base_priorities.copy()

        # Adjust for volatility
        if conditions["volatility"]["level"] == "EXTREME":
            adjusted = {
                k: v * (1.1 if "glassnode" in k or "onchain" in k else 0.95)
                for k, v in adjusted.items()
            }

        # Adjust for liquidity
        if conditions["liquidity"]["level"] == "LOW":
            adjusted = {
                k: v * (1.15 if "coingecko" in k or "messari" in k else 0.95)
                for k, v in adjusted.items()
            }

        # Adjust for sentiment extremes
        if conditions["sentiment"]["level"] in ["FEAR", "GREED"]:
            adjusted = {
                k: v * (1.2 if "twitter" in k or "reddit" in k else 0.95)
                for k, v in adjusted.items()
            }

        # Adjust for trend strength
        if conditions["trend"]["strength"] == "WEAK":
            adjusted = {
                k: v * (1.1 if "glassnode" in k or "onchain" in k else 0.95)
                for k, v in adjusted.items()
            }

        return adjusted


# Global instances
market_condition_detector = MarketConditionDetector()
adaptive_signal_processor = AdaptiveSignalProcessor(market_condition_detector)
adaptive_source_allocator = AdaptiveSourceAllocator(market_condition_detector)
