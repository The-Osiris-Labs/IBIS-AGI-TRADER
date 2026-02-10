"""
Entry Optimizer
===============
Waits for optimal entry timing to get better fill prices
WITHOUT changing when trades are taken (just HOW they're entered)
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import time


@dataclass
class EntryTiming:
    """Optimal entry timing recommendation"""

    should_enter: bool
    confidence: float  # 0-1
    suggested_price: Optional[float]
    wait_ms: int  # How long to wait for better entry
    reason: str


class EntryOptimizer:
    """
    Optimizes entry timing to reduce slippage and improve fill prices.

    This does NOT change IF we trade - only WHEN and at what price.
    The system still takes the same trades, just executes them better.
    """

    def __init__(self, max_wait_seconds: float = 5.0):
        self.max_wait_seconds = max_wait_seconds
        self.recent_fills: List[Dict] = []

    def analyze_order_book(self, order_book: Dict, direction: str) -> Dict:
        """
        Analyze order book depth for entry optimization

        Returns:
            {
                'spread_pct': current spread as %,
                'bid_depth': volume within 0.5% of bid,
                'ask_depth': volume within 0.5% of ask,
                'imbalance': bid/ask imbalance (-1 to 1),
                'optimal_side': 'bid' or 'ask' for limit order
            }
        """
        bids = order_book.get("bids", [])
        asks = order_book.get("asks", [])

        if not bids or not asks:
            return {
                "spread_pct": 0.1,
                "bid_depth": 0,
                "ask_depth": 0,
                "imbalance": 0,
                "optimal_side": "ask" if direction == "BUY" else "bid",
            }

        best_bid = (
            bids[0][0] if isinstance(bids[0], (list, tuple)) else bids[0]["price"]
        )
        best_ask = (
            asks[0][0] if isinstance(asks[0], (list, tuple)) else asks[0]["price"]
        )
        mid_price = (best_bid + best_ask) / 2

        spread_pct = ((best_ask - best_bid) / mid_price) * 100

        # Calculate depth within 0.5% of best price
        bid_depth = 0
        for bid in bids[:10]:
            price = bid[0] if isinstance(bid, (list, tuple)) else bid["price"]
            volume = bid[1] if isinstance(bid, (list, tuple)) else bid["volume"]
            if (mid_price - price) / mid_price <= 0.005:
                bid_depth += volume

        ask_depth = 0
        for ask in asks[:10]:
            price = ask[0] if isinstance(ask, (list, tuple)) else ask["price"]
            volume = ask[1] if isinstance(ask, (list, tuple)) else ask["volume"]
            if (price - mid_price) / mid_price <= 0.005:
                ask_depth += volume

        # Calculate imbalance
        total_depth = bid_depth + ask_depth
        imbalance = (bid_depth - ask_depth) / total_depth if total_depth > 0 else 0

        # Determine optimal side for limit order
        if direction == "BUY":
            # For buys, check if we can place limit on bid side
            optimal_side = "bid" if imbalance > 0.1 else "ask"
        else:  # SELL
            optimal_side = "ask" if imbalance < -0.1 else "bid"

        return {
            "spread_pct": spread_pct,
            "bid_depth": bid_depth,
            "ask_depth": ask_depth,
            "imbalance": imbalance,
            "optimal_side": optimal_side,
            "mid_price": mid_price,
            "best_bid": best_bid,
            "best_ask": best_ask,
        }

    def should_wait_for_better_entry(
        self, order_book_analysis: Dict, current_price: float, direction: str
    ) -> EntryTiming:
        """
        Determine if we should wait for a better entry price

        Returns EntryTiming with recommendation
        """
        spread_pct = order_book_analysis["spread_pct"]
        imbalance = order_book_analysis["imbalance"]

        # If spread is tight (< 0.05%), execute immediately
        if spread_pct < 0.05:
            return EntryTiming(
                should_enter=True,
                confidence=0.95,
                suggested_price=current_price,
                wait_ms=0,
                reason="Tight spread, execute now",
            )

        # If spread is moderate (0.05-0.15%), use limit order on favorable side
        if spread_pct < 0.15:
            if direction == "BUY" and imbalance > 0.2:
                # Buying into buying pressure - place limit at bid
                return EntryTiming(
                    should_enter=True,
                    confidence=0.85,
                    suggested_price=order_book_analysis["best_bid"],
                    wait_ms=2000,  # Wait 2 seconds for fill
                    reason="Moderate spread, limit at bid for better fill",
                )
            elif direction == "SELL" and imbalance < -0.2:
                # Selling into selling pressure - place limit at ask
                return EntryTiming(
                    should_enter=True,
                    confidence=0.85,
                    suggested_price=order_book_analysis["best_ask"],
                    wait_ms=2000,
                    reason="Moderate spread, limit at ask for better fill",
                )

        # Wide spread (> 0.15%) - use market order but warn
        return EntryTiming(
            should_enter=True,
            confidence=0.70,
            suggested_price=current_price,
            wait_ms=0,
            reason=f"Wide spread ({spread_pct:.2f}%), market order recommended",
        )

    def calculate_optimal_entry_price(
        self, base_price: float, direction: str, order_book: Dict, volatility_pct: float
    ) -> Tuple[float, str]:
        """
        Calculate optimal entry price based on market conditions

        Returns:
            (optimal_price, order_type)
            order_type: 'market' or 'limit'
        """
        analysis = self.analyze_order_book(order_book, direction)
        spread_pct = analysis["spread_pct"]

        # High volatility - use market order for speed
        if volatility_pct > 1.0:
            return base_price, "market"

        # Tight spread - use market order (little benefit to limit)
        if spread_pct < 0.08:
            return base_price, "market"

        # Moderate spread - use limit order to capture spread
        if direction == "BUY":
            # Try to buy at bid (slightly below mid)
            optimal = analysis["best_bid"] * 1.0002  # Slight buffer
            return optimal, "limit"
        else:  # SELL
            optimal = analysis["best_ask"] * 0.9998
            return optimal, "limit"

    def detect_optimal_moment(
        self, candles_1m: List[Dict], max_wait_seconds: float = 3.0
    ) -> Dict:
        """
        Detect the optimal moment to enter within the next few seconds

        Analyzes momentum to find micro-pullbacks for better entries
        """
        if len(candles_1m) < 3:
            return {"should_enter_now": True, "reason": "Insufficient data"}

        # Calculate micro-momentum (last 3 candles)
        recent_changes = []
        for i in range(1, min(4, len(candles_1m))):
            change = candles_1m[-i]["close"] - candles_1m[-i]["open"]
            recent_changes.append(change)

        avg_change = sum(recent_changes) / len(recent_changes)

        # Check for micro-pullback (temporary reversal)
        if len(recent_changes) >= 2:
            if recent_changes[-1] * recent_changes[-2] < 0:
                # Direction changed - potential pullback
                return {
                    "should_enter_now": True,
                    "reason": "Micro-pullback detected - optimal entry",
                    "confidence": 0.80,
                }

        # Strong momentum - enter immediately
        if abs(avg_change) / candles_1m[-1]["close"] > 0.001:
            return {
                "should_enter_now": True,
                "reason": "Strong momentum - execute now",
                "confidence": 0.85,
            }

        # Neutral conditions - safe to enter
        return {
            "should_enter_now": True,
            "reason": "Neutral conditions - proceed with entry",
            "confidence": 0.75,
        }

    def get_execution_recommendation(
        self,
        symbol: str,
        direction: str,
        target_price: float,
        order_book: Dict,
        candles_1m: List[Dict],
    ) -> Dict:
        """
        Get comprehensive execution recommendation

        This is the main function that provides entry optimization
        without changing the trade decision itself
        """
        # Analyze order book
        ob_analysis = self.analyze_order_book(order_book, direction)

        # Get timing recommendation
        timing = self.should_wait_for_better_entry(ob_analysis, target_price, direction)

        # Get optimal price
        volatility = self._calculate_volatility(candles_1m)
        opt_price, order_type = self.calculate_optimal_entry_price(
            target_price, direction, order_book, volatility
        )

        # Calculate potential price improvement
        if direction == "BUY":
            price_improvement = ((target_price - opt_price) / target_price) * 100
        else:
            price_improvement = ((opt_price - target_price) / target_price) * 100

        return {
            "symbol": symbol,
            "direction": direction,
            "target_price": target_price,
            "suggested_price": opt_price,
            "order_type": order_type,
            "should_wait": timing.wait_ms > 0,
            "wait_ms": timing.wait_ms,
            "confidence": timing.confidence,
            "reason": timing.reason,
            "spread_pct": ob_analysis["spread_pct"],
            "price_improvement_pct": price_improvement,
            "order_book_imbalance": ob_analysis["imbalance"],
        }

    def _calculate_volatility(self, candles: List[Dict], periods: int = 10) -> float:
        """Calculate recent volatility as percentage"""
        if len(candles) < periods:
            return 0.5  # Default moderate volatility

        changes = []
        for i in range(1, periods + 1):
            if candles[-i]["close"] > 0:
                pct_change = (
                    abs(
                        (candles[-i]["close"] - candles[-i]["open"])
                        / candles[-i]["close"]
                    )
                    * 100
                )
                changes.append(pct_change)

        return sum(changes) / len(changes) if changes else 0.5
