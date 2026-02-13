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

    MIN_VIABLE_TARGET: float = 0.005  # 0.5% minimum viable target
    MIN_CAPITAL_PER_TRADE: float = 11.0  # Min USD per position
    MAX_CAPITAL_PER_TRADE: float = 100.0  # Max USD per position
    MAX_POSITIONS: int = 25  # More positions for more opportunities
    MIN_SCORE_THRESHOLD: float = 0.25  # 25% - more aggressive in strong market


@dataclass
class ScoreThresholds:
    """Opportunity scoring thresholds"""

    GOD_TIER: int = 90  # Exceptional
    HIGH_CONFIDENCE: int = 85  # High confidence
    STRONG_SETUP: int = 80  # Strong setup
    GOOD_SETUP: int = 75  # Good opportunity
    STANDARD: int = 70  # Standard opportunity
    MIN_THRESHOLD: int = 65  # Minimum to consider
    MARKET_PRIMED_HIGH_COUNT: int = 5  # Number of high-scoring symbols for "primed" mode
    MARKET_PRIMED_AVG_SCORE: int = 70  # Lowered to be more aggressive

    def __post_init__(self):
        if not (
            0
            <= self.MIN_THRESHOLD
            < self.STANDARD
            < self.GOOD_SETUP
            < self.STRONG_SETUP
            < self.HIGH_CONFIDENCE
            < self.GOD_TIER
            <= 100
        ):
            raise ValueError("Score thresholds must be in increasing order from 0-100")
        if self.MARKET_PRIMED_HIGH_COUNT <= 0 or self.MARKET_PRIMED_HIGH_COUNT > 50:
            raise ValueError(
                f"MARKET_PRIMED_HIGH_COUNT ({self.MARKET_PRIMED_HIGH_COUNT}) must be between 1-50"
            )
        if (
            self.MARKET_PRIMED_AVG_SCORE < self.MIN_THRESHOLD
            or self.MARKET_PRIMED_AVG_SCORE > self.GOD_TIER
        ):
            raise ValueError(
                f"MARKET_PRIMED_AVG_SCORE ({self.MARKET_PRIMED_AVG_SCORE}) must be between {self.MIN_THRESHOLD} and {self.GOD_TIER}"
            )


@dataclass
class PositionConfig:
    """Position-related configuration - AGGRESSIVE CAPITAL UTILIZATION"""

    MAX_TOTAL_POSITIONS: int = 25  # Max concurrent positions
    MIN_CAPITAL_PER_TRADE: float = 11.0  # $11 minimum per trade
    FINAL_TRADE_MIN_CAPITAL: float = 11.0  # $11 minimum for final trade
    MAX_CAPITAL_PER_TRADE: float = 100.0  # $100 maximum per trade (for higher volume)
    MAX_POSITION_PCT: float = 90.0  # 90% max of portfolio per position
    BASE_POSITION_PCT: float = 75.0  # 75% base per position (MAXIMUM UTILIZATION!)

    def __post_init__(self):
        if self.MIN_CAPITAL_PER_TRADE < 11.0:
            self.MIN_CAPITAL_PER_TRADE = 11.0
        if self.FINAL_TRADE_MIN_CAPITAL < 11.0:
            self.FINAL_TRADE_MIN_CAPITAL = 11.0

        # Validate position percentage limits
        if self.BASE_POSITION_PCT < 10.0 or self.BASE_POSITION_PCT > 100.0:
            raise ValueError(
                f"BASE_POSITION_PCT must be between 10-100%, got {self.BASE_POSITION_PCT}"
            )
        if self.MAX_POSITION_PCT < self.BASE_POSITION_PCT or self.MAX_POSITION_PCT > 100.0:
            raise ValueError(
                f"MAX_POSITION_PCT must be between {self.BASE_POSITION_PCT}-100%, got {self.MAX_POSITION_PCT}"
            )
        if self.MAX_CAPITAL_PER_TRADE < self.MIN_CAPITAL_PER_TRADE:
            raise ValueError(
                f"MAX_CAPITAL_PER_TRADE ({self.MAX_CAPITAL_PER_TRADE}) must be >= MIN_CAPITAL_PER_TRADE ({self.MIN_CAPITAL_PER_TRADE})"
            )


