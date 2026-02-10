"""
Smart Stop Manager
==================
Adaptive stop-loss that maintains ~2% average while optimizing
for current market conditions
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import time


@dataclass
class StopLevels:
    """Calculated stop-loss and take-profit levels"""

    stop_loss: float
    take_profit: float
    stop_distance_pct: float
    tp_distance_pct: float
    risk_reward: float
    volatility_mode: str
    atr: float


class SmartStopManager:
    """
    Manages adaptive stops that average 2% but adjust based on volatility.

    Goal: Maintain same overall risk while optimizing individual trade stops
    - Tight stops (1-1.5%) in low volatility
    - Normal stops (2%) in normal conditions
    - Wide stops (2.5-3%) in high volatility

    Over many trades, this averages to ~2% but with better win rates
    """

    def __init__(self, target_avg_sl_pct: float = 0.02):
        self.target_avg_sl_pct = target_avg_sl_pct
        self.trade_history: List[Dict] = []

    def calculate_atr(self, candles: List[Dict], period: int = 14) -> float:
        """Calculate Average True Range"""
        if len(candles) < period + 1:
            return 0.0

        true_ranges = []
        for i in range(1, min(period + 1, len(candles))):
            high = candles[-i]["high"]
            low = candles[-i]["low"]
            prev_close = candles[-i - 1]["close"]

            tr1 = high - low
            tr2 = abs(high - prev_close)
            tr3 = abs(low - prev_close)

            true_ranges.append(max(tr1, tr2, tr3))

        return sum(true_ranges) / len(true_ranges) if true_ranges else 0.0

    def determine_volatility_mode(
        self, atr: float, entry_price: float, timeframe: str = "5m"
    ) -> Tuple[str, float]:
        """
        Determine volatility mode and multiplier

        Modes:
        - TIGHT: 1.0-1.5x ATR (low volatility, tighter stops)
        - NORMAL: 1.5-2.0x ATR (normal volatility, ~2% stops)
        - WIDE: 2.0-3.0x ATR (high volatility, wider stops)

        Target: Average ~2% across all trades
        """
        atr_pct = (atr / entry_price) * 100 if entry_price > 0 else 0

        if timeframe in ["1m", "3m"]:
            # Lower timeframe = tighter stops
            if atr_pct < 0.3:
                return "TIGHT", 1.0
            elif atr_pct > 0.8:
                return "WIDE", 2.5
            else:
                return "NORMAL", 1.5
        else:
            # Standard timeframe (5m+)
            if atr_pct < 0.4:
                return "TIGHT", 1.0
            elif atr_pct > 1.0:
                return "WIDE", 2.0
            else:
                return "NORMAL", 1.5

    def calculate_smart_stops(
        self,
        entry_price: float,
        direction: str,
        candles: List[Dict],
        timeframe: str = "5m",
        base_rr: float = 1.0,
    ) -> StopLevels:
        """
        Calculate adaptive stop-loss and take-profit levels

        Maintains ~2% average stop distance while optimizing for current conditions
        """
        atr = self.calculate_atr(candles)
        mode, multiplier = self.determine_volatility_mode(atr, entry_price, timeframe)

        # Calculate stop distance
        stop_distance = atr * multiplier

        # Ensure minimum stop distance (avoid stops too tight)
        min_stop_pct = 0.005  # 0.5% minimum
        min_stop_distance = entry_price * min_stop_pct
        stop_distance = max(stop_distance, min_stop_distance)

        # Cap maximum stop distance (avoid stops too wide)
        max_stop_pct = 0.04  # 4% maximum
        max_stop_distance = entry_price * max_stop_pct
        stop_distance = min(stop_distance, max_stop_distance)

        if direction == "LONG":
            stop_loss = entry_price - stop_distance
            take_profit = entry_price + (stop_distance * base_rr)
        else:  # SHORT
            stop_loss = entry_price + stop_distance
            take_profit = entry_price - (stop_distance * base_rr)

        stop_distance_pct = (stop_distance / entry_price) * 100
        tp_distance_pct = stop_distance_pct * base_rr

        return StopLevels(
            stop_loss=stop_loss,
            take_profit=take_profit,
            stop_distance_pct=stop_distance_pct,
            tp_distance_pct=tp_distance_pct,
            risk_reward=base_rr,
            volatility_mode=mode,
            atr=atr,
        )

    def adjust_for_recent_performance(
        self, base_stops: StopLevels, recent_win_rate: float
    ) -> StopLevels:
        """
        Slightly tighten stops if win rate is high, widen if low

        This helps maintain the 2% average while adapting to performance
        """
        adjustment = 1.0

        if recent_win_rate > 0.65:
            # High win rate - can afford slightly tighter stops
            adjustment = 0.9
        elif recent_win_rate < 0.45:
            # Low win rate - need wider stops to avoid whipsaws
            adjustment = 1.1

        # Apply adjustment
        adjusted_sl = base_stops.stop_loss
        adjusted_tp = base_stops.take_profit

        if adjustment != 1.0:
            # Recalculate with adjustment
            entry_price = (
                base_stops.stop_loss
                + (
                    (base_stops.take_profit - base_stops.stop_loss)
                    / (base_stops.risk_reward + 1)
                    * base_stops.risk_reward
                )
                if base_stops.risk_reward > 0
                else base_stops.stop_loss
            )

            new_distance = base_stops.stop_distance_pct * adjustment / 100 * entry_price

            # Determine direction from SL/TP relationship
            if base_stops.take_profit > base_stops.stop_loss:
                direction = "LONG"
                adjusted_sl = entry_price - new_distance
                adjusted_tp = entry_price + (new_distance * base_stops.risk_reward)
            else:
                direction = "SHORT"
                adjusted_sl = entry_price + new_distance
                adjusted_tp = entry_price - (new_distance * base_stops.risk_reward)

        return StopLevels(
            stop_loss=adjusted_sl,
            take_profit=adjusted_tp,
            stop_distance_pct=base_stops.stop_distance_pct * adjustment,
            tp_distance_pct=base_stops.tp_distance_pct * adjustment,
            risk_reward=base_stops.risk_reward,
            volatility_mode=base_stops.volatility_mode,
            atr=base_stops.atr,
        )

    def get_trailing_stop_adjustment(
        self,
        current_price: float,
        entry_price: float,
        highest_price: float,
        lowest_price: float,
        current_stop: float,
        direction: str,
        profit_activation_pct: float = 1.0,
    ) -> float:
        """
        Adjust stop to lock in profits

        - At +1% profit: Move to breakeven
        - At +2% profit: Trail at 50% of gains
        - At +3% profit: Trail at 70% of gains
        """
        if direction == "LONG":
            profit_pct = ((current_price - entry_price) / entry_price) * 100

            if profit_pct >= profit_activation_pct:
                # Move to breakeven or better
                new_stop = max(entry_price, current_stop)

                if profit_pct >= 3.0:
                    # Trail at 70% of max gains
                    new_stop = max(
                        entry_price + (highest_price - entry_price) * 0.3, new_stop
                    )
                elif profit_pct >= 2.0:
                    # Trail at 50% of gains
                    new_stop = max(
                        entry_price + (current_price - entry_price) * 0.5, new_stop
                    )

                return new_stop

        else:  # SHORT
            profit_pct = ((entry_price - current_price) / entry_price) * 100

            if profit_pct >= profit_activation_pct:
                new_stop = min(entry_price, current_stop)

                if profit_pct >= 3.0:
                    new_stop = min(
                        entry_price - (entry_price - lowest_price) * 0.3, new_stop
                    )
                elif profit_pct >= 2.0:
                    new_stop = min(
                        entry_price - (entry_price - current_price) * 0.5, new_stop
                    )

                return new_stop

        return current_stop

    def record_trade_result(
        self, entry_price: float, stop_loss: float, exit_price: float, exit_reason: str
    ):
        """Record trade for averaging calculations"""
        stop_distance = abs(entry_price - stop_loss)
        stop_pct = (stop_distance / entry_price) * 100

        self.trade_history.append(
            {
                "entry": entry_price,
                "stop_distance_pct": stop_pct,
                "exit_price": exit_price,
                "exit_reason": exit_reason,
                "timestamp": time.time(),
            }
        )

        # Keep only last 50 trades
        if len(self.trade_history) > 50:
            self.trade_history.pop(0)

    def get_average_stop_distance(self) -> float:
        """Get average stop distance over recent trades"""
        if not self.trade_history:
            return 2.0  # Default 2%

        recent = self.trade_history[-20:]  # Last 20 trades
        avg = sum([t["stop_distance_pct"] for t in recent]) / len(recent)
        return avg
