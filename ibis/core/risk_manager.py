"""
IBIS Risk Management Framework
Comprehensive risk management for cryptocurrency trading
"""

import math
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
import numpy as np


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
    """Comprehensive risk management system"""

    def __init__(self, params: RiskParams = None):
        self.params = params or RiskParams()
        self.position_history: List[Dict] = []
        self.risk_scores: Dict[str, float] = {}

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

        # Adjust for confidence and volatility
        confidence_multiplier = 0.5 + (confidence * 1.5)  # 0.5 to 2.0
        volatility_multiplier = max(0.5, min(2.0, 1 / (volatility * 100)))  # Inverse of volatility
        liquidity_multiplier = 0.5 + (liquidity * 0.5)  # 0.5 to 1.0

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
                max(self.params.min_position_size, account_balance * 0.02),
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

        return quantity, position_value, min(adjusted_risk, position_value)

    def calculate_stop_loss(
        self,
        entry_price: float,
        volatility: float,
        atr: float,
        support_level: float = None,
        trend_strength: float = 0.5,
    ) -> float:
        """
        Calculate dynamic stop loss based on volatility and market conditions

        Args:
            entry_price: Entry price
            volatility: Price volatility (0-1)
            atr: Average True Range
            support_level: Recent support level
            trend_strength: Trend strength (-1 to 1, negative = bearish)

        Returns: Stop loss price
        """
        # Base stop loss percentage based on volatility
        base_sl_pct = self.params.stop_loss_pct
        volatility_sl = entry_price * (1 - (base_sl_pct * (1 + volatility)))

        # ATR-based stop loss
        atr_sl = entry_price - (atr * 1.5)

        # Support-based stop loss
        support_sl = entry_price * 0.98  # Default if no support
        if support_level and support_level < entry_price:
            # Place stop loss slightly below support
            support_sl = support_level * 0.99

        # Trend adjustment
        trend_multiplier = 1.0
        if trend_strength > 0.5:
            # Strong uptrend - tighten stop loss
            trend_multiplier = 0.8
        elif trend_strength < -0.5:
            # Strong downtrend - widen stop loss
            trend_multiplier = 1.2

        # Combine all stop loss methods with trend adjustment
        stop_loss = min(volatility_sl, atr_sl, support_sl) * trend_multiplier

        # Ensure stop loss is not too far from entry price
        max_sl_distance = entry_price * 0.10  # 10% maximum distance
        stop_loss = max(entry_price - max_sl_distance, stop_loss)

        return max(entry_price * 0.90, stop_loss)  # Minimum 10% stop loss

    def calculate_take_profit(
        self,
        entry_price: float,
        stop_loss: float,
        reward_risk_ratio: float = None,
        resistance_level: float = None,
        trend_strength: float = 0.5,
    ) -> float:
        """
        Calculate optimal take profit based on risk-reward ratio

        Args:
            entry_price: Entry price
            stop_loss: Stop loss price
            reward_risk_ratio: Desired reward-risk ratio
            resistance_level: Recent resistance level
            trend_strength: Trend strength (-1 to 1)

        Returns: Take profit price
        """
        if reward_risk_ratio is None:
            reward_risk_ratio = self.params.risk_reward_ratio

        risk_amount = entry_price - stop_loss
        target_reward = risk_amount * reward_risk_ratio
        tp_price = entry_price + target_reward

        # Adjust for trend strength
        trend_multiplier = 1.0
        if trend_strength > 0.5:
            # Strong uptrend - increase target
            trend_multiplier = 1.1
        elif trend_strength < -0.5:
            # Strong downtrend - decrease target
            trend_multiplier = 0.9

        tp_price = tp_price * trend_multiplier

        # Cap at resistance level
        if resistance_level and resistance_level > entry_price:
            tp_price = min(tp_price, resistance_level * 0.99)

        # Ensure minimum take profit
        min_tp = entry_price * (1 + 0.01)  # 1% minimum
        tp_price = max(min_tp, tp_price)

        return tp_price

    def assess_position_risk(
        self,
        symbol: str,
        quantity: float,
        entry_price: float,
        current_price: float,
        stop_loss: float,
        take_profit: float,
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
        portfolio_exposure = position_value / account_balance

        # Calculate risk/reward metrics
        if stop_loss < entry_price:
            risk_amount = quantity * (entry_price - stop_loss)
        else:
            risk_amount = quantity * (current_price - stop_loss)

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
            take_profit=take_profit,
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
        total_exposure = sum(pos.position_value for pos in positions)
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

        if position.risk_reward < 0.3:  # 1:3.3 risk-reward minimum
            violations.append("Risk-reward ratio too low")

        # Check portfolio constraints
        if portfolio_risk.total_exposure > self.params.portfolio_heat_limit:
            violations.append("Portfolio exposure too high")

        if position.portfolio_exposure > 0.2:  # 20% max single position exposure
            violations.append("Single position exposure too high")

        if portfolio_risk.risk_concentration > 0.5:  # High concentration risk
            violations.append("Portfolio too concentrated")

        if portfolio_risk.drawdown_risk > 0.3:  # High drawdown risk
            violations.append("High drawdown risk")

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
    ) -> Tuple[float, str]:
        """
        Generate take profit recommendation

        Returns: (take_profit_price, reasoning)
        """
        tp_price = self.calculate_take_profit(entry_price, stop_loss, trend_strength=trend_strength)
        distance_pct = (tp_price - current_price) / current_price * 100

        reasoning = []
        if trend_strength > 0.5:
            reasoning.append("Strong uptrend detected")
        elif trend_strength < -0.5:
            reasoning.append("Strong downtrend detected")

        if resistance_level and abs((tp_price - resistance_level) / resistance_level) < 0.02:
            reasoning.append("Targeting recent resistance")

        return tp_price, "; ".join(reasoning)

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


# Global instance
risk_manager = RiskManager()
