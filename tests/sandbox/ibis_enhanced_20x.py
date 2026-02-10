#!/usr/bin/env python3
"""
🦅 IBIS TRUE AGENT - 20X ENHANCED VERSION
==========================================
Major enhancements:
1. Dynamic ATR-based stop loss & trailing stops
2. Full AGI brain integration (6-model consensus)
3. Multi-timeframe analysis (1m, 5m, 15m, 1h, 4h)
4. Confidence-based position sizing
5. Portfolio correlation tracking
6. Regime-specific strategy selection
7. Advanced risk management
8. Real-time performance attribution
9. Intelligent order management
10. Machine learning-ready architecture
"""

import asyncio
import json
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass, field

from ibis.core.trading_constants import TRADING


@dataclass
class EnhancedPosition:
    """Enhanced position with advanced tracking"""

    symbol: str
    quantity: float
    entry_price: float
    current_price: float
    stop_loss: float
    take_profit: float
    trailing_stop: Optional[float] = None
    highest_price: float = 0.0
    mode: str = "ACTIVE"
    regime: str = "unknown"
    strategy: str = "STANDARD"
    confidence: float = 0.5
    risk_reward: float = 0.0
    atr_percent: float = 0.02
    opened: str = field(default_factory=lambda: datetime.now().isoformat())
    order_id: Optional[str] = None
    agi_signal: Optional[Dict] = None
    timeframe_alignment: Dict = field(default_factory=dict)
    correlation_risk: float = 0.0

    def update_trailing_stop(self, current_price: float, atr_percent: float):
        """Update trailing stop based on price movement"""
        if self.highest_price == 0.0:
            self.highest_price = self.entry_price

        if current_price > self.highest_price:
            self.highest_price = current_price
            # Trail stop at 2x ATR below highest price
            new_trailing = self.highest_price * (1 - atr_percent * 2)
            if self.trailing_stop is None or new_trailing > self.trailing_stop:
                self.trailing_stop = new_trailing

        self.current_price = current_price

    def should_exit(self) -> tuple[bool, str]:
        """Check if position should be exited"""
        # Check take profit
        if self.current_price >= self.take_profit:
            return True, "TAKE_PROFIT"

        # Check trailing stop
        if self.trailing_stop and self.current_price <= self.trailing_stop:
            return True, "TRAILING_STOP"

        # Check stop loss
        if self.current_price <= self.stop_loss:
            return True, "STOP_LOSS"

        return False, "HOLD"

    def get_pnl(self) -> Dict:
        """Calculate P&L metrics"""
        pnl_abs = (self.current_price - self.entry_price) * self.quantity
        pnl_pct = ((self.current_price - self.entry_price) / self.entry_price) * 100

        return {
            "pnl_abs": pnl_abs,
            "pnl_pct": pnl_pct,
            "unrealized_pnl": pnl_abs,
            "entry_price": self.entry_price,
            "current_price": self.current_price,
            "highest_price": self.highest_price,
            "quantity": self.quantity,
        }


