"""
IBIS Intelligence Module - AGI Market Analysis
By TheOsirisLabs.com | Founder: Youssef SalahEldin

Multi-dimensional market intelligence for true AGI trading:
- Market Intelligence (comprehensive analysis)
- Low Cap Discovery (opportunity finding)
- Advanced Risk Management
- Regime Detection
- Enhanced Signal Processing
- Multi-Source Correlation
- Real-Time Optimization
- Error Handling & Fallbacks
- Adaptive Intelligence
- Comprehensive Monitoring
"""

from .market_intel import (
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

from .quality_assurance import (
    DataQualityAssurance,
    IntelligenceCleansingPipeline,
    intelligence_qa,
    cleansing_pipeline,
)

from .advanced_signal_processor import (
    AdvancedSignalProcessor,
    SignalQualityScorer,
    CorrelationAnalyzer,
    PatternRecognizer,
    advanced_signal_processor,
    signal_quality_scorer,
)

from .multi_source_correlator import (
    MultiSourceCorrelationSystem,
    SignalFusionEngine,
    CorrelationAnalyzer,
    ConsensusDetector,
    PatternMatcher,
    multi_source_correlator,
    signal_fusion_engine,
)

from .real_time_optimizer import (
    RealTimeProcessor,
    TaskPriorityQueue,
    AsyncDataFetcher,
    StreamingBuffer,
    PerformanceOptimizer,
    real_time_processor,
    async_data_fetcher,
    performance_optimizer,
)

from .error_handler import (
    ErrorHandler,
    CircuitBreaker,
    RetryManager,
    SystemHealthMonitor,
    error_handler,
    circuit_breaker,
    retry_manager,
    health_monitor,
)

from .adaptive_intelligence import (
    MarketConditionDetector,
    AdaptiveSignalProcessor,
    AdaptiveSourceAllocator,
    market_condition_detector,
    adaptive_signal_processor,
    adaptive_source_allocator,
)

from .monitoring import (
    IntelligenceMonitor,
    DebugLogger,
    Profiler,
    DiagnosticTester,
    intelligence_monitor,
    debug_logger,
    profiler,
    diagnostic_tester,
)

__all__ = [
    # Original Components
    "MarketIntelligence",
    "MarketInsight",
    "MarketContext",
    "LowCapDiscovery",
    "CoinOpportunity",
    "AdvancedRiskManager",
    "RegimeDetector",
    "IBISIntelligence",
    "OrderFlowData",
    "VolumeProfile",
    "SentimentData",
    "OnChainData",
    "AnalysisDimension",
    "get_intelligence",
    # Quality Assurance
    "DataQualityAssurance",
    "IntelligenceCleansingPipeline",
    "intelligence_qa",
    "cleansing_pipeline",
    # Advanced Signal Processing
    "AdvancedSignalProcessor",
    "SignalQualityScorer",
    "CorrelationAnalyzer",
    "PatternRecognizer",
    "advanced_signal_processor",
    "signal_quality_scorer",
    # Multi-Source Correlation
    "MultiSourceCorrelationSystem",
    "SignalFusionEngine",
    "ConsensusDetector",
    "PatternMatcher",
    "multi_source_correlator",
    "signal_fusion_engine",
    # Real-Time Optimization
    "RealTimeProcessor",
    "TaskPriorityQueue",
    "AsyncDataFetcher",
    "StreamingBuffer",
    "PerformanceOptimizer",
    "real_time_processor",
    "async_data_fetcher",
    "performance_optimizer",
    # Error Handling
    "ErrorHandler",
    "CircuitBreaker",
    "RetryManager",
    "SystemHealthMonitor",
    "error_handler",
    "circuit_breaker",
    "retry_manager",
    "health_monitor",
    # Adaptive Intelligence
    "MarketConditionDetector",
    "AdaptiveSignalProcessor",
    "AdaptiveSourceAllocator",
    "market_condition_detector",
    "adaptive_signal_processor",
    "adaptive_source_allocator",
    # Monitoring & Debugging
    "IntelligenceMonitor",
    "DebugLogger",
    "Profiler",
    "DiagnosticTester",
    "intelligence_monitor",
    "debug_logger",
    "profiler",
    "diagnostic_tester",
]
