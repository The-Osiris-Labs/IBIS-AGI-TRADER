"""
Liquidity Grab Detector
========================
Identifies stop hunts and liquidity sweeps that reverse
Based on Smart Money Concepts (SMC)
"""

from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
import time


@dataclass
class LiquiditySignal:
    """Liquidity grab detection signal"""

    grab_type: str  # 'BULLISH_GRAB', 'BEARISH_GRAB', 'NO_GRAB'
    level: Optional[float]  # Price level of liquidity sweep
    strength: float  # 0.0 to 1.0
    wick_ratio: float  # Wick-to-body ratio
    volume_confirmation: bool
    timestamp: float


class LiquidityGrabDetector:
    """
    Detects liquidity grabs (fake breakouts) where price sweeps
    previous highs/lows then immediately reverses
    """

    def __init__(self, lookback_candles: int = 20):
        self.lookback_candles = lookback_candles
        self.signals: List[LiquiditySignal] = []

    def find_recent_extremes(
        self, candles: List[Dict], periods: int = 5
    ) -> Tuple[List[float], List[float]]:
        """
        Find recent swing highs and lows

        Returns:
            (list_of_recent_highs, list_of_recent_lows)
        """
        if len(candles) < periods + 2:
            return [], []

        highs = []
        lows = []

        for i in range(2, min(periods + 2, len(candles))):
            # Check for swing high
            if (
                candles[-i]["high"] > candles[-i - 1]["high"]
                and candles[-i]["high"] > candles[-i + 1]["high"]
            ):
                highs.append(candles[-i]["high"])

            # Check for swing low
            if (
                candles[-i]["low"] < candles[-i - 1]["low"]
                and candles[-i]["low"] < candles[-i + 1]["low"]
            ):
                lows.append(candles[-i]["low"])

        return highs, lows

    def detect_liquidity_grab(
        self,
        candles: List[Dict],
        min_wick_ratio: float = 2.0,
        volume_threshold: float = 1.5,
    ) -> LiquiditySignal:
        """
        Detect if current candle is a liquidity grab

        Args:
            candles: List of candle data with 'high', 'low', 'open', 'close', 'volume'
            min_wick_ratio: Minimum wick-to-body ratio for confirmation
            volume_threshold: Volume multiplier vs average

        Returns:
            LiquiditySignal with grab details
        """
        if len(candles) < 10:
            return LiquiditySignal("NO_GRAB", None, 0.0, 0.0, False, time.time())

        current = candles[-1]
        current_price = current["close"]
        current_high = current["high"]
        current_low = current["low"]

        # Calculate candle body and wicks
        body_size = abs(current["close"] - current["open"])
        upper_wick = current_high - max(current["open"], current["close"])
        lower_wick = min(current["open"], current["close"]) - current_low

        if body_size == 0:
            body_size = 0.0001  # Avoid division by zero

        # Find recent extremes
        recent_highs, recent_lows = self.find_recent_extremes(candles)

        # Calculate volume confirmation
        avg_volume = sum([c["volume"] for c in candles[-10:-1]]) / 9
        volume_confirmed = current["volume"] > (avg_volume * volume_threshold)

        # Check for bullish liquidity grab (sweep of lows)
        for low_level in recent_lows[-3:]:  # Check last 3 lows
            if current_low < low_level and current_price > low_level:
                # Swept low but closed above = Bullish Grab
                wick_ratio = lower_wick / body_size

                if wick_ratio >= min_wick_ratio:
                    strength = min(wick_ratio / 3.0, 1.0)  # Cap at 1.0

                    signal = LiquiditySignal(
                        grab_type="BULLISH_GRAB",
                        level=low_level,
                        strength=strength,
                        wick_ratio=wick_ratio,
                        volume_confirmation=volume_confirmed,
                        timestamp=time.time(),
                    )
                    self.signals.append(signal)
                    return signal

        # Check for bearish liquidity grab (sweep of highs)
        for high_level in recent_highs[-3:]:  # Check last 3 highs
            if current_high > high_level and current_price < high_level:
                # Swept high but closed below = Bearish Grab
                wick_ratio = upper_wick / body_size

                if wick_ratio >= min_wick_ratio:
                    strength = min(wick_ratio / 3.0, 1.0)

                    signal = LiquiditySignal(
                        grab_type="BEARISH_GRAB",
                        level=high_level,
                        strength=strength,
                        wick_ratio=wick_ratio,
                        volume_confirmation=volume_confirmed,
                        timestamp=time.time(),
                    )
                    self.signals.append(signal)
                    return signal

        return LiquiditySignal("NO_GRAB", None, 0.0, 0.0, False, time.time())

    def calculate_reversal_strength(
        self, signal: LiquiditySignal, candles: List[Dict]
    ) -> float:
        """
        Calculate how strong the reversal is

        Factors:
        - Wick ratio (longer = stronger)
        - Volume confirmation (higher = stronger)
        - Close position (near opposite end = stronger)
        - Follow-through (next candle confirms = strongest)
        """
        if signal.grab_type == "NO_GRAB":
            return 0.0

        strength = signal.strength

        # Volume boost
        if signal.volume_confirmation:
            strength *= 1.2

        # Check for follow-through if we have enough candles
        if len(candles) >= 2 and signal.grab_type in ["BULLISH_GRAB", "BEARISH_GRAB"]:
            next_candle = candles[-1]
            prev_candle = candles[-2]

            if signal.grab_type == "BULLISH_GRAB":
                # Next candle should be bullish
                if next_candle["close"] > next_candle["open"]:
                    strength *= 1.3
            else:  # BEARISH_GRAB
                # Next candle should be bearish
                if next_candle["close"] < next_candle["open"]:
                    strength *= 1.3

        return min(strength, 1.0)

    def calculate_score(self) -> int:
        """
        Calculate entry score contribution (0-20 points)

        Scoring:
        - Strong grab + volume + reversal: 20 points
        - Moderate grab: 10 points
        - Weak/no grab: 0 points
        """
        if not self.signals:
            return 0

        signal = self.signals[-1]

        if signal.grab_type == "NO_GRAB":
            return 0

        if signal.strength >= 0.7 and signal.volume_confirmation:
            return 20
        elif signal.strength >= 0.5:
            return 10
        elif signal.strength >= 0.3:
            return 5

        return 0

    def get_optimal_entry_level(
        self, signal: LiquiditySignal, candles: List[Dict]
    ) -> Optional[float]:
        """
        Calculate optimal entry level (50% retracement of the grab)

        Returns price level for entry
        """
        if signal.grab_type == "NO_GRAB" or not signal.level:
            return None

        current = candles[-1]

        if signal.grab_type == "BULLISH_GRAB":
            # Entry at 50% between sweep low and close
            entry = (current["low"] + current["close"]) / 2
        else:  # BEARISH_GRAB
            # Entry at 50% between sweep high and close
            entry = (current["high"] + current["close"]) / 2

        return entry