class EnhancedRiskManager:
    """Advanced risk management with correlation tracking"""

    def __init__(self, config: Dict):
        self.config = config
        self.correlation_matrix = {}
        self.position_history = []
        self.drawdown_tracker = {
            "peak_balance": 0.0,
            "current_drawdown": 0.0,
            "max_drawdown": 0.0,
        }

    def calculate_position_size(
        self,
        symbol: str,
        confidence: float,
        volatility: float,
        available_capital: float,
        current_positions: int,
        score: float = 50,  # New parameter: deep scoring system
    ) -> float:
        """Dynamic position sizing based on confidence, volatility, and deep scoring"""
        # Get configuration from TRADING constants for consistency
        base_pct = self.config.get(
            "base_position_pct", TRADING.POSITION.BASE_POSITION_PCT
        )
        max_pct = self.config.get("max_position_pct", TRADING.POSITION.MAX_POSITION_PCT)

        # 🎯 FULL CAPITAL UTILIZATION FOR EXCEPTIONAL OPPORTUNITIES
        if score >= 100:  # God Tier (100+) - DEPLOY FULL CAPITAL
            base_multiplier = 3.0  # Triple position size
            max_pct = 100.0  # Remove limits for exceptional opportunities
        elif score >= 90:  # High Convergence (90-99) - DEPLOY 75-100%
            base_multiplier = 2.5
            max_pct = 100.0
        elif score >= 80:  # Very Strong (80-89) - DEPLOY 50-75%
            base_multiplier = 2.0
            max_pct = 75.0
        elif score >= 70:  # Strong (70-79) - DEPLOY 30-50%
            base_multiplier = 1.5
            max_pct = 50.0
        elif score >= 60:  # Moderate (60-69) - DEPLOY 20-30%
            base_multiplier = 1.0
            max_pct = 30.0
        else:  # Weak (<60) - DEPLOY 10-20%
            base_multiplier = 0.75
            max_pct = 20.0

        # 🎯 CONFIDENCE SCALING (Secondary)
        confidence_multiplier = 0.5 + (confidence * 1.0)

        # 🎯 VOLATILITY ADJUSTMENT (Risk control)
        if volatility > 0.20:  # Extreme volatility
            volatility_multiplier = 0.3
        elif volatility > 0.15:  # Very high volatility
            volatility_multiplier = 0.5
        elif volatility > 0.10:  # High volatility
            volatility_multiplier = 0.75
        elif volatility > 0.05:  # Moderate volatility
            volatility_multiplier = 0.9
        else:  # Low volatility
            volatility_multiplier = 1.0

        # 🎯 POSITION DIVERSIFICATION (Capital management)
        position_multiplier = 1.0 / (
            1 + current_positions * 0.15
        )  # More aggressive reduction

        # 🎯 FEAR & GREED ADJUSTMENT (Contrarian)
        fg_index = self.config.get("fear_greed_index", 50)
        fg_multiplier = 1.0
        if fg_index <= 20:  # Extreme Fear
            fg_multiplier = 1.3  # Increase size for contrarian opportunities
        elif fg_index >= 80:  # Extreme Greed
            fg_multiplier = 0.7  # Reduce size

        # Calculate final size
        size_pct = (
            base_pct
            * base_multiplier
            * confidence_multiplier
            * volatility_multiplier
            * position_multiplier
            * fg_multiplier
        )
        size_pct = min(size_pct, max_pct)
        size_pct = max(size_pct, 5.0)  # Minimum 5% position size

        position_size = (available_capital * size_pct) / 100

        # Apply maximum position percentage constraint
        max_position_size = (
            available_capital * TRADING.POSITION.MAX_POSITION_PCT
        ) / 100

        # For small available capital, prioritize minimum trade size over percentage limit
        # This ensures we can execute trades when capital is limited
        if (
            available_capital <= 50
        ):  # For small accounts (<= $50), allow larger percentage
            effective_min_size = TRADING.POSITION.MIN_CAPITAL_PER_TRADE
            effective_max_size = min(
                TRADING.POSITION.MAX_CAPITAL_PER_TRADE, available_capital
            )
        else:
            effective_min_size = TRADING.POSITION.MIN_CAPITAL_PER_TRADE
            effective_max_size = min(
                TRADING.POSITION.MAX_CAPITAL_PER_TRADE, max_position_size
            )

        # Apply constraints
        if position_size < effective_min_size:
            position_size = effective_min_size

        if position_size > effective_max_size:
            position_size = effective_max_size

        # Ensure position doesn't exceed available capital
        position_size = min(position_size, available_capital)

        return position_size

    def check_correlation_risk(
        self, new_symbol: str, existing_positions: List[str], price_data: Dict
    ) -> float:
        """Calculate correlation risk for new position"""
        if not existing_positions:
            return 0.0

        # Simplified correlation check
        # In production, use actual price correlation calculation
        correlation_score = 0.0

        for existing in existing_positions:
            # Check if symbols are in same category (simplified)
            if self._are_correlated(new_symbol, existing):
                correlation_score += 0.3

        return min(correlation_score, 1.0)

    def _are_correlated(self, symbol1: str, symbol2: str) -> bool:
        """Simple correlation check (can be enhanced with actual correlation)"""
        # Major pairs that tend to correlate
        btc_related = {"BTC", "BCH", "BTG", "BSV"}
        eth_related = {"ETH", "ETC", "ETHW"}

        if symbol1 in btc_related and symbol2 in btc_related:
            return True
        if symbol1 in eth_related and symbol2 in eth_related:
            return True

        return False

    def update_drawdown(self, current_balance: float):
        """Track drawdown for risk management"""
        if current_balance > self.drawdown_tracker["peak_balance"]:
            self.drawdown_tracker["peak_balance"] = current_balance

        drawdown = (
            (
                (self.drawdown_tracker["peak_balance"] - current_balance)
                / self.drawdown_tracker["peak_balance"]
            )
            if self.drawdown_tracker["peak_balance"] > 0
            else 0
        )

        self.drawdown_tracker["current_drawdown"] = drawdown

        if drawdown > self.drawdown_tracker["max_drawdown"]:
            self.drawdown_tracker["max_drawdown"] = drawdown

        return drawdown

    def should_reduce_risk(self, drawdown: float) -> bool:
        """Determine if risk should be reduced"""
        if drawdown > 0.10:  # 10% drawdown
            return True
        return False

    def should_stop_trading(self, drawdown: float, daily_loss: float) -> bool:
        """Determine if trading should stop"""
        max_daily_loss = self.config.get("max_daily_loss", 0.20)
        max_drawdown = 0.15

        if drawdown > max_drawdown:
            return True
        if daily_loss < -max_daily_loss:
            return True

        return False


