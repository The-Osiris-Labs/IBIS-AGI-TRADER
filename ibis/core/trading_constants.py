"""
IBIS Unified Configuration
==========================
Centralized configuration for all trading thresholds and constants.
Merged from config.py and trading_constants.py for consistency.
"""

from dataclasses import dataclass, field
from typing import Dict
from enum import Enum


class MarketRegime(Enum):
    """Market regime classifications"""

    STRONG_BULL = "STRONG_BULL"
    BULL = "BULL"
    BEAR = "BEAR"
    STRONG_BEAR = "STRONG_BEAR"
    VOLATILE = "VOLATILE"
    NORMAL = "NORMAL"
    FLAT = "FLAT"
    UNKNOWN = "UNKNOWN"


@dataclass
class ExchangeConfig:
    """Exchange parameters"""

    EXCHANGE: str = "kucoin"
    FEE_TIER: str = "Taker"
    MAKER_FEE: float = 0.0010  # 0.10%
    TAKER_FEE: float = 0.0010  # 0.10%
    ESTIMATED_SLIPPAGE: float = 0.0005  # 0.05%

    def get_total_friction(self) -> float:
        return self.TAKER_FEE + self.MAKER_FEE + self.ESTIMATED_SLIPPAGE


@dataclass
class CriticalThresholds:
    """Critical trading thresholds"""

    MIN_VIABLE_TARGET: float = 0.0150  # 1.5% (minimum viable target to cover fees)
    MIN_CAPITAL_PER_TRADE: float = 10.0  # Min USD per position
    MAX_CAPITAL_PER_TRADE: float = 20.0  # Max USD per position
    MAX_POSITIONS: int = 5
    MIN_SCORE_THRESHOLD: float = 0.70  # 70% confidence threshold


@dataclass
class ScoreThresholds:
    """Score thresholds for opportunity grading"""

    GOD_TIER: int = 95  # Exceptional opportunities
    HIGH_CONFIDENCE: int = 90  # High confidence trades
    STRONG_SETUP: int = 85  # Strong buy signal
    GOOD_SETUP: int = 80  # Good buy signal
    STANDARD: int = 70  # Standard opportunity
    MIN_THRESHOLD: int = 55  # Lowered to be more aggressive in volatile markets
    MARKET_PRIMED_HIGH_COUNT: int = (
        5  # Number of high-scoring symbols for "primed" mode
    )
    MARKET_PRIMED_AVG_SCORE: int = 70  # Lowered to be more aggressive


@dataclass
class PositionConfig:
    """Position-related configuration - AGGRESSIVE CAPITAL UTILIZATION"""

    MAX_TOTAL_POSITIONS: int = 5  # Max concurrent positions
    MIN_CAPITAL_PER_TRADE: float = 5.0  # $5 minimum per trade
    FINAL_TRADE_MIN_CAPITAL: float = 5.0  # $5 minimum for final trade
    MAX_CAPITAL_PER_TRADE: float = 30.0  # $30 maximum per trade
    MAX_POSITION_PCT: float = 50.0  # 50% max of portfolio per position
    BASE_POSITION_PCT: float = 40.0  # 40% base per position (USE CAPITAL!)

    def __post_init__(self):
        if self.MIN_CAPITAL_PER_TRADE < 5.0:
            self.MIN_CAPITAL_PER_TRADE = 5.0
        if self.FINAL_TRADE_MIN_CAPITAL < 5.0:
            self.FINAL_TRADE_MIN_CAPITAL = 5.0


