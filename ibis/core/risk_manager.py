"""
IBIS Risk Management Framework
Comprehensive risk management for cryptocurrency trading
"""

import math
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import numpy as np
from ibis.core.logging_config import get_logger

logger = get_logger(__name__)


@dataclass
class RiskParams:
    """Risk parameters for position sizing and management"""

    base_risk_per_trade: float = 0.02  # 2% per trade
    max_risk_per_trade: float = 0.05  # 5% max per trade
    portfolio_heat_limit: float = 0.60  # 60% max portfolio exposure
    stop_loss_pct: float = 0.05  # 5% stop loss
    take_profit_pct: float = 0.02  # 2% take profit
    min_position_size: float = 11.0  # $11 minimum
    max_position_size: float = 40.0  # $40 maximum
    risk_reward_ratio: float = 0.4  # 1:2.5 risk-reward

    # Dynamic SL/TP parameters
    atr_multiplier: float = 1.5  # ATR multiplier for SL
    volatility_sl_multiplier: float = 1.0  # Volatility-based SL adjustment
    trailing_stop_activation: float = 0.01  # 1% profit to activate trailing stop
    trailing_stop_distance: float = 0.02  # 2% trailing distance
    min_stop_loss_pct: float = 0.01  # 1% minimum SL
    max_stop_loss_pct: float = 0.10  # 10% maximum SL
    slippage_estimate: float = 0.0005  # 0.05% estimated slippage

    # Enhanced TP parameters
    min_take_profit_pct: float = 0.005  # 0.5% minimum net profit
    volatility_tp_multiplier: float = 0.5  # Volatility-based TP adjustment (0-2)
    trend_tp_multiplier: float = 0.3  # Trend strength-based TP adjustment (0-2)
    tp_levels: List[float] = field(
        default_factory=lambda: [0.3, 0.5, 0.2]
    )  # Partial TP ratios (sum to 1)
    tp_level_multipliers: List[float] = field(
        default_factory=lambda: [0.8, 1.0, 1.3]
    )  # Multipliers for each TP level
    volatility_regime_multipliers: Dict[str, float] = field(
        default_factory=lambda: {
            "VOLATILE": 1.3,
            "STRONG_BULL": 1.25,
            "BULL": 1.15,
            "NORMAL": 1.0,
            "FLAT": 0.9,
            "BEAR": 0.95,
            "STRONG_BEAR": 0.85,
        }
    )


@dataclass
class PositionRisk:
    """Risk assessment for a specific position"""

    symbol: str
    entry_price: float
    quantity: float
    stop_loss: float
    take_profit: float
    risk_amount: float
    reward_amount: float
    risk_reward: float
    position_value: float
    portfolio_exposure: float
    confidence: float
    volatility_score: float
    liquidity_score: float


@dataclass
class PortfolioRisk:
    """Overall portfolio risk assessment"""

    total_value: float
    total_risk: float
    total_exposure: float
    positions_count: int
    max_position_risk: float
    avg_position_risk: float
    risk_concentration: float
    drawdown_risk: float
    volatility_risk: float
    liquidity_risk: float


