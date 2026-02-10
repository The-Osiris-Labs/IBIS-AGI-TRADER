"""
IBIS Local Reasoning Engine - Fallback when LLMs unavailable
By TheOsirisLabs.com | Founder: Youssef SalahEldin

Provides local reasoning when free models require payment.
Uses algorithmic analysis instead of LLM calls.
"""

import asyncio
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum


class DecisionType(Enum):
    """Types of trading decisions."""

    BUY = "BUY"
    SELL = "SELL"
    HOLD = "HOLD"
    SCALE_IN = "SCALE_IN"
    SCALE_OUT = "SCALE_OUT"


@dataclass
class LocalDecision:
    """Local trading decision."""

    action: str
    confidence: float
    reasoning: str
    risk_level: str
    regime: str
    key_levels: List[float] = field(default_factory=list)


class LocalReasoningEngine:
    """
    Local reasoning engine using algorithmic analysis.
    Fallback when LLM is unavailable or requires payment.
    """

    def __init__(self):
        self.decision_history: List[Dict] = []
        self.regime_history: List[str] = []

    def analyze_market(
        self,
        symbol: str,
        price: float,
        price_change_pct: float,
        volatility_1h: float,
        volatility_24h: float,
        trend_strength: float,
        spread_avg: float,
        order_flow: str,
        recent_trades: List[Dict] = None,
    ) -> LocalDecision:
        """
        Algorithmic market analysis.
        """
        # Determine regime
        regime = self._determine_regime(
            volatility_1h, volatility_24h, trend_strength, spread_avg
        )

        # Determine action based on regime
        action, reasoning = self._determine_action(
            regime, price_change_pct, order_flow, trend_strength
        )

        # Calculate confidence
        confidence = self._calculate_confidence(
            volatility_1h, trend_strength, price_change_pct
        )

        # Determine risk level
        risk_level = self._assess_risk(volatility_1h, volatility_24h, regime)

        # Calculate key levels
        key_levels = self._calculate_key_levels(price, volatility_1h, regime)

        # Record decision
        decision = {
            "timestamp": datetime.now().isoformat(),
            "symbol": symbol,
            "regime": regime,
            "action": action,
            "confidence": confidence,
            "reasoning": reasoning,
        }
        self.decision_history.append(decision)

        return LocalDecision(
            action=action,
            confidence=confidence,
            reasoning=reasoning,
            risk_level=risk_level,
            regime=regime,
            key_levels=key_levels,
        )

    def quick_decide(
        self,
        symbol: str,
        price: float,
        volatility: float,
        trend: float,
        order_flow: str,
    ) -> LocalDecision:
        """Fast decision for time-sensitive scenarios."""
        return self.analyze_market(
            symbol=symbol,
            price=price,
            price_change_pct=0,
            volatility_1h=volatility,
            volatility_24h=volatility,
            trend_strength=trend,
            spread_avg=0.05,
            order_flow=order_flow,
        )

    def _determine_regime(
        self,
        volatility_1h: float,
        volatility_24h: float,
        trend_strength: float,
        spread_avg: float,
    ) -> str:
        """Determine market regime."""
        avg_volatility = (volatility_1h + volatility_24h) / 2

        if avg_volatility < 1.5 and spread_avg < 0.05:
            return "SCALPER"
        elif avg_volatility > 1.5 and trend_strength > 25:
            return "MOMENTUM"
        elif avg_volatility > 3.0 or spread_avg > 0.1:
            return "VOLATILITY"
        else:
            return "IDLE"

    def _determine_action(
        self,
        regime: str,
        price_change_pct: float,
        order_flow: str,
        trend_strength: float,
    ) -> tuple:
        """Determine trading action."""
        order_flow_bullish = order_flow.upper() in ["BULLISH", "BUY", "STRONG_BUY"]
        order_flow_bearish = order_flow.upper() in ["BEARISH", "SELL", "STRONG_SELL"]

        if regime == "SCALPER":
            # Scalper mode: neutral action, focus on spread
            return "HOLD", "Calm market - scalper mode, waiting for clear signal"

        elif regime == "MOMENTUM":
            # Momentum mode: follow trend
            if order_flow_bullish and trend_strength > 30:
                return "BUY", f"Momentum bullish with strength {trend_strength:.0f}"
            elif order_flow_bearish and trend_strength > 30:
                return "SELL", f"Momentum bearish with strength {trend_strength:.0f}"
            else:
                return "HOLD", "Momentum unclear, awaiting confirmation"

        elif regime == "VOLATILITY":
            # Volatility mode: mean reversion
            if price_change_pct < -5:
                return "BUY", f"Oversold by {abs(price_change_pct):.1f}%, buying dip"
            elif price_change_pct > 5:
                return "SELL", f"Overbought by {price_change_pct:.1f}%, taking profit"
            else:
                return "HOLD", "Volatility mode but no extreme move"

        else:  # IDLE
            return "HOLD", "No clear regime identified"

    def _calculate_confidence(
        self, volatility: float, trend: float, price_change: float
    ) -> float:
        """Calculate decision confidence."""
        confidence = 0.5  # Base confidence

        # Volatility factor
        if volatility < 2:
            confidence += 0.1  # Lower vol = more predictable
        elif volatility > 4:
            confidence -= 0.1  # Higher vol = less predictable

        # Trend factor
        if trend > 40:
            confidence += 0.15  # Strong trend = higher confidence
        elif trend < 15:
            confidence -= 0.1  # Weak trend = lower confidence

        # Price change factor
        if abs(price_change) < 1:
            confidence += 0.05  # Small moves = more predictable
        elif abs(price_change) > 5:
            confidence -= 0.1  # Large moves = less predictable

        return max(0.2, min(0.95, confidence))

    def _assess_risk(
        self, volatility_1h: float, volatility_24h: float, regime: str
    ) -> str:
        """Assess risk level."""
        avg_vol = (volatility_1h + volatility_24h) / 2

        if regime == "SCALPER":
            return "LOW"
        elif regime == "MOMENTUM":
            return "MEDIUM" if avg_vol < 3 else "HIGH"
        elif regime == "VOLATILITY":
            return "HIGH" if avg_vol < 5 else "EXTREME"
        else:
            return "MEDIUM"

    def _calculate_key_levels(
        self, price: float, volatility: float, regime: str
    ) -> List[float]:
        """Calculate key price levels."""
        atr = price * (volatility / 100)

        levels = [price]

        if regime == "SCALPER":
            levels.append(price - atr * 0.1)  # Tight stop
            levels.append(price + atr * 0.1)

        elif regime == "MOMENTUM":
            levels.append(price - atr * 2)  # Wide stop
            levels.append(price + atr * 5)  # Target

        elif regime == "VOLATILITY":
            levels.append(price - atr * 4)  # Deep stop
            levels.append(price + atr * 8)  # Big target

        return sorted(set(levels))

    def reflect_on_trade(self, trade_data: Dict, context: Dict) -> Dict:
        """Generate reflection on trade."""
        pnl_pct = trade_data.get("pnl_pct", 0)
        pnl_abs = trade_data.get("pnl_abs", 0)
        duration = trade_data.get("duration", 0)
        mode = trade_data.get("mode", "UNKNOWN")
        regime = context.get("regime", "UNKNOWN")

        if pnl_pct > 0.5:
            outcome = "WIN"
            analysis = f"Strong win in {mode} mode. Regime alignment: {regime == mode}."
            lesson = "Maintaining discipline in identified regime pays off."
        elif pnl_pct > 0:
            outcome = "SMALL_WIN"
            analysis = f"Small win in {mode} mode. Risk management working."
            lesson = "Consistent small wins compound over time."
        elif pnl_pct > -0.5:
            outcome = "SMALL_LOSS"
            analysis = f"Small loss in {mode} mode. Acceptable for strategy."
            lesson = "Small losses are cost of doing business."
        else:
            outcome = "LOSS"
            analysis = f"Significant loss in {mode} mode. Review needed."
            lesson = "Check regime identification accuracy."

        return {
            "analysis": analysis,
            "outcome": outcome,
            "lesson": lesson,
            "pnl_pct": pnl_pct,
            "pnl_abs": pnl_abs,
            "duration_seconds": duration,
            "timestamp": datetime.now().isoformat(),
        }

    def generate_insight(self, performance_data: Dict) -> str:
        """Generate strategic insight."""
        mode_performance = performance_data.get("mode_dist", {})

        best_mode = max(mode_performance.items(), key=lambda x: x[1].get("win_rate", 0))

        return f"Current best performing mode: {best_mode[0]} with {best_mode[1].get('win_rate', 0):.1%} win rate. Consider focusing on this regime."

    def get_statistics(self) -> Dict:
        """Get engine statistics."""
        if not self.decision_history:
            return {"total_decisions": 0}

        wins = sum(1 for d in self.decision_history if d["action"] in ["BUY", "SELL"])

        return {
            "total_decisions": len(self.decision_history),
            "directional_decisions": wins,
            "avg_confidence": sum(d["confidence"] for d in self.decision_history)
            / len(self.decision_history),
            "regime_distribution": self._count_regimes(),
        }

    def _count_regimes(self) -> Dict:
        """Count regime occurrences."""
        counts = {}
        for d in self.decision_history:
            regime = d.get("regime", "UNKNOWN")
            counts[regime] = counts.get(regime, 0) + 1
        return counts


# Global instance
local_reasoning: Optional[LocalReasoningEngine] = None


def get_local_reasoning() -> LocalReasoningEngine:
    """Get or create global local reasoning instance."""
    global local_reasoning

    if local_reasoning is None:
        local_reasoning = LocalReasoningEngine()

    return local_reasoning