@dataclass
class ScanConfig:
    """Scanning configuration"""

    DEFAULT_SCAN_INTERVAL: int = 10
    DEFAULT_MAX_POSITIONS: int = 20
    TIMEFRAME: str = "5m"
    LOOKBACK_PERIOD: int = 30

    def __post_init__(self):
        self.SCAN_INTERVALS = {
            "STRONG_BULL": 3,
            "BULL": 10,
            "STRONG_BEAR": 10,
            "BEAR": 15,
            "VOLATILE": 5,
            "NORMAL": 10,
            "FLAT": 30,
            "UNKNOWN": 30,
        }
        self.MAX_POSITIONS_BY_REGIME = {
            "STRONG_BULL": 15,
            "BULL": 12,
            "STRONG_BEAR": 8,
            "BEAR": 10,
            "VOLATILE": 10,
            "NORMAL": 10,
            "FLAT": 8,
            "UNKNOWN": 8,
        }


@dataclass
class RiskConfig:
    """Risk management configuration"""

    BASE_RISK_PER_TRADE: float = 0.02  # 2% base
    MIN_RISK_PER_TRADE: float = 0.005  # 0.5% minimum
    MAX_RISK_PER_TRADE: float = 0.05  # 5% maximum
    STOP_LOSS_PCT: float = 0.05  # 5% stop loss (aggressive)
    TAKE_PROFIT_PCT: float = 0.015  # 1.5% take profit
    MIN_PROFIT_BUFFER: float = 0.50  # $0.50 minimum USDT profit to cover fees + buffer
    FEE_BUDGET_DAILY: float = 0.0001  # 0.01% of portfolio for fees
    PORTFOLIO_HEAT: float = 0.60  # 60% (max portfolio exposure) - USE CAPITAL!
    MAX_PORTFOLIO_RISK: float = 0.6  # 60% (max portfolio exposure)


@dataclass
class IntelligenceConfig:
    """Intelligence/threshold configuration"""

    AGI_CONFIDENCE_THRESHOLD: float = 0.70
    MIN_VIABLE_TARGET: float = 0.008  # 1.5% (minimum viable target to cover fees)
    CROSS_EXCHANGE_LEAD_THRESHOLD: float = 0.002  # 0.2%
    INTELLIGENCE_GAP_THRESHOLD: int = 10
    SAME_SCORE_PROTECTION_THRESHOLD: int = 5


@dataclass
class AlphaRecyclingConfig:
    """Alpha recycling configuration"""

    GOD_TIER_SCORE: int = 95
    MIN_RECYCLING_SCORE: int = 85
    MIN_SCORE_VARIANCE: int = 5
    INTELLIGENCE_GAP_AGGRESSIVE: int = 10  # Aggressive recycling
    INTELLIGENCE_GAP_CONSERVATIVE: int = 10  # Standard gap
    DUST_VALUE_THRESHOLD: float = 5.0


@dataclass
class PrecisionExecutionConfig:
    """Precision execution configuration for better entry/exit quality"""

    MAX_WAIT_SECONDS: float = 5.0  # Max time to wait for better entry
    MIN_PRICE_IMPROVEMENT_PCT: float = 0.02  # 0.02% min improvement to wait
    SPREAD_THRESHOLD_TIGHT: float = 0.05  # <0.05% = tight, market order
    SPREAD_THRESHOLD_MODERATE: float = 0.15  # <0.15% = limit order

    TARGET_AVG_SL_PCT: float = 0.02  # 2% average stop across all trades
    ATR_MULTIPLIER_TIGHT: float = 1.0  # Low volatility
    ATR_MULTIPLIER_NORMAL: float = 1.5  # Normal volatility
    ATR_MULTIPLIER_WIDE: float = 2.0  # High volatility
    MIN_SL_PCT: float = 0.005  # 0.5% minimum
    MAX_SL_PCT: float = 0.04  # 4% maximum

    TRAILING_ACTIVATION_PCT: float = 1.0  # Start trailing at +1%
    TRAILING_50_PCT_LEVEL: float = 2.0  # Trail at 50% at +2%
    TRAILING_70_PCT_LEVEL: float = 3.0  # Trail at 70% at +3%


@dataclass
class ExecutionConfig:
    """Execution limits and parallelization settings"""

    TOP_CANDIDATES_LIMIT: int = 25
    PRIORITY_SYMBOLS_LIMIT: int = 30
    PARALLEL_ANALYSIS_SIZE: int = 5
    MIN_TRADE_VALUE: float = 0.10
    DECAY_TIMEOUT_SECONDS: int = 7200
    MARKET_PRIMED_MULTIPLIER: float = 1.5