class RiskManager:
    """Comprehensive risk management system with dynamic fee calculation"""

    def __init__(self, params: RiskParams = None):
        self.params = params or RiskParams()
        # Align with TRADING.RISK parameters
        from ibis.core.trading_constants import TRADING

        self.params.base_risk_per_trade = TRADING.RISK.BASE_RISK_PER_TRADE
        self.params.max_risk_per_trade = TRADING.RISK.MAX_RISK_PER_TRADE
        self.params.stop_loss_pct = TRADING.RISK.STOP_LOSS_PCT
        self.params.take_profit_pct = TRADING.RISK.TAKE_PROFIT_PCT
        self.params.min_take_profit_pct = TRADING.RISK.MIN_PROFIT_BUFFER

        self.position_history: List[Dict] = []
        self.risk_scores: Dict[str, float] = {}
        self.db = None

    def set_database(self, db):
        """Set database instance for fee calculation"""
        self.db = db

    def update_fee_rates(self, days: int = 7):
        """Update fee rates from database and trading constants (last N days)"""
        if self.db:
            # This will ensure TRADING constants are updated with latest fees from DB
            from ibis.core.trading_constants import TRADING

            symbol_fees = self.db.get_average_fees_per_symbol(days)

            for symbol, fees in symbol_fees.items():
                TRADING.EXCHANGE.update_symbol_fees(symbol, fees["maker"], fees["taker"])

            logger.info(
                f"Updated dynamic fees for {len(symbol_fees)} symbols from database (last {days} days)"
            )

    def _get_fee_rates(self, symbol: str, days: int = 7):
        """Get fee rates for symbol, using database if available (last 7 days), fallback to TRADING constants

        Args:
            symbol: Trading symbol
            days: Number of days to look back for fee history

        Returns:
            Dictionary with "maker", "taker", and "count" fields

        Raises:
            ValueError: If days parameter is invalid
        """
        from ibis.core.trading_constants import TRADING

        if days <= 0:
            raise ValueError("Days must be a positive integer")

        # Realistic fee range for major cryptocurrency exchanges (0.01% to 0.1%)
        MIN_FEE_RATE = 0.0001  # 0.01%
        MAX_FEE_RATE = 0.001  # 0.1%

        if self.db:
            try:
                db_fees = self.db.get_average_fee_rate(symbol, days)
                if db_fees["count"] > 0:
                    # Validate fee rates - clamp to realistic range (0.01% to 0.1%)
                    valid_maker = max(MIN_FEE_RATE, min(MAX_FEE_RATE, db_fees["maker"]))
                    valid_taker = max(MIN_FEE_RATE, min(MAX_FEE_RATE, db_fees["taker"]))
                    if valid_maker != db_fees["maker"] or valid_taker != db_fees["taker"]:
                        logger.warning(
                            f"Invalid fee rates for {symbol}: maker={db_fees['maker']:.4f}, taker={db_fees['taker']:.4f} - clamped to valid range ({MIN_FEE_RATE:.4f} to {MAX_FEE_RATE:.4f})"
                        )
                    logger.debug(
                        f"Using database fee rates for {symbol}: maker={valid_maker:.4f}, taker={valid_taker:.4f} (count={db_fees['count']})"
                    )
                    return {
                        "maker": valid_maker,
                        "taker": valid_taker,
                        "count": db_fees["count"],
                    }
            except Exception as e:
                logger.error(f"Failed to get fee rates from database: {e}")

        # Fall back to TRADING constants (which may have dynamic rates)
        try:
            maker_fee = TRADING.EXCHANGE.get_maker_fee(symbol)
            taker_fee = TRADING.EXCHANGE.get_taker_fee(symbol)
            # Also validate TRADING constants
            valid_maker = max(MIN_FEE_RATE, min(MAX_FEE_RATE, maker_fee))
            valid_taker = max(MIN_FEE_RATE, min(MAX_FEE_RATE, taker_fee))
            if valid_maker != maker_fee or valid_taker != taker_fee:
                logger.warning(
                    f"Invalid TRADING fee rates for {symbol}: maker={maker_fee:.4f}, taker={taker_fee:.4f} - clamped to valid range ({MIN_FEE_RATE:.4f} to {MAX_FEE_RATE:.4f})"
                )
            logger.debug(
                f"Using TRADING fee rates for {symbol}: maker={valid_maker:.4f}, taker={valid_taker:.4f}"
            )
            return {
                "maker": valid_maker,
                "taker": valid_taker,
                "count": 0,
            }
        except Exception as e:
            logger.error(f"Failed to get TRADING fee rates: {e}")
            return {
                "maker": 0.0010,
                "taker": 0.0010,
                "count": 0,
            }

    def calculate_position_size(
        self,
        account_balance: float,
        entry_price: float,
        stop_loss_price: float,
        confidence: float = 0.5,
        volatility: float = 0.05,
        liquidity: float = 0.5,
    ) -> Tuple[float, float, float]:
        """
        Calculate optimal position size based on risk parameters

        Returns: (quantity, position_value, risk_amount)
        """
        # Calculate position size based on risk per trade
        risk_per_trade = account_balance * self.params.base_risk_per_trade

        # Adjust for confidence and volatility (more conservative multipliers)
        confidence_multiplier = 0.7 + (confidence * 0.8)  # 0.7 to 1.5
        volatility_multiplier = max(0.6, min(1.5, 1 / (volatility * 100)))  # Inverse of volatility
        liquidity_multiplier = 0.6 + (liquidity * 0.4)  # 0.6 to 1.0

        adjusted_risk = (
            risk_per_trade * confidence_multiplier * volatility_multiplier * liquidity_multiplier
        )
        adjusted_risk = max(0, min(account_balance * self.params.max_risk_per_trade, adjusted_risk))

        # Calculate position size based on risk amount and stop loss distance
        risk_per_unit = entry_price - stop_loss_price
        if risk_per_unit <= 0:
            # If no valid stop loss, use fixed position size
            position_value = min(
                self.params.max_position_size,
                max(self.params.min_position_size, account_balance * 0.01),  # More conservative
            )
            quantity = position_value / entry_price
        else:
            quantity = adjusted_risk / risk_per_unit
            position_value = quantity * entry_price

            # Ensure position size is within limits
            if position_value < self.params.min_position_size:
                position_value = self.params.min_position_size
                quantity = position_value / entry_price
            elif position_value > self.params.max_position_size:
                position_value = self.params.max_position_size
                quantity = position_value / entry_price

        # Additional validation: Ensure position size is not too large for volatility
        max_position_value = account_balance * 0.02  # Max 2% of account per trade
        if position_value > max_position_value:
            position_value = max_position_value
            quantity = position_value / entry_price

        return quantity, position_value, min(adjusted_risk, position_value)

    def calculate_stop_loss(
        self,
        entry_price: float,
        volatility: float,
        atr: float,
        support_level: float = None,
        trend_strength: float = 0.5,
        symbol: str = None,
        market_regime: str = "NORMAL",
        price_history: List[float] = None,
    ) -> float:
        """
        Calculate dynamic stop loss based on volatility, market conditions, and recent price action, accounting for fees and slippage

        Args:
            entry_price: Entry price
            volatility: Price volatility (0-1)
            atr: Average True Range
            support_level: Recent support level
            trend_strength: Trend strength (-1 to 1, negative = bearish)
            symbol: Trading symbol for fee calculation
            market_regime: Current market regime (VOLATILE, NORMAL, etc.)
            price_history: Recent price history for additional analysis

        Returns: Stop loss price
        """
        # Base stop loss percentage from config
        base_sl_pct = self.params.stop_loss_pct

        # Volatility adjustment
        volatility_multiplier = 1 + (volatility * 0.5)  # Up to 1.5x in high volatility
        adjusted_sl_pct = base_sl_pct * volatility_multiplier

        # Regime adjustment
        regime_multipliers = {
            "VOLATILE": 1.2,
            "STRONG_BULL": 0.8,
            "STRONG_BEAR": 1.3,
            "BULL": 0.9,
            "BEAR": 1.1,
            "NORMAL": 1.0,
            "FLAT": 0.95,
            "UNKNOWN": 1.0,
        }
        regime_multiplier = regime_multipliers.get(market_regime, 1.0)
        adjusted_sl_pct = adjusted_sl_pct * regime_multiplier

        # Trend adjustment
        trend_multiplier = 1.0
        if trend_strength > 0.7:
            trend_multiplier = 0.85  # Tighten in very strong uptrend
        elif trend_strength > 0.5:
            trend_multiplier = 0.95  # Moderately tighten in strong uptrend
        elif trend_strength < -0.7:
            trend_multiplier = 1.3  # Widen in very strong downtrend
        elif trend_strength < -0.5:
            trend_multiplier = 1.15  # Moderately widen in strong downtrend
        adjusted_sl_pct = adjusted_sl_pct * trend_multiplier

        # Calculate initial stop loss
        stop_loss = entry_price * (1 - adjusted_sl_pct)

        # Support level adjustment
        if support_level and support_level < entry_price:
            # Place stop loss slightly below support with volatility-based buffer
            buffer = 0.005 + (volatility * 0.005)  # 0.5-1.0% buffer
            support_sl = support_level * (1 - buffer)
            stop_loss = max(stop_loss, support_sl)  # Keep stop loss above support buffer

        # ATR-based adjustment (for volatility protection)
        atr_sl = entry_price - (atr * 1.5)
        stop_loss = max(stop_loss, atr_sl)  # Ensure stop loss isn't too tight

        # Recent price action adjustment
        if price_history and len(price_history) >= 20:
            recent_lows = sorted(price_history[-20:])
            lowest_low = recent_lows[0]
            action_sl = lowest_low * 0.995  # 0.5% buffer below recent low
            stop_loss = max(stop_loss, action_sl)

        # Fee and slippage adjustment (ensure we account for transaction costs)
        fee_rates = self._get_fee_rates(symbol)
        total_fee_pct = (
            fee_rates["taker"] + fee_rates["taker"]
        )  # Assume taker on both entry and exit
        total_cost_pct = total_fee_pct + self.params.slippage_estimate
        cost_adjustment = entry_price * total_cost_pct
        stop_loss = stop_loss - cost_adjustment

        # Ensure stop loss is within reasonable bounds
        min_sl = entry_price * (1 - self.params.max_stop_loss_pct)
        max_sl = entry_price * (1 - self.params.min_stop_loss_pct)
        stop_loss = max(min_sl, min(max_sl, stop_loss))

        debug_msg = f"Stop loss calculation: Entry={entry_price:.4f}, SL%={adjusted_sl_pct:.2%}"
        if support_level is not None:
            debug_msg += f", Support={support_level:.4f}"
        if atr is not None:
            debug_msg += f", ATR={atr:.4f}"
        debug_msg += f", Final={stop_loss:.4f}"
        logger.debug(debug_msg)

        return stop_loss

    def calculate_trailing_stop(
        self,
        entry_price: float,
        current_price: float,
        highest_price: float,
        volatility: float,
        atr: float,
        symbol: str = None,
        trend_strength: float = 0.5,
        market_regime: str = "NORMAL",
    ) -> Optional[float]:
        """
        Calculate enhanced trailing stop loss based on price movement, volatility, trend strength,
        and market regime that locks in profits while allowing upside potential

        Args:
            entry_price: Entry price
            current_price: Current price
            highest_price: Highest price reached since entry
            volatility: Price volatility (0-1)
            atr: Average True Range
            symbol: Trading symbol for fee calculation
            trend_strength: Trend strength (-1 to 1)
            market_regime: Current market regime (VOLATILE, NORMAL, etc.)

        Returns: Trailing stop price or None if not activated
        """
        # Check if trailing stop should be activated (minimum profit requirement)
        profit_pct = (current_price - entry_price) / entry_price
        if profit_pct < self.params.trailing_stop_activation:
            return None

        # Dynamic trailing stop distance based on volatility, trend, and market regime
        base_distance = self.params.trailing_stop_distance

        # Volatility adjustment
        volatility_multiplier = 1 + (volatility * 0.8)  # Up to 1.8x in high volatility

        # Trend strength adjustment
        trend_multiplier = 1.0
        if trend_strength > 0.7:
            trend_multiplier = 0.8  # Tighter trailing stop in strong uptrend
        elif trend_strength > 0.5:
            trend_multiplier = 0.9  # Slightly tighter in moderate uptrend
        elif trend_strength < -0.7:
            trend_multiplier = 1.3  # Wider trailing stop in strong downtrend
        elif trend_strength < -0.5:
            trend_multiplier = 1.1  # Slightly wider in moderate downtrend

        # Market regime adjustment
        regime_multipliers = {
            "VOLATILE": 1.2,
            "STRONG_BULL": 0.9,
            "BULL": 1.0,
            "NORMAL": 1.0,
            "FLAT": 1.1,
            "BEAR": 1.15,
            "STRONG_BEAR": 1.25,
        }
        regime_multiplier = regime_multipliers.get(market_regime, 1.0)

        # Calculate dynamic distance
        dynamic_distance_pct = (
            base_distance * volatility_multiplier * trend_multiplier * regime_multiplier
        )
        volatility_distance = highest_price * dynamic_distance_pct

        # ATR-based distance (more responsive to current market conditions)
        atr_multiplier = 1.5
        if volatility > 0.08:
            atr_multiplier = 2.0  # Larger ATR multiplier in high volatility
        elif trend_strength > 0.7:
            atr_multiplier = 1.2  # Smaller ATR multiplier in strong trend
        atr_distance = atr * atr_multiplier

        # Use maximum of volatility and ATR-based distance for trailing stop
        trailing_distance = max(volatility_distance, atr_distance)
        trailing_stop = highest_price - trailing_distance

        # Adjust for fees to ensure minimum profit even if stopped out
        fee_rates = self._get_fee_rates(symbol)
        total_fee_pct = fee_rates["taker"] + fee_rates["maker"]
        minimum_profit_price = entry_price * (
            1 + total_fee_pct + self.params.slippage_estimate + self.params.min_take_profit_pct
        )
        trailing_stop = max(trailing_stop, minimum_profit_price)

        # Lock in profits as price increases
        if profit_pct > 0.02:  # If 2% or more profit
            # Adjust trailing stop to lock in at least half the current profit
            min_trailing_stop = entry_price * (1 + profit_pct * 0.5)
            trailing_stop = max(trailing_stop, min_trailing_stop)

        logger.debug(
            f"Trailing stop: Highest={highest_price:.4f}, Distance={trailing_distance:.4f}, "
            f"Stop={trailing_stop:.4f}, Min profit={minimum_profit_price:.4f}, "
            f"Volatility={volatility:.2f}, Trend={trend_strength:.2f}, Regime={market_regime}"
        )

        return trailing_stop

    def calculate_take_profit(
        self,
        entry_price: float,
        stop_loss: float,
        reward_risk_ratio: float = None,
        resistance_level: float = None,
        trend_strength: float = 0.5,
        symbol: str = None,
        market_regime: str = "NORMAL",
        price_history: List[float] = None,
        volatility: float = 0.05,
        return_multiple_levels: bool = True,
    ) -> List[float] or float:
        """
        Calculate optimal take profit levels based on volatility, trend strength, market regime,
        and recent price action, accounting for actual fees, slippage, and dynamic adjustments

        Args:
            entry_price: Entry price
            stop_loss: Stop loss price
            reward_risk_ratio: Desired reward-risk ratio
            resistance_level: Recent resistance level
            trend_strength: Trend strength (-1 to 1)
            symbol: Trading symbol for fee calculation
            market_regime: Current market regime (VOLATILE, NORMAL, etc.)
            price_history: Recent price history for additional analysis
            volatility: Price volatility (0-1)
            return_multiple_levels: Whether to return multiple TP levels or single level

        Returns: List of take profit prices or single take profit price
        """
        if reward_risk_ratio is None:
            reward_risk_ratio = self.params.risk_reward_ratio

        risk_amount = entry_price - stop_loss
        base_target_reward = risk_amount * reward_risk_ratio

        # Calculate volatility-based adjustment
        volatility_multiplier = 1 + (volatility * self.params.volatility_tp_multiplier)
        volatility_adjusted_reward = base_target_reward * volatility_multiplier

        # Calculate trend strength adjustment
        trend_multiplier = 1 + (abs(trend_strength) * self.params.trend_tp_multiplier)
        if trend_strength < 0:
            trend_multiplier = 1 - (abs(trend_strength) * self.params.trend_tp_multiplier * 0.5)
        trend_adjusted_reward = volatility_adjusted_reward * trend_multiplier

        # Calculate market regime adjustment
        regime_multiplier = self.params.volatility_regime_multipliers.get(market_regime, 1.0)
        final_target_reward = trend_adjusted_reward * regime_multiplier

        if symbol:
            # Calculate actual fee rates from database (last 7 days)
            fee_rates = self._get_fee_rates(symbol)
            entry_fee_pct = fee_rates["taker"]  # Assume taker on entry (market order)
            exit_fee_pct = fee_rates["maker"]  # Assume maker on exit (limit order)

            # Calculate total transaction costs including fees and slippage
            total_cost_pct = entry_fee_pct + exit_fee_pct + self.params.slippage_estimate
        else:
            total_cost_pct = 0

        if return_multiple_levels:
            # Calculate multiple take profit levels with partial profit taking
            tp_levels = []
            for ratio, level_multiplier in zip(
                self.params.tp_levels, self.params.tp_level_multipliers
            ):
                level_reward = final_target_reward * level_multiplier * ratio

                if symbol:
                    # Adjust for fees and slippage for each level
                    slippage_cost = entry_price * self.params.slippage_estimate
                    numerator = (
                        entry_price + level_reward + (entry_price * entry_fee_pct) + slippage_cost
                    )

                    if (1 - exit_fee_pct) <= 0:
                        logger.warning(
                            f"Exit fee percentage {exit_fee_pct:.4f} is too high, using minimum TP"
                        )
                        tp_price = entry_price * (
                            1 + self.params.min_take_profit_pct + total_cost_pct
                        )
                    else:
                        tp_price = numerator / (1 - exit_fee_pct)
                else:
                    tp_price = entry_price + level_reward

                tp_levels.append(tp_price)
        else:
            # Calculate single take profit level
            if symbol:
                slippage_cost = entry_price * self.params.slippage_estimate
                numerator = (
                    entry_price
                    + final_target_reward
                    + (entry_price * entry_fee_pct)
                    + slippage_cost
                )

                if (1 - exit_fee_pct) <= 0:
                    logger.warning(
                        f"Exit fee percentage {exit_fee_pct:.4f} is too high, using minimum TP"
                    )
                    tp_price = entry_price * (1 + self.params.min_take_profit_pct + total_cost_pct)
                else:
                    tp_price = numerator / (1 - exit_fee_pct)
            else:
                tp_price = entry_price + final_target_reward

            tp_levels = [tp_price]

        # Adjust levels based on resistance and recent price action
        for i, tp_price in enumerate(tp_levels):
            adjusted_price = tp_price

            # Cap at resistance level
            if resistance_level and resistance_level > entry_price:
                adjusted_price = min(adjusted_price, resistance_level * 0.99)

            # Recent price action based adjustment
            if price_history and len(price_history) >= 20:
                recent_highs = sorted(price_history[-20:], reverse=True)
                highest_high = recent_highs[0]
                # If resistance is not provided, use recent high as reference
                if not resistance_level or resistance_level > highest_high * 1.05:
                    adjusted_price = min(adjusted_price, highest_high * 0.99)

            # Ensure minimum take profit that covers all costs
            min_profit_pct = self.params.min_take_profit_pct
            if symbol:
                min_tp = entry_price * (1 + total_cost_pct + min_profit_pct)
            else:
                min_tp = entry_price * (1 + min_profit_pct)

            tp_levels[i] = max(adjusted_price, min_tp)

        # Sort levels in ascending order
        tp_levels = sorted(tp_levels)

        # Verify calculations and add validation
        if symbol:
            for i, tp_price in enumerate(tp_levels):
                gross_profit = tp_price - entry_price
                entry_fee = entry_price * entry_fee_pct
                exit_fee = tp_price * exit_fee_pct
                total_slippage = (entry_price + tp_price) * self.params.slippage_estimate / 2
                net_profit = gross_profit - entry_fee - exit_fee - total_slippage

                # Validate TP level is realistic
                if net_profit <= 0:
                    logger.warning(
                        f"TP Level {i + 1}: Net profit negative ({net_profit:.4f}) - adjusting to minimum"
                    )
                    min_tp = entry_price * (1 + total_cost_pct + self.params.min_take_profit_pct)
                    tp_levels[i] = max(tp_levels[i], min_tp)
                    # Recalculate net profit with adjusted price
                    tp_price = tp_levels[i]
                    gross_profit = tp_price - entry_price
                    entry_fee = entry_price * entry_fee_pct
                    exit_fee = tp_price * exit_fee_pct
                    total_slippage = (entry_price + tp_price) * self.params.slippage_estimate / 2
                    net_profit = gross_profit - entry_fee - exit_fee - total_slippage

                logger.debug(
                    f"TP Level {i + 1}: Price={tp_price:.4f}, Gross={gross_profit:.4f}, "
                    f"Net={net_profit:.4f}, Costs={total_cost_pct:.4f}%"
                )
        else:
            for i, tp_price in enumerate(tp_levels):
                logger.debug(f"TP Level {i + 1}: Price={tp_price:.4f}")

        if return_multiple_levels:
            return tp_levels
        else:
            return tp_levels[-1]  # Return the highest TP level

    def assess_position_risk(
        self,
        symbol: str,
        quantity: float,
        entry_price: float,
        current_price: float,
        stop_loss: float,
        take_profit: float or List[float],
        account_balance: float,
        volatility: float = 0.05,
        liquidity: float = 0.5,
        confidence: float = 0.5,
    ) -> PositionRisk:
        """
        Assess risk for a single position

        Returns: PositionRisk object with comprehensive risk assessment
        """
        position_value = quantity * current_price
        # Calculate exposure correctly (should be fraction of account balance)
        portfolio_exposure = (quantity * current_price) / account_balance

        # Calculate risk/reward metrics
        if stop_loss < entry_price:
            risk_amount = quantity * (entry_price - stop_loss)
        else:
            risk_amount = quantity * (current_price - stop_loss)

        # Handle single or multiple take profit levels
        if isinstance(take_profit, list):
            # Use the highest TP level for reward calculation
            max_tp = max(take_profit)
            if max_tp > entry_price:
                reward_amount = quantity * (max_tp - entry_price)
            else:
                reward_amount = quantity * (max_tp - current_price)
        else:
            if take_profit > entry_price:
                reward_amount = quantity * (take_profit - entry_price)
            else:
                reward_amount = quantity * (take_profit - current_price)

        risk_reward = reward_amount / risk_amount if risk_amount > 0 else 0

        return PositionRisk(
            symbol=symbol,
            entry_price=entry_price,
            quantity=quantity,
            stop_loss=stop_loss,
            take_profit=take_profit if isinstance(take_profit, float) else max(take_profit),
            risk_amount=risk_amount,
            reward_amount=reward_amount,
            risk_reward=risk_reward,
            position_value=position_value,
            portfolio_exposure=portfolio_exposure,
            confidence=confidence,
            volatility_score=volatility,
            liquidity_score=liquidity,
        )

    def assess_portfolio_risk(
        self, positions: List[PositionRisk], account_balance: float, portfolio_value: float
    ) -> PortfolioRisk:
        """
        Assess overall portfolio risk

        Returns: PortfolioRisk object with comprehensive assessment
        """
        if not positions:
            return PortfolioRisk(
                total_value=portfolio_value,
                total_risk=0,
                total_exposure=0,
                positions_count=0,
                max_position_risk=0,
                avg_position_risk=0,
                risk_concentration=0,
                drawdown_risk=0,
                volatility_risk=0,
                liquidity_risk=0,
            )

        total_risk = sum(pos.risk_amount for pos in positions)
        # Calculate total exposure as sum of each position's exposure (fraction of account balance)
        total_exposure = sum(pos.portfolio_exposure for pos in positions)
        positions_count = len(positions)

        position_risks = [pos.risk_amount for pos in positions]
        max_position_risk = max(position_risks) if position_risks else 0
        avg_position_risk = sum(position_risks) / positions_count if positions_count > 0 else 0

        position_values = [pos.position_value for pos in positions]
        value_std = np.std(position_values) if positions_count > 1 else 0
        risk_concentration = (
            value_std / (sum(position_values) / positions_count) if positions_count > 1 else 0
        )

        # Volatility risk based on average volatility of positions
        volatility_scores = [pos.volatility_score for pos in positions]
        volatility_risk = (
            sum(vs * pos.position_value for vs, pos in zip(volatility_scores, positions))
            / total_exposure
            if total_exposure > 0
            else 0
        )

        # Liquidity risk
        liquidity_scores = [pos.liquidity_score for pos in positions]
        liquidity_risk = 1 - (
            sum(ls * pos.position_value for ls, pos in zip(liquidity_scores, positions))
            / total_exposure
            if total_exposure > 0
            else 0
        )

        # Drawdown risk based on volatility and concentration
        drawdown_risk = volatility_risk * (1 + risk_concentration)

        return PortfolioRisk(
            total_value=portfolio_value,
            total_risk=total_risk,
            total_exposure=total_exposure,
            positions_count=positions_count,
            max_position_risk=max_position_risk,
            avg_position_risk=avg_position_risk,
            risk_concentration=risk_concentration,
            drawdown_risk=drawdown_risk,
            volatility_risk=volatility_risk,
            liquidity_risk=liquidity_risk,
        )

    def validate_position(
        self, position: PositionRisk, portfolio_risk: PortfolioRisk
    ) -> Tuple[bool, List[str]]:
        """
        Validate if position meets risk constraints

        Returns: (is_valid, [violations])
        """
        violations = []

        # Check individual position constraints
        if position.risk_amount > self.params.max_risk_per_trade * portfolio_risk.total_value:
            violations.append("Position risk exceeds max per trade")

        if position.position_value < self.params.min_position_size:
            violations.append("Position size too small")

        if position.position_value > self.params.max_position_size:
            violations.append("Position size too large")

        if position.risk_reward < 0.4:  # 1:2.5 risk-reward minimum (stricter)
            violations.append("Risk-reward ratio too low")

        # Check portfolio constraints
        if portfolio_risk.total_exposure > self.params.portfolio_heat_limit:
            violations.append("Portfolio exposure too high")

        if position.portfolio_exposure > 0.15:  # 15% max single position exposure (stricter)
            violations.append("Single position exposure too high")

        if portfolio_risk.risk_concentration > 0.4:  # Lower concentration risk threshold
            violations.append("Portfolio too concentrated")

        if portfolio_risk.drawdown_risk > 0.25:  # Lower drawdown risk threshold
            violations.append("High drawdown risk")

        # Validate position risk calculations
        if position.risk_amount <= 0:
            violations.append("Invalid risk amount")
        if position.reward_amount <= 0:
            violations.append("Invalid reward amount")

        return len(violations) == 0, violations

    def calculate_position_score(
        self, position: PositionRisk, portfolio_risk: PortfolioRisk
    ) -> float:
        """
        Calculate overall position score combining reward, risk, and portfolio fit

        Returns: Score between 0 (worst) and 100 (best)
        """
        score = 0

        # Reward component (60% weight)
        risk_reward_score = min(position.risk_reward * 33.33, 60)  # Max 60 points for 1.8+ RR
        profit_potential = min(
            (position.take_profit - position.entry_price) / position.entry_price * 100, 40
        )
        reward_score = risk_reward_score + profit_potential

        # Risk component (30% weight)
        risk_score = 30
        if position.risk_amount > self.params.max_risk_per_trade * portfolio_risk.total_value:
            risk_score -= 15
        if position.risk_reward < 0.4:
            risk_score -= 10

        # Portfolio fit (10% weight)
        fit_score = 10
        if position.portfolio_exposure > 0.2:
            fit_score -= 5
        if portfolio_risk.risk_concentration > 0.5:
            fit_score -= 3

        return reward_score + risk_score + fit_score

    def generate_stop_loss_recommendation(
        self,
        symbol: str,
        current_price: float,
        volatility: float,
        atr: float,
        support_level: float = None,
        trend_strength: float = 0.5,
    ) -> Tuple[float, str]:
        """
        Generate stop loss recommendation

        Returns: (stop_loss_price, reasoning)
        """
        sl_price = self.calculate_stop_loss(
            current_price, volatility, atr, support_level, trend_strength
        )
        distance_pct = (current_price - sl_price) / current_price * 100

        reasoning = []
        if trend_strength > 0.5:
            reasoning.append("Strong uptrend detected")
        elif trend_strength < -0.5:
            reasoning.append("Strong downtrend detected")

        if volatility > 0.08:
            reasoning.append("High volatility")
        elif volatility < 0.03:
            reasoning.append("Low volatility")

        if support_level and abs((sl_price - support_level) / support_level) < 0.02:
            reasoning.append("Placed below recent support")

        return sl_price, "; ".join(reasoning)

    def generate_take_profit_recommendation(
        self,
        entry_price: float,
        current_price: float,
        stop_loss: float,
        resistance_level: float = None,
        trend_strength: float = 0.5,
        volatility: float = 0.05,
        market_regime: str = "NORMAL",
    ) -> Tuple[List[float], str]:
        """
        Generate take profit recommendation with multiple levels

        Returns: (take_profit_prices, reasoning)
        """
        tp_prices = self.calculate_take_profit(
            entry_price,
            stop_loss,
            trend_strength=trend_strength,
            volatility=volatility,
            market_regime=market_regime,
        )

        reasoning = []
        if trend_strength > 0.5:
            reasoning.append("Strong uptrend detected - higher TP targets")
        elif trend_strength < -0.5:
            reasoning.append("Strong downtrend detected - lower TP targets")

        if volatility > 0.08:
            reasoning.append("High volatility - expanded TP range")
        elif volatility < 0.03:
            reasoning.append("Low volatility - tighter TP range")

        if resistance_level:
            reasoning.append("Targeting recent resistance levels")

        if market_regime in ["VOLATILE", "STRONG_BULL"]:
            reasoning.append(f"{market_regime} regime - optimized TP levels")

        return tp_prices, "; ".join(reasoning)

    def calculate_correlation_risk(
        self,
        positions: List[PositionRisk],
        correlation_matrix: Optional[Dict[str, Dict[str, float]]] = None,
    ) -> float:
        """
        Calculate correlation risk between positions

        Args:
            positions: List of positions
            correlation_matrix: Correlation between symbols (0-1)

        Returns: Correlation risk score (0-1)
        """
        if len(positions) < 2 or not correlation_matrix:
            return 0.0

        risk = 0.0
        pairs = []

        for i, pos1 in enumerate(positions):
            for j, pos2 in enumerate(positions):
                if (
                    i < j
                    and (pos1.symbol, pos2.symbol) not in pairs
                    and (pos2.symbol, pos1.symbol) not in pairs
                ):
                    pairs.append((pos1.symbol, pos2.symbol))

                    if (
                        pos1.symbol in correlation_matrix
                        and pos2.symbol in correlation_matrix[pos1.symbol]
                    ):
                        corr = correlation_matrix[pos1.symbol][pos2.symbol]
                        weight = pos1.position_value * pos2.position_value
                        risk += corr * weight

        total_value = sum(pos.position_value for pos in positions)
        avg_correlation_risk = risk / (total_value**2) if total_value > 0 else 0

        return min(avg_correlation_risk * 2, 1.0)  # Normalize to 0-1 scale

    def backtest_tp_sl_strategy(
        self,
        historical_data: List[Dict],
        symbol: str,
        start_date: datetime,
        end_date: datetime,
    ) -> Dict:
        """
        Backtest the dynamic TP/SL strategy using historical data

        Args:
            historical_data: List of OHLCV data with 'timestamp', 'open', 'high', 'low', 'close'
            symbol: Trading symbol
            start_date: Start date for backtest
            end_date: End date for backtest

        Returns: Backtest results including win rate, profit factor, etc.
        """
        trades = []
        position = None
        results = {
            "total_trades": 0,
            "winning_trades": 0,
            "losing_trades": 0,
            "total_profit": 0.0,
            "avg_win": 0.0,
            "avg_loss": 0.0,
            "profit_factor": 0.0,
            "max_drawdown": 0.0,
            "win_rate": 0.0,
        }

        # Filter data for date range
        filtered_data = [
            d
            for d in historical_data
            if start_date <= datetime.fromtimestamp(d["timestamp"] / 1000) <= end_date
        ]

        for i, data in enumerate(filtered_data):
            if i < 20:  # Need at least 20 periods for indicators
                continue

            # Calculate volatility and ATR from historical data
            price_history = [d["close"] for d in filtered_data[max(0, i - 20) : i]]
            current_price = data["close"]

            # Simplified ATR calculation for backtesting
            atr = 0.0
            if i >= 14:
                tr_values = []
                for j in range(i - 13, i):
                    high_low = filtered_data[j]["high"] - filtered_data[j]["low"]
                    high_close = abs(filtered_data[j]["high"] - filtered_data[j - 1]["close"])
                    low_close = abs(filtered_data[j]["low"] - filtered_data[j - 1]["close"])
                    tr_values.append(max(high_low, high_close, low_close))
                atr = sum(tr_values) / 14

            volatility = np.std(price_history) / current_price if len(price_history) > 1 else 0.05

            if not position:
                # Entry signal (simplified for backtesting)
                if i > 0 and data["close"] > filtered_data[i - 1]["close"]:
                    entry_price = data["close"]
                    # Calculate dynamic SL and TP
                    stop_loss = self.calculate_stop_loss(
                        entry_price, volatility, atr, symbol=symbol, price_history=price_history
                    )
                    take_profit = self.calculate_take_profit(
                        entry_price, stop_loss, symbol=symbol, price_history=price_history
                    )

                    position = {
                        "entry_price": entry_price,
                        "stop_loss": stop_loss,
                        "take_profit": take_profit,
                        "highest_price": entry_price,
                        "entry_index": i,
                    }
            else:
                # Update highest price for trailing stop
                if data["high"] > position["highest_price"]:
                    position["highest_price"] = data["high"]

                # Check for exit conditions
                exited = False

                # Check stop loss
                if data["low"] <= position["stop_loss"]:
                    exit_price = position["stop_loss"]
                    exited = True
                # Check take profit
                elif data["high"] >= position["take_profit"]:
                    exit_price = position["take_profit"]
                    exited = True
                # Check trailing stop (activated after 1% profit)
                else:
                    trailing_stop = self.calculate_trailing_stop(
                        position["entry_price"],
                        data["close"],
                        position["highest_price"],
                        volatility,
                        atr,
                        symbol=symbol,
                    )
                    if trailing_stop and data["low"] <= trailing_stop:
                        exit_price = trailing_stop
                        exited = True

                if exited:
                    # Calculate trade results
                    profit = exit_price - position["entry_price"]
                    trades.append(
                        {
                            "entry_price": position["entry_price"],
                            "exit_price": exit_price,
                            "profit": profit,
                            "duration": i - position["entry_index"],
                            "type": "win" if profit > 0 else "loss",
                        }
                    )
                    position = None

        # Calculate results
        if trades:
            results["total_trades"] = len(trades)
            results["winning_trades"] = sum(1 for t in trades if t["profit"] > 0)
            results["losing_trades"] = sum(1 for t in trades if t["profit"] < 0)

            total_win = sum(t["profit"] for t in trades if t["profit"] > 0)
            total_loss = sum(abs(t["profit"]) for t in trades if t["profit"] < 0)

            results["total_profit"] = total_win - total_loss
            results["avg_win"] = (
                total_win / results["winning_trades"] if results["winning_trades"] > 0 else 0
            )
            results["avg_loss"] = (
                total_loss / results["losing_trades"] if results["losing_trades"] > 0 else 0
            )
            results["profit_factor"] = total_win / total_loss if total_loss > 0 else 0
            results["win_rate"] = results["winning_trades"] / results["total_trades"]

            # Calculate max drawdown (simplified)
            cumulative_profit = 0
            peak = 0
            max_drawdown = 0

            for trade in trades:
                cumulative_profit += trade["profit"]
                if cumulative_profit > peak:
                    peak = cumulative_profit
                drawdown = peak - cumulative_profit
                if drawdown > max_drawdown:
                    max_drawdown = drawdown

            results["max_drawdown"] = max_drawdown

        logger.info(
            f"Backtest results for {symbol}: {results['total_trades']} trades, "
            f"{results['win_rate']:.1%} win rate, Profit factor: {results['profit_factor']:.2f}"
        )

        return results

    def validate_tp_sl_calculations(
        self,
        historical_trades: List[Dict],
        symbol: str,
    ) -> Dict:
        """
        Validate the dynamic TP/SL calculations using historical trade data

        Args:
            historical_trades: List of historical trades with entry/exit prices
            symbol: Trading symbol

        Returns: Validation results comparing static vs dynamic calculations
        """
        static_profits = []
        dynamic_profits = []

        for trade in historical_trades:
            entry_price = trade["entry_price"]
            actual_exit = trade["exit_price"]
            actual_profit = actual_exit - entry_price

            # Calculate static SL/TP (old method)
            static_stop = entry_price * (1 - self.params.stop_loss_pct)
            static_tp = entry_price * (1 + self.params.take_profit_pct)

            # Calculate dynamic SL/TP
            volatility = trade.get("volatility", 0.05)
            atr = trade.get("atr", entry_price * 0.02)
            price_history = trade.get("price_history", [entry_price])

            dynamic_stop = self.calculate_stop_loss(
                entry_price, volatility, atr, symbol=symbol, price_history=price_history
            )
            dynamic_tp = self.calculate_take_profit(
                entry_price, dynamic_stop, symbol=symbol, price_history=price_history
            )

            # Determine what would have happened with static vs dynamic
            if actual_exit <= static_stop:
                static_profits.append(static_stop - entry_price)
            elif actual_exit >= static_tp:
                static_profits.append(static_tp - entry_price)
            else:
                static_profits.append(actual_profit)

            if actual_exit <= dynamic_stop:
                dynamic_profits.append(dynamic_stop - entry_price)
            elif actual_exit >= dynamic_tp:
                dynamic_profits.append(dynamic_tp - entry_price)
            else:
                dynamic_profits.append(actual_profit)

        # Calculate validation metrics
        validation = {
            "static_total": sum(static_profits),
            "dynamic_total": sum(dynamic_profits),
            "static_avg": np.mean(static_profits) if static_profits else 0,
            "dynamic_avg": np.mean(dynamic_profits) if dynamic_profits else 0,
            "static_win_rate": sum(1 for p in static_profits if p > 0) / len(static_profits)
            if static_profits
            else 0,
            "dynamic_win_rate": sum(1 for p in dynamic_profits if p > 0) / len(dynamic_profits)
            if dynamic_profits
            else 0,
            "profit_improvement": sum(dynamic_profits) - sum(static_profits),
        }

        logger.info(
            f"Validation results for {symbol}: Static profit: {validation['static_total']:.2f}, "
            f"Dynamic profit: {validation['dynamic_total']:.2f}, Improvement: {validation['profit_improvement']:.2f}"
        )

        return validation


# Global instance
risk_manager = RiskManager()
