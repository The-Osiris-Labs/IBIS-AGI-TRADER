"""
IBIS v8 PROFESSIONAL CONFIGURATION (Deprecated)
===============================================
This module is deprecated. Import from ibis.core.trading_constants instead.
Kept for backwards compatibility - imports from unified config.
"""

from ibis.core.trading_constants import (
    TRADING,
    SCORE_THRESHOLDS,
    RISK_CONFIG,
    POSITION_CONFIG,
)


class Config:
    """Backwards-compatible wrapper around unified TRADING config"""

    EXCHANGE: str = TRADING.EXCHANGE.EXCHANGE
    FEE_TIER: str = TRADING.EXCHANGE.FEE_TIER
    MAKER_FEE: float = TRADING.EXCHANGE.MAKER_FEE
    TAKER_FEE: float = TRADING.EXCHANGE.TAKER_FEE
    ESTIMATED_SLIPPAGE: float = TRADING.EXCHANGE.ESTIMATED_SLIPPAGE

    MIN_VIABLE_TARGET: float = TRADING.CRITICAL.MIN_VIABLE_TARGET

    TIMEFRAME: str = TRADING.SCAN.TIMEFRAME
    LOOKBACK_PERIOD: int = TRADING.SCAN.LOOKBACK_PERIOD

    MAX_CAPITAL_PER_TRADE: float = TRADING.CRITICAL.MAX_CAPITAL_PER_TRADE
    MIN_CAPITAL_PER_TRADE: float = TRADING.CRITICAL.MIN_CAPITAL_PER_TRADE
    MAX_POSITIONS: int = TRADING.CRITICAL.MAX_POSITIONS
    STOP_LOSS_PCT: float = TRADING.RISK.STOP_LOSS_PCT
    TAKE_PROFIT_PCT: float = TRADING.RISK.TAKE_PROFIT_PCT

    AGI_CONFIDENCE_THRESHOLD: float = TRADING.INTELLIGENCE.AGI_CONFIDENCE_THRESHOLD
    CROSS_EXCHANGE_LEAD_THRESHOLD: float = (
        TRADING.INTELLIGENCE.CROSS_EXCHANGE_LEAD_THRESHOLD
    )

    @classmethod
    def get_total_friction(cls) -> float:
        """Calculate total friction (fees + slippage)."""
        return TRADING.get_total_friction()