@dataclass
class MultiplierConfig:
    """Position sizing multipliers based on score thresholds"""

    GOD_TIER_MULTIPLIER: float = 4.0  # Score >= 95
    HIGH_CONFIDENCE_MULTIPLIER: float = 3.0  # Score >= 90
    STRONG_SETUP_MULTIPLIER: float = 2.0  # Score >= 85
    GOOD_SETUP_MULTIPLIER: float = 1.5  # Score >= 80
    STANDARD_MULTIPLIER: float = 1.0  # Score < 80

    REGIME_TRENDING_MULTIPLIER: float = 1.25  # Bull trending market
    REGIME_FLAT_MULTIPLIER: float = 0.75  # Flat/range-bound market
    REGIME_DEFAULT_MULTIPLIER: float = 1.0  # Normal/volatile markets

    MARKET_PRIMED_MULTIPLIER: float = 1.5  # Multiplier when market is primed
    BASE_SIZE_PCT: float = 0.25  # Base position size percentage


@dataclass
class FilterConfig:
    """Symbol filtering configuration"""

    MIN_LIQUIDITY: int = 1000
    MAX_SPREAD: float = 0.02
    STABLECOINS: set = field(default_factory=lambda: {"USDT", "USDC", "DAI", "BUSD"})
    IGNORED_SYMBOLS: set = field(default_factory=lambda: set())


@dataclass
class IBISTradingConstants:
    """Master configuration class - import this for all thresholds"""

    EXCHANGE: ExchangeConfig = field(default_factory=ExchangeConfig)
    CRITICAL: CriticalThresholds = field(default_factory=CriticalThresholds)
    SCORE: ScoreThresholds = field(default_factory=ScoreThresholds)
    POSITION: PositionConfig = field(default_factory=PositionConfig)
    SCAN: ScanConfig = field(default_factory=ScanConfig)
    RISK: RiskConfig = field(default_factory=RiskConfig)
    INTELLIGENCE: IntelligenceConfig = field(default_factory=IntelligenceConfig)
    ALPHA: AlphaRecyclingConfig = field(default_factory=AlphaRecyclingConfig)
    PRECISION: PrecisionExecutionConfig = field(
        default_factory=PrecisionExecutionConfig
    )
    EXECUTION: ExecutionConfig = field(default_factory=ExecutionConfig)
    MULTIPLIERS: MultiplierConfig = field(default_factory=MultiplierConfig)
    FILTER: FilterConfig = field(default_factory=FilterConfig)

    def get_total_friction(self) -> float:
        return self.EXCHANGE.get_total_friction()

    def get_scan_interval(self, regime: str) -> int:
        return self.SCAN.SCAN_INTERVALS.get(regime, self.SCAN.DEFAULT_SCAN_INTERVAL)

    def get_max_positions(self, regime: str) -> int:
        return self.SCAN.MAX_POSITIONS_BY_REGIME.get(
            regime, self.SCAN.DEFAULT_MAX_POSITIONS
        )

    def get_standard_position_size(self, capital: float) -> float:
        min_size = self.POSITION.MIN_CAPITAL_PER_TRADE
        max_size = capital * self.POSITION.MAX_POSITION_PCT / 100
        base_size = capital * self.POSITION.BASE_POSITION_PCT / 100
        return min(max(base_size, min_size), max_size)


# Global instance
TRADING = IBISTradingConstants()
SCORE_THRESHOLDS = TRADING.SCORE
POSITION_CONFIG = TRADING.POSITION
RISK_CONFIG = TRADING.RISK
EXECUTION_CONFIG = TRADING.EXECUTION
MULTIPLIER_CONFIG = TRADING.MULTIPLIERS
FILTER_CONFIG = TRADING.FILTER