class MultiTimeframeAnalyzer:
    """Multi-timeframe analysis for better entries"""

    def __init__(self, client):
        self.client = client
        self.timeframes = {
            "1m": "1min",
            "5m": "5min",
            "15m": "15min",
            "1h": "1hour",
            "4h": "4hour",
        }

    async def analyze_all_timeframes(self, symbol: str, timeout: float = 8.0) -> Dict:
        """Analyze symbol across all timeframes with timeout protection"""
        results = {}

        # Use gather for parallel fetching but with timeout protection
        async def safe_analyze(tf_name, tf_code):
            try:
                analysis = await asyncio.wait_for(
                    self._analyze_timeframe(symbol, tf_code, tf_name), timeout=timeout
                )
                return tf_name, analysis
            except asyncio.TimeoutError:
                return tf_name, {"trend": "UNKNOWN", "strength": 0, "error": "timeout"}
            except Exception as e:
                return tf_name, {"trend": "UNKNOWN", "strength": 0, "error": str(e)}

        # Fetch all timeframes in parallel with individual timeouts
        tasks = [safe_analyze(tf, code) for tf, code in self.timeframes.items()]
        completed = await asyncio.gather(*tasks, return_exceptions=True)

        for result in completed:
            if isinstance(result, tuple) and len(result) == 2:
                tf_name, analysis = result
                results[tf_name] = analysis
            else:
                # Handle exception case
                results["unknown"] = {"trend": "UNKNOWN", "strength": 0}

        # Calculate alignment score
        alignment = self._calculate_alignment(results)

        return {
            "timeframes": results,
            "alignment_score": alignment["score"],
            "dominant_trend": alignment["trend"],
            "strength": alignment["strength"],
        }

    async def _analyze_timeframe(self, symbol: str, tf_code: str, tf_name: str) -> Dict:
        """Analyze single timeframe"""
        try:
            # Use reasonable candle count for each timeframe
            candle_count = {
                "1min": 30,
                "5min": 24,
                "15min": 16,
                "1hour": 24,
                "4hour": 12,
            }.get(tf_code, 20)

            candles = await self.client.get_candles(
                f"{symbol}-USDT", tf_code, candle_count
            )

            if not candles:
                return {
                    "trend": "UNKNOWN",
                    "strength": 0,
                    "error": "no_candles",
                    "candle_count": 0,
                }
            if len(candles) < 5:
                return {
                    "trend": "UNKNOWN",
                    "strength": 0,
                    "error": f"insufficient_candles: {len(candles)}",
                    "candle_count": len(candles),
                }

            # Calculate trend
            closes = [float(c.close) for c in candles]

            # Use more candles for SMA calculation
            short_period = min(5, len(closes))
            long_period = min(10, len(closes))

            sma_short = sum(closes[-short_period:]) / short_period
            sma_long = sum(closes[-long_period:]) / long_period

            # Stronger threshold for trend detection
            if sma_short > sma_long * 1.005:
                trend = "BULLISH"
                strength = ((sma_short - sma_long) / sma_long) * 100
            elif sma_short < sma_long * 0.995:
                trend = "BEARISH"
                strength = ((sma_long - sma_short) / sma_long) * 100
            else:
                trend = "NEUTRAL"
                strength = 0

            # Calculate momentum
            momentum = ((closes[-1] - closes[0]) / closes[0]) * 100

            # Calculate volatility (always positive)
            high_low_range = [abs(float(c.high) - float(c.low)) for c in candles[-5:]]
            avg_range = sum(high_low_range) / len(high_low_range)
            volatility = abs(avg_range / closes[-1]) * 100

            return {
                "trend": trend,
                "strength": abs(strength),
                "momentum": momentum,
                "volatility": volatility,
                "sma_short": sma_short,
                "sma_long": sma_long,
                "current_price": closes[-1],
                "candle_count": len(candles),
            }
        except Exception as e:
            return {"trend": "UNKNOWN", "strength": 0, "error": str(e)}

    def _calculate_alignment(self, results: Dict) -> Dict:
        """Calculate timeframe alignment"""
        trends = []
        strengths = []

        for tf_name, data in results.items():
            if "trend" in data and data["trend"] != "UNKNOWN":
                trends.append(data["trend"])
                strengths.append(data.get("strength", 0))

        if not trends:
            return {"score": 0, "trend": "UNKNOWN", "strength": 0}

        # Count trend agreement
        bullish_count = trends.count("BULLISH")
        bearish_count = trends.count("BEARISH")
        neutral_count = trends.count("NEUTRAL")

        total = len(trends)
        non_neutral = bullish_count + bearish_count

        if non_neutral == 0:
            # All neutral
            dominant = "NEUTRAL"
            alignment_score = 50
        elif bullish_count > bearish_count:
            dominant = "BULLISH"
            # Score based on bullish percentage of non-neutral
            alignment_score = (bullish_count / total) * 100
        elif bearish_count > bullish_count:
            dominant = "BEARISH"
            alignment_score = (bearish_count / total) * 100
        else:
            # Equal bullish and bearish (e.g., 2B, 2N, 1Bull, 1Bear)
            dominant = "NEUTRAL"
            alignment_score = 50

        avg_strength = sum(strengths) / len(strengths) if strengths else 0

        return {
            "score": alignment_score,
            "trend": dominant,
            "strength": avg_strength,
            "bullish_count": bullish_count,
            "bearish_count": bearish_count,
            "neutral_count": neutral_count,
        }