@dataclass
class ScanConfig:
    """Scanning configuration"""

    DEFAULT_SCAN_INTERVAL: int = 5  # Faster scanning for quick opportunities
    DEFAULT_MAX_POSITIONS: int = 25  # More positions to utilize all capital
    TIMEFRAME: str = "1min"  # 1-minute timeframe for fast trading
    LOOKBACK_PERIOD: int = 15  # Shorter lookback for quicker analysis

    def __post_init__(self):
        self.SCAN_INTERVALS = {
            "STRONG_BULL": 2,  # Ultra-fast scanning in strong bull
            "BULL": 5,
            "STRONG_BEAR": 8,
            "BEAR": 10,
            "VOLATILE": 3,  # Very fast in volatile conditions
            "NORMAL": 5,
            "FLAT": 10,
            "UNKNOWN": 10,
            "PERFECT": 1,  # Extreme fast scanning in perfect conditions
        }
        self.MAX_POSITIONS_BY_REGIME = {
            "STRONG_BULL": 25,  # Max positions to use all capital
            "BULL": 20,
            "STRONG_BEAR": 15,
            "BEAR": 18,
            "VOLATILE": 22,  # More positions in volatile markets
            "NORMAL": 20,
            "FLAT": 15,
            "UNKNOWN": 18,
            "PERFECT": 30,  # Maximum positions in perfect conditions
        }
        # Order type by regime: True = MARKET, False = LIMIT
        self.MARKET_ORDERS_BY_REGIME = {
            "STRONG_BULL": True,  # Bull = market for speed
            "BULL": True,
            "STRONG_BEAR": True,  # Bear = market for speed
            "BEAR": True,
            "VOLATILE": True,  # Volatile = market for speed
            "NORMAL": True,  # Normal = market for speed
            "FLAT": True,
            "UNKNOWN": True,
            "PERFECT": True,  # PERFECT = ALWAYS MARKET for max speed
        }
        # Capital deployment % by regime
        self.CAPITAL_DEPLOYMENT_BY_REGIME = {
            "STRONG_BULL": 0.95,  # 95% in strong bull
            "BULL": 0.90,
            "STRONG_BEAR": 0.85,  # 85% in strong bear (still aggressive)
            "BEAR": 0.90,
            "VOLATILE": 0.95,  # 95% in volatile conditions
            "NORMAL": 0.90,
            "FLAT": 0.80,
            "UNKNOWN": 0.85,
            "PERFECT": 0.98,  # 98% in perfect conditions (maximum utilization)
        }


@dataclass
class RiskConfig:
    """Risk management configuration"""

    BASE_RISK_PER_TRADE: float = 0.02  # 2% base
    MIN_RISK_PER_TRADE: float = 0.005  # 0.5% minimum
    MAX_RISK_PER_TRADE: float = 0.05  # 5% maximum
    STOP_LOSS_PCT: float = 0.05  # 5% stop loss (aggressive)
    TAKE_PROFIT_PCT: float = 0.008  # 0.8% take profit (optimized for quick in-and-out)
    MIN_PROFIT_BUFFER: float = 0.0  # No minimum profit requirement
    FEE_BUDGET_DAILY: float = 0.0001  # 0.01% of portfolio for fees
    PORTFOLIO_HEAT: float = 0.95  # 95% (maximum capital utilization)
    MAX_PORTFOLIO_RISK: float = 0.95  # 95% (maximum portfolio exposure)

    def __post_init__(self):
        if self.MIN_RISK_PER_TRADE < 0 or self.MIN_RISK_PER_TRADE > self.BASE_RISK_PER_TRADE:
            raise ValueError(
                f"MIN_RISK_PER_TRADE ({self.MIN_RISK_PER_TRADE}) must be between 0 and {self.BASE_RISK_PER_TRADE}"
            )
        if self.MAX_RISK_PER_TRADE < self.BASE_RISK_PER_TRADE or self.MAX_RISK_PER_TRADE > 0.5:
            raise ValueError(
                f"MAX_RISK_PER_TRADE ({self.MAX_RISK_PER_TRADE}) must be between {self.BASE_RISK_PER_TRADE} and 0.5"
            )
        if self.PORTFOLIO_HEAT < 0 or self.PORTFOLIO_HEAT > 1.0:
            raise ValueError(f"PORTFOLIO_HEAT ({self.PORTFOLIO_HEAT}) must be between 0-1.0")
        if self.STOP_LOSS_PCT <= 0 or self.STOP_LOSS_PCT > 0.2:
            raise ValueError(f"STOP_LOSS_PCT ({self.STOP_LOSS_PCT}) must be between 0-0.2")
        if self.TAKE_PROFIT_PCT <= 0 or self.TAKE_PROFIT_PCT > 0.5:
            raise ValueError(f"TAKE_PROFIT_PCT ({self.TAKE_PROFIT_PCT}) must be between 0-0.5")


