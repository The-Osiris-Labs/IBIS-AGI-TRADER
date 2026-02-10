"""
Order Flow Imbalance (OFI) Calculator
======================================
Detects aggressive buying/selling pressure before price reflects it
"""

from typing import Dict, List, Tuple
from dataclasses import dataclass
import time


@dataclass
class OFISignal:
    """Order Flow Imbalance Signal"""

    imbalance: float  # -1.0 to 1.0
    direction: str  # 'BUY', 'SELL', 'NEUTRAL'
    strength: float  # 0.0 to 1.0
    bid_volume: float
    ask_volume: float
    timestamp: float


class OrderFlowImbalance:
    """
    Calculates Order Flow Imbalance using Level II order book data

    Formula: OFI = (Bid Vol - Ask Vol) / (Bid Vol + Ask Vol) weighted by trade flow

    Positive OFI = Buying pressure (price likely to rise)
    Negative OFI = Selling pressure (price likely to fall)
    """

    def __init__(self, lookback_periods: int = 5):
        self.lookback_periods = lookback_periods
        self.history: List[OFISignal] = []

    def calculate_imbalance(
        self, order_book: Dict, recent_trades: List[Dict] = None
    ) -> OFISignal:
        """
        Calculate OFI from order book and recent trades

        Args:
            order_book: {'bids': [(price, vol), ...], 'asks': [(price, vol), ...]}
            recent_trades: List of recent trades with 'side' and 'volume'

        Returns:
            OFISignal with imbalance, direction, and strength
        """
        # Calculate Static Order Book Imbalance (SOBI)
        bid_volume = sum([level[1] for level in order_book.get("bids", [])[:5]])
        ask_volume = sum([level[1] for level in order_book.get("asks", [])[:5]])

        total_volume = bid_volume + ask_volume
        if total_volume == 0:
            return OFISignal(0.0, "NEUTRAL", 0.0, 0.0, 0.0, time.time())

        sobi = (bid_volume - ask_volume) / total_volume

        # Calculate Trade Flow Imbalance (TFI)
        if recent_trades:
            buy_flow = sum(
                [t["volume"] for t in recent_trades if t.get("side") == "buy"]
            )
            sell_flow = sum(
                [t["volume"] for t in recent_trades if t.get("side") == "sell"]
            )
            total_flow = buy_flow + sell_flow

            if total_flow > 0:
                tfi = (buy_flow - sell_flow) / total_flow
                # Weight SOBI 60%, TFI 40%
                ofi = (sobi * 0.6) + (tfi * 0.4)
            else:
                ofi = sobi
        else:
            ofi = sobi

        # Determine direction and strength
        if ofi > 0.3:
            direction = "BUY"
            strength = min(abs(ofi), 1.0)
        elif ofi < -0.3:
            direction = "SELL"
            strength = min(abs(ofi), 1.0)
        else:
            direction = "NEUTRAL"
            strength = abs(ofi)

        signal = OFISignal(
            imbalance=ofi,
            direction=direction,
            strength=strength,
            bid_volume=bid_volume,
            ask_volume=ask_volume,
            timestamp=time.time(),
        )

        self.history.append(signal)
        if len(self.history) > self.lookback_periods:
            self.history.pop(0)

        return signal

    def get_smoothed_imbalance(self, periods: int = 3) -> float:
        """Get EMA-smoothed imbalance over recent periods"""
        if len(self.history) < periods:
            return 0.0

        recent = self.history[-periods:]
        values = [s.imbalance for s in recent]

        # Simple EMA
        ema = values[0]
        multiplier = 2 / (periods + 1)
        for value in values[1:]:
            ema = (value - ema) * multiplier + ema

        return ema

    def is_trending(self, threshold: float = 0.4) -> Tuple[bool, str]:
        """Check if OFI is trending strongly in one direction"""
        if len(self.history) < 2:
            return False, "NEUTRAL"

        current = self.history[-1].imbalance
        previous = self.history[-2].imbalance

        # Check for momentum continuation
        if current > threshold and previous > threshold * 0.5:
            return True, "BUY"
        elif current < -threshold and previous < -threshold * 0.5:
            return True, "SELL"

        return False, "NEUTRAL"

    def calculate_score(self, threshold: float = 0.3) -> int:
        """
        Calculate entry score contribution (0-25 points)

        Scoring:
        - |OFI| > 0.5: 25 points (strong signal)
        - |OFI| > 0.3: 15 points (moderate signal)
        - |OFI| > 0.1: 5 points (weak signal)
        - Otherwise: 0 points
        """
        if not self.history:
            return 0

        current = abs(self.history[-1].imbalance)

        if current > 0.5:
            return 25
        elif current > 0.3:
            return 15
        elif current > 0.1:
            return 5
        return 0
