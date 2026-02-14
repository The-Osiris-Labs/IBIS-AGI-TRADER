"""
IBIS Unified Scoring System
Single source of truth for all symbol scoring
Replaces multiple parallel scoring systems with one data-driven approach
"""

import asyncio
import numpy as np
from dataclasses import dataclass
from typing import Dict, List, Optional
from datetime import datetime


@dataclass
class RegimeConfig:
    """Market regime-adaptive weight configuration"""

    name: str
    technical_weight: float
    agi_weight: float
    mtf_weight: float
    volume_weight: float
    sentiment_weight: float
    min_threshold_percentile: int  # Top X% to select
    max_positions_scale: float


REGIME_CONFIGS = {
    "STRONG_BULL": RegimeConfig(
        name="STRONG_BULL",
        technical_weight=0.30,
        agi_weight=0.35,  # Higher weight on AGI in bull markets
        mtf_weight=0.15,
        volume_weight=0.10,
        sentiment_weight=0.10,
        min_threshold_percentile=70,  # Top 30%
        max_positions_scale=1.5,
    ),
    "BULLISH": RegimeConfig(
        name="BULLISH",
        technical_weight=0.35,
        agi_weight=0.30,
        mtf_weight=0.15,
        volume_weight=0.10,
        sentiment_weight=0.10,
        min_threshold_percentile=65,  # Top 35%
        max_positions_scale=1.2,
    ),
    "VOLATILE": RegimeConfig(
        name="VOLATILE",
        technical_weight=0.40,  # More weight on technical in volatile
        agi_weight=0.25,
        mtf_weight=0.20,  # More weight on MTF
        volume_weight=0.10,
        sentiment_weight=0.05,
        min_threshold_percentile=60,  # Top 40%
        max_positions_scale=1.0,
    ),
    "NEUTRAL": RegimeConfig(
        name="NEUTRAL",
        technical_weight=0.35,
        agi_weight=0.30,
        mtf_weight=0.15,
        volume_weight=0.10,
        sentiment_weight=0.10,
        min_threshold_percentile=60,  # Top 40%
        max_positions_scale=1.0,
    ),
    "BEARISH": RegimeConfig(
        name="BEARISH",
        technical_weight=0.40,
        agi_weight=0.25,
        mtf_weight=0.15,
        volume_weight=0.15,  # More weight on volume (liquidity matters)
        sentiment_weight=0.05,
        min_threshold_percentile=75,  # Top 25% only
        max_positions_scale=0.7,
    ),
    "CRASH": RegimeConfig(
        name="CRASH",
        technical_weight=0.45,  # Very conservative
        agi_weight=0.20,
        mtf_weight=0.15,
        volume_weight=0.15,
        sentiment_weight=0.05,
        min_threshold_percentile=80,  # Top 20% only
        max_positions_scale=0.5,
    ),
}