@dataclass
class IntelligenceConfig:
    """Intelligence/threshold configuration"""

    AGI_CONFIDENCE_THRESHOLD: float = 0.70
    MIN_VIABLE_TARGET: float = 0.005  # 0.5% (minimum viable target for quick profits)
    CROSS_EXCHANGE_LEAD_THRESHOLD: float = 0.002  # 0.2%
    INTELLIGENCE_GAP_THRESHOLD: int = 10
    SAME_SCORE_PROTECTION_THRESHOLD: int = 5
    MIN_SYMBOL_QUALITY_THRESHOLD: int = 70  # Minimum score for symbols to be analyzed

    def __post_init__(self):
        if self.AGI_CONFIDENCE_THRESHOLD < 0 or self.AGI_CONFIDENCE_THRESHOLD > 1.0:
            raise ValueError(
                f"AGI_CONFIDENCE_THRESHOLD ({self.AGI_CONFIDENCE_THRESHOLD}) must be between 0-1.0"
            )
        if self.MIN_VIABLE_TARGET <= 0 or self.MIN_VIABLE_TARGET > 0.1:
            raise ValueError(f"MIN_VIABLE_TARGET ({self.MIN_VIABLE_TARGET}) must be between 0-0.1")
        if self.CROSS_EXCHANGE_LEAD_THRESHOLD < 0 or self.CROSS_EXCHANGE_LEAD_THRESHOLD > 0.05:
            raise ValueError(
                f"CROSS_EXCHANGE_LEAD_THRESHOLD ({self.CROSS_EXCHANGE_LEAD_THRESHOLD}) must be between 0-0.05"
            )
        if self.INTELLIGENCE_GAP_THRESHOLD < 0 or self.INTELLIGENCE_GAP_THRESHOLD > 100:
            raise ValueError(
                f"INTELLIGENCE_GAP_THRESHOLD ({self.INTELLIGENCE_GAP_THRESHOLD}) must be between 0-100"
            )
        if self.SAME_SCORE_PROTECTION_THRESHOLD < 0 or self.SAME_SCORE_PROTECTION_THRESHOLD > 50:
            raise ValueError(
                f"SAME_SCORE_PROTECTION_THRESHOLD ({self.SAME_SCORE_PROTECTION_THRESHOLD}) must be between 0-50"
            )


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

    MAX_WAIT_SECONDS: float = 0.0  # No waiting - immediate execution
    MIN_PRICE_IMPROVEMENT_PCT: float = 0.0  # No price improvement required
    SPREAD_THRESHOLD_TIGHT: float = 0.10  # <0.10% = tight, market order
    SPREAD_THRESHOLD_MODERATE: float = 0.20  # <0.20% = limit order

    TARGET_AVG_SL_PCT: float = 0.03  # 3% average stop across all trades
    ATR_MULTIPLIER_TIGHT: float = 1.0  # Low volatility
    ATR_MULTIPLIER_NORMAL: float = 1.5  # Normal volatility
    ATR_MULTIPLIER_WIDE: float = 2.0  # High volatility
    MIN_SL_PCT: float = 0.01  # 1% minimum
    MAX_SL_PCT: float = 0.05  # 5% maximum

    # No trailing stops for hyper-frequency trading
    TRAILING_ACTIVATION_PCT: float = 0.0
    TRAILING_50_PCT_LEVEL: float = 0.0
    TRAILING_70_PCT_LEVEL: float = 0.0


