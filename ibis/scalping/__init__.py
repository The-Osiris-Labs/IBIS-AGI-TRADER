"""
IBIS Precision Execution Module
================================
Enhances execution quality WITHOUT changing:
- Trade frequency (unlimited, IBIS decides)
- Position sizing (15% base, $10-15 per trade)
- Core strategy behavior
- Score thresholds or selection criteria

Only improves HOW trades are executed when IBIS decides to trade.
"""

from .order_flow import OrderFlowImbalance
from .liquidity_detector import LiquidityGrabDetector
from .momentum_sniper import MomentumSnipper
from .entry_optimizer import EntryOptimizer
from .smart_stops import SmartStopManager

__all__ = [
    "OrderFlowImbalance",
    "LiquidityGrabDetector",
    "MomentumSnipper",
    "EntryOptimizer",
    "SmartStopManager",
]