class StrategySelector:
    """Regime-specific strategy selection"""

    def __init__(self):
        self.strategies = {
            "FLAT": {
                "name": "Range Scalper",
                "target_pct": 0.20,
                "stop_pct": 0.30,
                "max_positions": float("inf"),
                "scan_interval": 10,
                "description": "Quick scalps in flat markets",
            },
            "TRENDING": {
                "name": "Trend Rider",
                "target_pct": 2.00,
                "stop_pct": 1.50,
                "max_positions": float("inf"),
                "scan_interval": 30,
                "description": "Ride strong trends with wider targets",
            },
            "VOLATILE": {
                "name": "Volatility Hunter",
                "target_pct": 1.50,
                "stop_pct": 2.00,
                "max_positions": float("inf"),
                "scan_interval": 15,
                "description": "Capture volatility with wider stops",
            },
            "NORMAL": {
                "name": "Balanced Trader",
                "target_pct": 0.50,
                "stop_pct": 0.75,
                "max_positions": float("inf"),
                "scan_interval": 20,
                "description": "Standard balanced approach",
            },
            "UNCERTAIN": {
                "name": "Conservative Observer",
                "target_pct": 0.30,
                "stop_pct": 0.50,
                "max_positions": 5,
                "scan_interval": 60,
                "description": "Minimal risk in uncertain conditions",
            },
        }

    def get_strategy(self, regime: str, confidence: float = 0.5) -> Dict:
        """Get optimal strategy for regime - enhanced for full capital utilization"""
        base_strategy = self.strategies.get(regime, self.strategies["NORMAL"])

        # Adjust based on confidence and market conditions
        strategy = base_strategy.copy()

        if confidence > 0.85:  # Very high confidence
            strategy["target_pct"] *= 1.5
            strategy["max_positions"] = float("inf")  # Unlimited positions
        elif confidence > 0.7:  # High confidence
            strategy["target_pct"] *= 1.2
            strategy["max_positions"] = float("inf")  # Unlimited positions
        elif confidence < 0.4:  # Low confidence
            strategy["target_pct"] *= 0.8
            strategy["max_positions"] = max(strategy["max_positions"] - 2, 3)
        else:
            strategy["max_positions"] = float(
                "inf"
            )  # Unlimited positions for normal confidence

        return strategy


