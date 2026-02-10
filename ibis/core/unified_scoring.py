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

    def __init__(self):
        self.score_history: List[float] = []
        self.volatility_history: List[float] = []
        self.regime = "VOLATILE"
        self.regime_config = REGIME_CONFIGS["VOLATILE"]

    def update_regime(self, regime: str):
        """Update regime and weights"""
        self.regime = regime.upper()
        self.regime_config = REGIME_CONFIGS.get(self.regime, REGIME_CONFIGS["NEUTRAL"])

    def calculate_technical_score(
        self,
        momentum_1h: float,
        change_24h: float,
        volatility: float,
        volume_24h: float,
        min_volume: float = 100000,
        max_volume: float = 50000000,
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
        if volume_24h > 0:
            vol_ratio = min(volume_24h / min_volume, max_volume / min_volume)
            volume_score = min(vol_ratio * 50, 100) * 0.2  # Max 20 points
        else:
            volume_score = 0

        base_score = 50 + momentum_score + change_score + vol_score + volume_score
        return max(0, min(100, base_score))

    def calculate_agi_score(
        self, agi_confidence: float, agi_reasoning: str = ""
    ) -> float:
        """
        Calculate AGI score from enhanced brain
        Returns confidence score (0-100)
        """
        return max(0, min(100, agi_confidence))

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
    ) -> float:
        """
        Calculate sentiment score (0-100)
        Based on Fear & Greed index and symbol-specific sentiment
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

        # Blend with symbol sentiment
        sentiment = (fg_score * 0.6) + (symbol_sentiment * 0.4)
        return max(0, min(100, sentiment))

    def calculate_unified_score(
        self,
        technical_score: float,
        agi_score: float,
        mtf_score: float,
        volume_score: float,
        sentiment_score: float,
    ) -> float:
        """
        Calculate unified score using regime-adaptive weights
        """
        cfg = self.regime_config

        unified = (
            technical_score * cfg.technical_weight
            + agi_score * cfg.agi_weight
            + mtf_score * cfg.mtf_weight
            + volume_score * cfg.volume_weight
            + sentiment_score * cfg.sentiment_weight
        )

        return max(0, min(100, unified))

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
        """
        if not scored_symbols:
            return []

        # Extract all scores for percentile calculation
        all_scores = [s.get("unified_score", 50) for s in scored_symbols.values()]
        threshold = self.calculate_percentile_threshold(all_scores)

        # Filter by threshold and sort
        candidates = [
            {"symbol": sym, **data}
            for sym, data in scored_symbols.items()
            if data.get("unified_score", 0) >= threshold
        ]

        # Sort by score descending
        candidates.sort(key=lambda x: x.get("unified_score", 0), reverse=True)

        return candidates[:max_positions]

    def get_score_thresholds(self, score: float) -> Dict:
        """Get tier label for a score"""
        if score >= 95:
            return {"tier": "GOD_TIER", "multiplier": 4.0, "label": "Exceptional"}
        elif score >= 90:
            return {
                "tier": "HIGH_CONFIDENCE",
                "multiplier": 3.0,
                "label": "High Confidence",
            }
        elif score >= 85:
            return {"tier": "STRONG_SETUP", "multiplier": 2.0, "label": "Strong Buy"}
        elif score >= 80:
            return {"tier": "GOOD_SETUP", "multiplier": 1.5, "label": "Good Buy"}
        elif score >= 70:
            return {"tier": "STANDARD", "multiplier": 1.0, "label": "Standard"}
        else:
            return {"tier": "BELOW_THRESHOLD", "multiplier": 0.5, "label": "Weak"}


# Global instance
unified_scorer = UnifiedScorer()