@dataclass
class ExecutionConfig:
    """Execution limits and parallelization settings"""

    TOP_CANDIDATES_LIMIT: int = 20  # More candidates for more opportunities
    PRIORITY_SYMBOLS_LIMIT: int = 20  # More symbols for faster discovery
    PARALLEL_ANALYSIS_SIZE: int = 15  # Increased for faster parallel processing
    MIN_TRADE_VALUE: float = 11.0  # Match minimum capital per trade
    DECAY_TIMEOUT_SECONDS: int = 300  # 5 minutes max holding time for quick trades
    MARKET_PRIMED_MULTIPLIER: float = 2.0  # More aggressive in primed markets


@dataclass
class MultiplierConfig:
    """Position sizing multipliers based on score thresholds"""

    GOD_TIER_MULTIPLIER: float = 2.0  # Score >= 95
    HIGH_CONFIDENCE_MULTIPLIER: float = 1.8  # Score >= 90
    STRONG_SETUP_MULTIPLIER: float = 1.5  # Score >= 85
    GOOD_SETUP_MULTIPLIER: float = 1.3  # Score >= 80
    STANDARD_MULTIPLIER: float = 1.1  # Score < 80

    REGIME_TRENDING_MULTIPLIER: float = 1.2  # Bull trending market
    REGIME_FLAT_MULTIPLIER: float = 1.0  # Flat/range-bound market
    REGIME_DEFAULT_MULTIPLIER: float = 1.1  # Normal/volatile markets

    MARKET_PRIMED_MULTIPLIER: float = 1.3  # Multiplier when market is primed
    BASE_SIZE_PCT: float = 0.25  # Base position size percentage (25% per trade)


@dataclass
class FilterConfig:
    """Symbol filtering configuration"""

    MIN_LIQUIDITY: int = 50000
    MAX_SPREAD: float = 0.02
    STABLECOINS: set = field(default_factory=lambda: {"USDT", "USDC", "DAI", "BUSD"})
    IGNORED_SYMBOLS: set = field(default_factory=lambda: set())


@dataclass
class TechnicalIndicatorConfig:
    """Technical indicator weights and thresholds"""

    RSI_PERIOD: int = 14
    RSI_OVERSOLD: float = 30.0
    RSI_OVERBOUGHT: float = 70.0
    MACD_FAST: int = 12
    MACD_SLOW: int = 26
    MACD_SIGNAL: int = 9
    BB_PERIOD: int = 20
    BB_STD: float = 2.0
    MA_SHORT: int = 20
    MA_MEDIUM: int = 50
    MA_LONG: int = 200
    ATR_PERIOD: int = 14
    STOCH_K: int = 14
    STOCH_D: int = 3

    WEIGHT_RSI: float = 0.10
    WEIGHT_MACD: float = 0.15
    WEIGHT_BOLLINGER: float = 0.10
    WEIGHT_MA: float = 0.15
    WEIGHT_OBV: float = 0.10
    WEIGHT_STOCH: float = 0.10
    WEIGHT_VWAP: float = 0.10
    WEIGHT_ATR: float = 0.05
    WEIGHT_VOLUME: float = 0.15


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
    PRECISION: PrecisionExecutionConfig = field(default_factory=PrecisionExecutionConfig)
    EXECUTION: ExecutionConfig = field(default_factory=ExecutionConfig)
    MULTIPLIERS: MultiplierConfig = field(default_factory=MultiplierConfig)
    FILTER: FilterConfig = field(default_factory=FilterConfig)
    TECHNICAL: TechnicalIndicatorConfig = field(default_factory=TechnicalIndicatorConfig)

    def get_total_friction(self) -> float:
        return self.EXCHANGE.get_total_friction()

    def get_scan_interval(self, regime: str) -> int:
        return self.SCAN.SCAN_INTERVALS.get(regime, self.SCAN.DEFAULT_SCAN_INTERVAL)

    def get_max_positions(self, regime: str) -> int:
        return self.SCAN.MAX_POSITIONS_BY_REGIME.get(regime, self.SCAN.DEFAULT_MAX_POSITIONS)

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