class PerformanceTracker:
    """Real-time performance attribution and metrics"""

    def __init__(self):
        self.trades = []
        self.daily_stats = {}
        self.regime_performance = {}
        self.strategy_performance = {}

    def record_trade(self, trade: Dict):
        """Record completed trade"""
        self.trades.append({**trade, "timestamp": datetime.now().isoformat()})

        # Update regime performance
        regime = trade.get("regime", "unknown")
        if regime not in self.regime_performance:
            self.regime_performance[regime] = {
                "trades": 0,
                "wins": 0,
                "losses": 0,
                "total_pnl": 0.0,
            }

        self.regime_performance[regime]["trades"] += 1
        if trade["pnl"] > 0:
            self.regime_performance[regime]["wins"] += 1
        else:
            self.regime_performance[regime]["losses"] += 1
        self.regime_performance[regime]["total_pnl"] += trade["pnl"]

    def get_metrics(self) -> Dict:
        """Get comprehensive performance metrics"""
        if not self.trades:
            return {}

        total_trades = len(self.trades)
        winning_trades = [t for t in self.trades if t["pnl"] > 0]
        losing_trades = [t for t in self.trades if t["pnl"] <= 0]

        win_rate = (len(winning_trades) / total_trades) * 100 if total_trades > 0 else 0

        total_pnl = sum(t["pnl"] for t in self.trades)
        avg_win = (
            sum(t["pnl"] for t in winning_trades) / len(winning_trades)
            if winning_trades
            else 0
        )
        avg_loss = (
            sum(t["pnl"] for t in losing_trades) / len(losing_trades)
            if losing_trades
            else 0
        )

        profit_factor = (
            abs(
                sum(t["pnl"] for t in winning_trades)
                / sum(t["pnl"] for t in losing_trades)
            )
            if losing_trades and sum(t["pnl"] for t in losing_trades) != 0
            else 0
        )

        return {
            "total_trades": total_trades,
            "winning_trades": len(winning_trades),
            "losing_trades": len(losing_trades),
            "win_rate": win_rate,
            "total_pnl": total_pnl,
            "avg_win": avg_win,
            "avg_loss": avg_loss,
            "profit_factor": profit_factor,
            "regime_performance": self.regime_performance,
            "best_regime": max(
                self.regime_performance.items(), key=lambda x: x[1]["total_pnl"]
            )[0]
            if self.regime_performance
            else "unknown",
        }


# Export enhanced classes
__all__ = [
    "EnhancedPosition",
    "EnhancedRiskManager",
    "MultiTimeframeAnalyzer",
    "StrategySelector",
    "PerformanceTracker",
]
