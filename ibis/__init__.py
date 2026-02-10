"""
IBIS AGI Trading Agent Package
By TheOsirisLabs.com | Founder: Youssef SalahEldin

Sacred Bird of Thoth - Hunter of Opportunities
"""

__version__ = "2.0.0"
__author__ = "Youssef SalahEldin"
__license__ = "Proprietary"

from .brain import (
    FreeLLMEngine,
    TradingDecision,
    ModelTier,
    FreeModels,
    get_brain,
    LocalReasoningEngine,
    LocalDecision,
    get_local_reasoning,
    IBISAGIBrain,
    TradeSignal,
    ReasoningModel,
    get_agi_brain,
)

from .memory import IBISMemory, TradeMemory, PatternMemory, RuleMemory, get_memory

from .cognition import (
    IBISCognition,
    ReflectionEngine,
    PlanningEngine,
    MetacognitionEngine,
    AdaptationEngine,
    CognitiveState,
    Thought,
    SelfAssessment,
    Plan,
)

from .intelligence import (
    MarketIntelligence,
    MarketInsight,
    MarketContext,
    LowCapDiscovery,
    CoinOpportunity,
    AdvancedRiskManager,
    RegimeDetector,
    IBISIntelligence,
    OrderFlowData,
    VolumeProfile,
    SentimentData,
    OnChainData,
    AnalysisDimension,
    get_intelligence,
)

from .indicators import (
    IndicatorEngine,
    MovingAverage,
    RSI,
    MACD,
    BollingerBands,
    ATR,
    VWAP,
    Stochastic,
    OBV,
    Ichimoku,
    Fibonacci,
    SupportResistance,
    calculate_indicators,
)

from .exchange import (
    KuCoinClient,
    MarketData,
    TradingClient,
    DataFeed,
    TradeExecutor,
    get_kucoin_client,
    get_data_feed,
    get_trade_executor,
)

from .orchestrator import IBIS, IBISConfig

from .ui import (
    IBISDashboard,
    Colors,
    Icons,
    ChartGenerator,
    ASCIICharts,
    IBISEnhancedApp,
    format_number,
    format_duration,
    format_pnl,
    format_score,
    format_decision,
)

from .data import (
    MarketDataManager,
    KuCoinRESTClient,
    KuCoinWebSocketClient,
    MarketPrice,
    OrderBook,
    Candle,
)

from .backtest import (
    BacktestEngine,
    BacktestResult,
    Strategy,
    BacktestConfig,
    Trade,
)

from .optimization import (
    GeneticOptimizer,
    OptimizationConfig,
    Genome,
)

__all__ = [
    # Version
    "__version__",
    # Orchestrator
    "IBIS",
    "IBISConfig",
    # UI
    "IBISDashboard",
    "Colors",
    "Icons",
    "ChartGenerator",
    "ASCIICharts",
    "IBISEnhancedApp",
    "format_number",
    "format_duration",
    "format_pnl",
    "format_score",
    "format_decision",
    # Data
    "MarketDataManager",
    "KuCoinRESTClient",
    "KuCoinWebSocketClient",
    "MarketPrice",
    "OrderBook",
    "Candle",
    # Backtest
    "BacktestEngine",
    "BacktestResult",
    "Strategy",
    "BacktestConfig",
    "Trade",
    # Optimization
    "GeneticOptimizer",
    "OptimizationConfig",
    "Genome",
]
