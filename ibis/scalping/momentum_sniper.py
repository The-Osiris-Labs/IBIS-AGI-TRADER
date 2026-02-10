"""
Momentum Sniper
===============
Captures momentum explosions on low timeframes using velocity and acceleration
"""

from typing import Dict, List
from dataclasses import dataclass
import time


@dataclass
class MomentumMetrics:
    """Multi-timeframe momentum metrics"""

    velocity_1m: float  # Price change per minute
    acceleration: float  # Change in velocity
    alignment_score: float  # 0-100, how aligned timeframes are
    volume_surge: float  # Volume vs average
    direction: int  # 1 for up, -1 for down, 0 for neutral
    timestamp: float


class MomentumSnipper:
    """
    Detects and snipes momentum explosions using:
    - Velocity (speed of price change)
    - Acceleration (increasing/decreasing velocity)
    - Multi-timeframe alignment
    - Volume confirmation
    """

    def __init__(self):
        self.history: List[MomentumMetrics] = []
        self.max_history = 50

    def calculate_velocity(self, candles: List[Dict], periods: int = 3) -> float:
        """
        Calculate price velocity (change per candle)

        Returns average price change over last N candles
        """
        if len(candles) < periods + 1:
            return 0.0

        changes = []
        for i in range(1, periods + 1):
            change = candles[-i]["close"] - candles[-i - 1]["close"]
            changes.append(change)

        avg_change = sum(changes) / len(changes)

        # Normalize to percentage
        if candles[-1]["close"] > 0:
            velocity_pct = (avg_change / candles[-1]["close"]) * 100
        else:
            velocity_pct = 0.0

        return velocity_pct

    def calculate_acceleration(self, candles: List[Dict]) -> float:
        """
        Calculate acceleration (change in velocity)

        Positive = momentum increasing
        Negative = momentum decreasing
        """
        if len(candles) < 5:
            return 0.0

        # Recent velocity (last 2 candles)
        recent_velocity = self.calculate_velocity(candles[-3:], periods=2)

        # Older velocity (candles 3-4)
        if len(candles) >= 5:
            older_velocity = self.calculate_velocity(candles[-5:-2], periods=2)
        else:
            older_velocity = 0.0

        return recent_velocity - older_velocity

    def calculate_timeframe_alignment(
        self,
        candles_1m: List[Dict],
        candles_5m: List[Dict],
        candles_15m: List[Dict] = None,
    ) -> float:
        """
        Calculate how aligned different timeframes are (0-100)

        All timeframes pointing same direction = 100
        Mixed directions = lower score
        """
        trends = []

        # 1M trend (last 3 candles)
        if len(candles_1m) >= 3:
            trend_1m = 1 if candles_1m[-1]["close"] > candles_1m[-3]["open"] else -1
            trends.append(trend_1m)

        # 5M trend (last 3 candles)
        if len(candles_5m) >= 3:
            trend_5m = 1 if candles_5m[-1]["close"] > candles_5m[-3]["open"] else -1
            trends.append(trend_5m)

        # 15M trend if available
        if candles_15m and len(candles_15m) >= 3:
            trend_15m = 1 if candles_15m[-1]["close"] > candles_15m[-3]["open"] else -1
            trends.append(trend_15m)

        if not trends:
            return 0.0

        # Calculate alignment
        if len(trends) == 1:
            return 100.0  # Single timeframe always 100

        # Check how many agree with the most recent (1M)
        recent_trend = trends[0]
        agreements = sum([1 for t in trends if t == recent_trend])

        alignment = (agreements / len(trends)) * 100
        return alignment

    def calculate_volume_surge(self, candles: List[Dict], periods: int = 10) -> float:
        """
        Calculate volume surge vs average

        Returns multiplier (1.0 = average, 2.0 = 2x average)
        """
        if len(candles) < periods + 1:
            return 1.0

        current_volume = candles[-1]["volume"]
        avg_volume = sum([c["volume"] for c in candles[-periods - 1 : -1]]) / periods

        if avg_volume > 0:
            return current_volume / avg_volume
        return 1.0

    def analyze_momentum(
        self,
        candles_1m: List[Dict],
        candles_5m: List[Dict],
        candles_15m: List[Dict] = None,
    ) -> MomentumMetrics:
        """
        Full momentum analysis combining all metrics
        """
        velocity = self.calculate_velocity(candles_1m)
        acceleration = self.calculate_acceleration(candles_1m)
        alignment = self.calculate_timeframe_alignment(
            candles_1m, candles_5m, candles_15m
        )
        volume_surge = self.calculate_volume_surge(candles_1m)

        # Determine direction
        if velocity > 0.05:  # 0.05% positive
            direction = 1
        elif velocity < -0.05:  # 0.05% negative
            direction = -1
        else:
            direction = 0

        metrics = MomentumMetrics(
            velocity_1m=velocity,
            acceleration=acceleration,
            alignment_score=alignment,
            volume_surge=volume_surge,
            direction=direction,
            timestamp=time.time(),
        )

        self.history.append(metrics)
        if len(self.history) > self.max_history:
            self.history.pop(0)

        return metrics

    def should_snipe(
        self,
        metrics: MomentumMetrics,
        min_velocity: float = 0.15,
        min_alignment: float = 80.0,
        min_volume_surge: float = 1.5,
    ) -> tuple:
        """
        Determine if we should snipe this momentum

        Returns:
            (should_trade: bool, reason: str)
        """
        # Check velocity
        if abs(metrics.velocity_1m) < min_velocity:
            return False, f"Velocity {metrics.velocity_1m:.3f}% < {min_velocity}%"

        # Check alignment
        if metrics.alignment_score < min_alignment:
            return False, f"Alignment {metrics.alignment_score:.1f}% < {min_alignment}%"

        # Check volume
        if metrics.volume_surge < min_volume_surge:
            return False, f"Volume {metrics.volume_surge:.2f}x < {min_volume_surge}x"

        # Check acceleration (momentum should be building)
        if metrics.acceleration * metrics.direction < 0:
            return False, "Momentum decelerating"

        return True, "MOMENTUM_EXPLOSION_DETECTED"

    def calculate_score(
        self,
        min_alignment_high: float = 90.0,
        min_alignment_med: float = 75.0,
        min_vol_high: float = 2.0,
        min_vol_med: float = 1.5,
    ) -> int:
        """
        Calculate entry score contribution (0-25 points)

        Scoring:
        - Alignment 90%+ + Volume 2x: 25 points
        - Alignment 75%+ + Volume 1.5x: 15 points
        - Alignment 60%+: 5 points
        """
        if not self.history:
            return 0

        m = self.history[-1]

        # High score
        if m.alignment_score >= min_alignment_high and m.volume_surge >= min_vol_high:
            return 25

        # Medium score
        if m.alignment_score >= min_alignment_med and m.volume_surge >= min_vol_med:
            return 15

        # Low score
        if m.alignment_score >= 60.0:
            return 5

        return 0

    def detect_momentum_reversal(self, lookback: int = 3) -> bool:
        """
        Detect if momentum has reversed recently

        Used for early exit signals
        """
        if len(self.history) < lookback:
            return False

        recent = self.history[-lookback:]

        # Check if direction flipped
        if recent[0].direction != 0 and recent[-1].direction != 0:
            if recent[0].direction != recent[-1].direction:
                return True

        # Check if velocity crossed zero
        if recent[0].velocity_1m * recent[-1].velocity_1m < 0:
            return True

        return False