class UnifiedScorer:
    """
    Single source of truth for symbol scoring.
    Replaces: _calculate_technical_strength, calculate_intelligence_score, funnel scores
    """

    def __init__(self, regime: str = "VOLATILE"):
        self.score_history: List[float] = []
        self.volatility_history: List[float] = []
        self.regime = regime
        self.regime_config = REGIME_CONFIGS.get(regime, REGIME_CONFIGS["VOLATILE"])
        self.funnel_scores = []

    def calculate_funnel_score(self, symbol_data: Dict) -> float:
        """
        Calculate funnel score that simulates the probability of a symbol passing through
        all analysis stages (discovery → filtering → analysis → trading)
        """
        score = 50

        # Stage 1: Discovery (volume and volatility)
        volume_24h = symbol_data.get("volume_24h", 0)
        volatility = symbol_data.get("volatility", 0.05)

        if volume_24h > 1000000:
            score += 20
        elif volume_24h > 100000:
            score += 15
        elif volume_24h > 10000:
            score += 10

        if 0.03 < volatility < 0.15:
            score += 10
        elif 0.02 < volatility < 0.20:
            score += 5

        # Stage 2: Filtering (price and momentum)
        change_24h = symbol_data.get("change_24h", 0)
        momentum_1h = symbol_data.get("change_1h", 0)

        if abs(change_24h) > 3:
            score += 15
        elif abs(change_24h) > 1:
            score += 10

        if abs(momentum_1h) > 0.5:
            score += 10
        elif abs(momentum_1h) > 0.2:
            score += 5

        # Stage 3: Analysis (indicators and intelligence)
        technical_score = symbol_data.get("technical_score", 50)
        agi_score = symbol_data.get("agi_score", 50)

        score += (technical_score - 50) * 0.1
        score += (agi_score - 50) * 0.1

        # Stage 4: Trading (liquidity and spread)
        spread = symbol_data.get("spread", 0.02)
        if spread < 0.01:
            score += 10
        elif spread < 0.02:
            score += 5

        return max(0, min(100, score))
        self.regime = "VOLATILE"
        self.regime_config = REGIME_CONFIGS["VOLATILE"]

    def update_regime(self, regime: str):
        """Update regime and weights"""
        self.regime = regime.upper()
        self.regime_config = REGIME_CONFIGS.get(self.regime, REGIME_CONFIGS["NEUTRAL"])

    def calculate_agi_score(self, symbol: str, symbol_data: Dict) -> float:
        """
        Calculate AGI score using multi-source intelligence factors
        This simulates the AGI decision-making process
        """
        score = 50

        # Price action patterns
        if "candle_analysis" in symbol_data:
            patterns = symbol_data["candle_analysis"].get("patterns", [])
            score += len([p for p in patterns if "bullish" in p.lower()]) * 3
            score -= len([p for p in patterns if "bearish" in p.lower()]) * 3

        # Market correlation
        if "market_correlation" in symbol_data:
            correlation = symbol_data["market_correlation"]
            if correlation < 0.3:
                score += 5  # Low correlation (diversification benefit)
            elif correlation > 0.8:
                score -= 5  # High correlation (systemic risk)

        # Volume profile
        volume_profile = symbol_data.get("volume_profile", {})
        if "accumulation" in volume_profile.get("type", ""):
            score += 8
        elif "distribution" in volume_profile.get("type", ""):
            score -= 8

        # Sentiment analysis
        sentiment = symbol_data.get("sentiment", {})
        sentiment_score = sentiment.get("score", 50)
        score += (sentiment_score - 50) * 0.2

        # On-chain metrics
        if "onchain" in symbol_data:
            onchain = symbol_data["onchain"]
            if onchain.get("network_growth", 0) > 100:
                score += 5
            if onchain.get("active_addresses", 0) > 1000:
                score += 3

        return max(0, min(100, score))

    def calculate_technical_score(
        self,
        momentum_1h: float,
        change_24h: float,
        volatility: float = 0.05,
        volume_24h: float = 0,
    ) -> float:
        """
        Calculate technical strength score (0-100)
        Based on momentum, price change, volatility, and volume
        """
        # Momentum contribution (capped at +/- 25 points)
        momentum_score = max(-25, min(25, momentum_1h * 25))

        # 24h change contribution (capped at +/- 30 points)
        change_score = max(-30, min(30, change_24h * 6))

        # Volatility bonus (optimal range 3-8%)
        if 0.03 <= volatility <= 0.08:
            vol_score = 15
        elif volatility < 0.03:
            vol_score = 10
        elif volatility > 0.15:
            vol_score = -10  # Penalize extreme volatility
        else:
            vol_score = 5

        # Volume score (normalized 0-100)
        min_volume = 10000  # $10k minimum
        max_volume = 1000000  # $1M maximum
        if volume_24h > 0:
            vol_ratio = min(volume_24h / min_volume, max_volume / min_volume)
            volume_score = min(vol_ratio * 50, 100) * 0.2  # Max 20 points
        else:
            volume_score = 0

        base_score = 50 + momentum_score + change_score + vol_score + volume_score
        return max(0, min(100, base_score))

    def calculate_mtf_score(
        self,
        trends: List[str],
        alignment_score: float,
    ) -> float:
        """
        Calculate multi-timeframe alignment score (0-100)
        Based on trend consistency across timeframes
        """
        if not trends:
            return 50.0

        bullish = sum(1 for t in trends if t.upper() == "BULLISH")
        bearish = sum(1 for t in trends if t.upper() == "BEARISH")

        # Score based on alignment
        if bullish >= 4:
            mtf_score = 85 + (bullish - 4) * 5
        elif bearish >= 4:
            mtf_score = 15 - (bearish - 4) * 5
        elif bullish == 3:
            mtf_score = 70
        elif bearish == 3:
            mtf_score = 30
        elif bullish == 2 and bearish == 0:
            mtf_score = 60
        elif bearish == 2 and bullish == 0:
            mtf_score = 40
        else:
            mtf_score = 50

        # Blend with alignment score
        blended = (mtf_score * 0.6) + (alignment_score * 0.4)
        return max(0, min(100, blended))

    def calculate_sentiment_score(
        self,
        fear_greed_index: int,
        symbol_sentiment: float = 50,
        dominance_score: float = 50,
        altcoin_season_index: float = 50,
        eth_gas_score: float = 50,
        symbol: str = "BTC",
    ) -> float:
        """
        Calculate sentiment score (0-100)
        Based on Fear & Greed index, symbol-specific sentiment, and market context
        """
        # Fear & Greed contribution (inverted - fear is bullish for contrarian)
        if fear_greed_index <= 25:  # Extreme Fear
            fg_score = 70
        elif fear_greed_index <= 45:  # Fear
            fg_score = 55
        elif fear_greed_index <= 55:  # Neutral
            fg_score = 50
        elif fear_greed_index <= 75:  # Greed
            fg_score = 45
        else:  # Extreme Greed
            fg_score = 30

        # Market context adjustments based on symbol type
        context_score = 50
        if symbol.lower() == "btc":
            # BTC benefits from high dominance
            context_score = dominance_score
        elif symbol.lower() == "eth":
            # ETH benefits from moderate dominance and healthy network
            context_score = (dominance_score * 0.5) + (eth_gas_score * 0.5)
        else:
            # Altcoins benefit from altcoin season
            context_score = altcoin_season_index

        # Blend all sentiment factors
        sentiment = (fg_score * 0.4) + (symbol_sentiment * 0.3) + (context_score * 0.3)
        return max(0, min(100, sentiment))

    def calculate_unified_score(
        self,
        technical_score: float = None,
        agi_score: float = None,
        mtf_score: float = None,
        volume_score: float = None,
        sentiment_score: float = None,
        dominance_score: float = 50,
        altcoin_season_index: float = 50,
        eth_gas_score: float = 50,
        symbol: str = "BTC",
        symbol_data: Dict = None,
    ) -> Dict:
        """
        Calculate unified score using regime-adaptive weights with confidence levels
        If scores aren't provided, calculate them from symbol_data
        """
        # Calculate missing scores from symbol_data if needed
        if symbol_data is not None:
            if technical_score is None:
                technical_score = self.calculate_technical_score(
                    momentum_1h=symbol_data.get("change_1h", 0),
                    change_24h=symbol_data.get("change_24h", 0),
                    volatility=symbol_data.get("volatility", 0.05),
                    volume_24h=symbol_data.get("volume_24h", 0),
                )

            if agi_score is None:
                agi_score = self.calculate_agi_score(symbol, symbol_data)

            if mtf_score is None:
                mtf_score = self.calculate_mtf_score(symbol_data)

            if volume_score is None:
                volume_score = self.calculate_volume_score(symbol_data.get("volume_24h", 0))

            if sentiment_score is None:
                sentiment_score = self.calculate_sentiment_score(symbol_data)
        """
        Calculate unified score using regime-adaptive weights with confidence levels
        Returns: {score: float, confidence: float, breakdown: Dict}
        """
        cfg = self.regime_config

        # Base score
        unified = (
            technical_score * cfg.technical_weight
            + agi_score * cfg.agi_weight
            + mtf_score * cfg.mtf_weight
            + volume_score * cfg.volume_weight
            + sentiment_score * cfg.sentiment_weight
        )

        # Market context bonuses/penalties based on symbol type
        context_bonus = 0
        if symbol.lower() != "btc" and symbol.lower() != "eth":
            # Altcoin bonus during altcoin season
            if altcoin_season_index >= 70:
                context_bonus = 10
            elif altcoin_season_index >= 60:
                context_bonus = 5
            elif altcoin_season_index <= 35:
                context_bonus = -5
        elif symbol.lower() == "eth":
            # ETH bonus for healthy network
            if eth_gas_score >= 70:
                context_bonus = 5
            elif eth_gas_score <= 35:
                context_bonus = -5

        # Final score with context
        final_score = unified + context_bonus
        final_score = max(0, min(100, final_score))

        # Calculate confidence based on score consistency across components
        scores = [technical_score, agi_score, mtf_score, volume_score, sentiment_score]
        score_std = np.std(scores)
        consistency = max(0, min(100, 100 - (score_std * 2)))  # Lower std = higher consistency

        # Calculate weight-based confidence
        weight_consistency = 0
        for score, weight in zip(
            scores,
            [
                cfg.technical_weight,
                cfg.agi_weight,
                cfg.mtf_weight,
                cfg.volume_weight,
                cfg.sentiment_weight,
            ],
        ):
            weight_consistency += (score / 100) * weight

        # Overall confidence
        confidence = (consistency * 0.6) + (weight_consistency * 40)  # 0-100 scale
        confidence = max(0, min(100, confidence))

        # Score breakdown
        breakdown = {
            "technical": {"score": technical_score, "weight": cfg.technical_weight},
            "agi": {"score": agi_score, "weight": cfg.agi_weight},
            "mtf": {"score": mtf_score, "weight": cfg.mtf_weight},
            "volume": {"score": volume_score, "weight": cfg.volume_weight},
            "sentiment": {"score": sentiment_score, "weight": cfg.sentiment_weight},
        }

        return {
            "score": round(final_score, 2),
            "confidence": round(confidence, 2),
            "breakdown": breakdown,
            "regime": self.regime,
        }

    def calculate_mtf_score(self, symbol_data: Dict) -> float:
        """Calculate multi-timeframe score based on trend consistency across timeframes"""
        score = 50

        # Check trend consistency
        timeframes = ["1m", "5m", "15m", "1h"]
        bullish_count = 0
        bearish_count = 0

        for tf in timeframes:
            tf_key = f"{tf}_trend"
            if tf_key in symbol_data:
                trend = symbol_data[tf_key].lower()
                if "bull" in trend:
                    bullish_count += 1
                elif "bear" in trend:
                    bearish_count += 1

        trend_consistency = abs(bullish_count - bearish_count) / len(timeframes)
        score += trend_consistency * 30

        # Trend strength
        if bullish_count == len(timeframes):
            score += 20
        elif bearish_count == len(timeframes):
            score -= 20

        return max(0, min(100, score))

    def calculate_volume_score(self, volume_24h: float) -> float:
        """Calculate volume score based on 24h trading volume"""
        if volume_24h >= 10000000:
            return 95
        elif volume_24h >= 5000000:
            return 90
        elif volume_24h >= 1000000:
            return 85
        elif volume_24h >= 500000:
            return 80
        elif volume_24h >= 100000:
            return 75
        elif volume_24h >= 50000:
            return 70
        elif volume_24h >= 10000:
            return 65
        elif volume_24h >= 5000:
            return 60
        elif volume_24h >= 1000:
            return 55
        else:
            return 50

    def calculate_sentiment_score(self, symbol_data: Dict) -> float:
        """Calculate sentiment score from symbol data"""
        sentiment = symbol_data.get("sentiment", {})
        return sentiment.get("score", 50)

    def calculate_unified_score_from_data(self, symbol: str, symbol_data: Dict) -> Dict:
        """Calculate unified score directly from symbol data"""
        return self.calculate_unified_score(
            symbol=symbol,
            symbol_data=symbol_data,
        )

    def calculate_percentile_threshold(
        self,
        all_scores: List[float],
        config_percentile: int = None,
    ) -> float:
        """
        Calculate adaptive threshold based on score distribution
        Returns the score at the configured percentile
        """
        if not all_scores:
            return 55.0  # Default fallback

        if config_percentile is None:
            config_percentile = self.regime_config.min_threshold_percentile

        percentile_score = np.percentile(all_scores, config_percentile)
        return float(percentile_score)

    def select_symbols(
        self,
        scored_symbols: Dict[str, Dict],
        max_positions: int = 10,
    ) -> List[Dict]:
        """
        Select top symbols based on unified score and regime-adaptive thresholds
        Considers both score and confidence
        """
        if not scored_symbols:
            return []

        # Extract all scores for percentile calculation
        all_scores = [
            s.get("score", 50) if isinstance(s, dict) else 50 for s in scored_symbols.values()
        ]
        threshold = self.calculate_percentile_threshold(all_scores)

        # Filter by threshold and sort
        candidates = [
            {"symbol": sym, **data}
            for sym, data in scored_symbols.items()
            if isinstance(data, dict) and data.get("score", 0) >= threshold
        ]

        # Sort by score * confidence descending (better combination of score and reliability)
        candidates.sort(
            key=lambda x: (x.get("score", 0) * x.get("confidence", 50) / 100), reverse=True
        )

        return candidates[:max_positions]

    def get_score_thresholds(self, score: float, confidence: float = 50) -> Dict:
        """Get tier label for a score with confidence adjustment"""
        # Adjust score by confidence
        adjusted_score = score * (confidence / 100)

        if adjusted_score >= 95:
            return {"tier": "GOD_TIER", "multiplier": 5.0, "label": "GOD TIER"}
        elif adjusted_score >= 90:
            return {
                "tier": "HIGH_CONFIDENCE",
                "multiplier": 4.0,
                "label": "HIGH CONFIDENCE",
            }
        elif adjusted_score >= 85:
            return {"tier": "STRONG_SETUP", "multiplier": 3.0, "label": "STRONG SETUP"}
        elif adjusted_score >= 80:
            return {"tier": "GOOD_SETUP", "multiplier": 2.0, "label": "GOOD SETUP"}
        elif adjusted_score >= 75:
            return {"tier": "STANDARD", "multiplier": 1.5, "label": "STANDARD"}
        elif adjusted_score >= 70:
            return {"tier": "CONSERVATIVE", "multiplier": 1.0, "label": "CONSERVATIVE"}
        else:
            return {"tier": "BELOW_THRESHOLD", "multiplier": 0.5, "label": "WEAK"}


# Global instance
unified_scorer = UnifiedScorer()
