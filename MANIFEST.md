# IBIS Python File Manifest

Scope: repository Python files from `rg --files -g "*.py"`.

## Tier Definitions

- **Tier-1**: Direct runtime critical path for the live `ibis_true_agent.py` loop (dependency closure)
- **Tier-2**: Supporting/operational code not in direct live loop
- **Tier-3**: Non-runtime development artifacts (tests, diagnostics, sandbox, examples, backtest helpers)

## File Count

**177 total files** | **24 Tier-1** | **64 Tier-2** | **89 Tier-3**

## File List

### Tier-1 Files (Runtime Critical)

| File | Purpose |
|------|---------|
| `ibis_true_agent.py` | Main trading agent loop |
| `ibis/brain/agi_brain.py` | AGI brain for decision making |
| `ibis/core/config.py` | Configuration management |
| `ibis/core/trading_constants.py` | Trading constants and thresholds |
| `ibis/core/unified_scoring.py` | Unified opportunity scoring system |
| `ibis/cross_exchange_monitor.py` | Cross-exchange validation (Binance) |
| `ibis/data_consolidation.py` | Data consolidation and processing |
| `ibis/database/db.py` | Database operations |
| `ibis/enhanced_intel.py` | Enhanced intelligence gathering |
| `ibis/exchange/ccxt_client.py` | CCXT exchange integration |
| `ibis/exchange/kucoin_client.py` | KuCoin exchange API integration |
| `ibis/free_intelligence.py` | Free intelligence sources (Fear & Greed, etc.) |
| `ibis/indicators/indicators.py` | Technical indicators (RSI, MACD, etc.) |
| `ibis/intelligence/adaptive_intelligence.py` | Adaptive intelligence system |
| `ibis/intelligence/advanced_signal_processor.py` | Advanced signal processing |
| `ibis/intelligence/enhanced_sniping.py` | Enhanced sniping strategy |
| `ibis/intelligence/error_handler.py` | Error handling and recovery |
| `ibis/intelligence/market_intel.py` | Market intelligence analysis |
| `ibis/intelligence/monitoring.py` | System monitoring |
| `ibis/intelligence/multi_source_correlator.py` | Multi-source intelligence correlation |
| `ibis/intelligence/quality_assurance.py` | Data quality assurance |
| `ibis/intelligence/real_time_optimizer.py` | Real-time optimization |
| `ibis/market_intelligence.py` | Comprehensive market intelligence |
| `ibis/pnl_tracker.py` | Profit and loss tracking |

### Tier-2 Files (Supporting/Operational)

| File | Purpose |
|------|---------|
| `ibis/__init__.py` | Package initialization |
| `ibis/agent_controller.py` | Agent control interface |
| `ibis/agent_server.py` | Agent server functionality |
| `ibis/aggregator.py` | Data aggregation |
| `ibis/analytics.py` | Analytics and reporting |
| `ibis/brain/__init__.py` | AGI brain package |
| `ibis/brain/llm_engine.py` | LLM engine integration |
| `ibis/brain/local_reasoning.py` | Local reasoning capabilities |
| `ibis/cognition/__init__.py` | Cognition package |
| `ibis/cognition/cognition.py` | Cognitive functions |
| `ibis/core/__init__.py` | Core package |
| `ibis/core/risk_manager.py` | Risk management system |
| `ibis/data/__init__.py` | Data package |
| `ibis/exchange/__init__.py` | Exchange integration package |
| `ibis/exchange/data_feed.py` | Market data feed |
| `ibis/exchange/trade_executor.py` | Trade execution |
| `ibis/execution/engine.py` | Execution engine |
| `ibis/execution/engine_v2.py` | Enhanced execution engine |
| `ibis/intel_enhancement.py` | Intelligence enhancement |
| `ibis/intelligence/__init__.py` | Intelligence package |
| `ibis/market_cache.py` | Market data cache |
| `ibis/market_funnel.py` | Market filtering and selection |
| `ibis/memory/__init__.py` | Memory package |
| `ibis/memory/memory.py` | Memory management |
| `ibis/microstructure.py` | Market microstructure analysis |
| `ibis/notifications/__init__.py` | Notifications package |
| `ibis/notifications/alert.py` | Alert system |
| `ibis/notifications/notifier.py` | Notification management |
| `ibis/optimization/__init__.py` | Optimization package |
| `ibis/orchestrator.py` | Execution orchestration |
| `ibis/position_rotation.py` | Position rotation strategy |
| `ibis/regime.py` | Market regime detection |
| `ibis/scalping/__init__.py` | Scalping strategy package |
| `ibis/scalping/entry_optimizer.py` | Entry point optimization |
| `ibis/scalping/liquidity_detector.py` | Liquidity detection |
| `ibis/scalping/momentum_sniper.py` | Momentum sniping |
| `ibis/scalping/order_flow.py` | Order flow analysis |
| `ibis/scalping/smart_stops.py` | Smart stop loss management |
| `ibis/setup_live.py` | Live trading setup |
| `ibis/state_sync.py` | State synchronization |
| `ibis/storage.py` | Data storage management |
| `ibis/strategies/base.py` | Strategy base classes |
| `ibis/strategies/swing.py` | Swing trading strategy |
| `ibis/strategies/swing_native.py` | Native swing strategy |
| `ibis/system_health.py` | System health monitoring |
| `ibis/telemetry.py` | Telemetry and metrics |
| `ibis/ui/__init__.py` | UI package |
| `ibis/ui/animations.py` | UI animations |
| `ibis/ui/charts.py` | Chart components |
| `ibis/ui/colors.py` | Color management |
| `ibis/ui/components.py` | UI components |
| `ibis/ui/dashboards/__init__.py` | Dashboards package |
| `ibis/ui/dashboards/textual_enhanced.py` | Enhanced textual dashboard |
| `ibis/ui/dashboards/ultimate.py` | Ultimate dashboard |
| `ibis/ui/icons.py` | UI icons |
| `ibis_watchdog.py` | Agent watchdog monitor |
| `main.py` | Main entry point |
| `monitor_agent.py` | Agent monitoring |
| `tools/deep_state_audit.py` | Deep state audit |
| `tools/monitor_performance.py` | Performance monitoring |
| `tools/project_dashboard.py` | Project dashboard |
| `tools/reconcile_state_db.py` | State/db reconciliation |
| `update_positions.py` | Position updates |

### Tier-3 Files (Development/Testing)

#### Examples
- `examples/basic_usage/view_state.py`

#### Backtesting
- `ibis/backtest/__init__.py`
- `ibis/backtest/apply_learning.py`
- `ibis/backtest/backtester.py`
- `ibis/backtest/learning.py`
- `ibis/backtest/run_learning.py`
- `ibis/backtest/run_long_learning.py`
- `ibis/backtest/run_real_learning.py`

#### Tests - Archive
- `tests/archive/comprehensive_audit.py`
- `tests/archive/run_intelligence_test.py`
- `tests/archive/test_candle_analysis.py`
- `tests/archive/test_enhancements.py`
- `tests/archive/test_ibis.py`
- `tests/archive/test_ibis_internal.py`
- `tests/archive/test_ibis_true.py`
- `tests/archive/test_intelligence.py`
- `tests/archive/test_kucoin_client.py`
- `tests/archive/test_new_intel.py`
- `tests/archive/test_new_intelligence.py`
- `tests/archive/test_price_fixes.py`
- `tests/archive/test_simple.py`
- `tests/archive/verify_api_internal.py`
- `tests/archive/verify_kucoin_orders.py`
- `tests/archive/verify_optimizations.py`

#### Tests - Diagnostics
- `tests/diagnostics/check_agent_activity.py`
- `tests/diagnostics/check_config.py`
- `tests/diagnostics/check_intel.py`
- `tests/diagnostics/check_meme_scores.py`
- `tests/diagnostics/check_open_order.py`
- `tests/diagnostics/check_order_dict.py`
- `tests/diagnostics/check_performance.py`
- `tests/diagnostics/check_system.py`
- `tests/diagnostics/check_system_fixed.py`
- `tests/diagnostics/comprehensive_verification.py`
- `tests/diagnostics/debug_adi_priority.py`
- `tests/diagnostics/debug_analysis.py`
- `tests/diagnostics/debug_analyze_intel.py`
- `tests/diagnostics/debug_balances.py`
- `tests/diagnostics/debug_execution.py`
- `tests/diagnostics/debug_opportunity_filtering.py`
- `tests/diagnostics/debug_priority.py`
- `tests/diagnostics/debug_priority_origin.py`
- `tests/diagnostics/debug_scores.py`
- `tests/diagnostics/debug_state.py`
- `tests/diagnostics/diagnose_symbol_discovery.py`
- `tests/diagnostics/verify_adi_holding.py`
- `tests/diagnostics/verify_data_fetching.py`
- `tests/diagnostics/verify_final.py`
- `tests/diagnostics/verify_fix.py`
- `tests/diagnostics/verify_kucoin_trades.py`
- `tests/diagnostics/verify_momentum.py`
- `tests/diagnostics/verify_pure_data.py`

#### Tests - Sandbox
- `tests/sandbox/execute_final.py`
- `tests/sandbox/execute_fixed.py`
- `tests/sandbox/execute_opportunity.py`
- `tests/sandbox/execute_tick_fix.py`
- `tests/sandbox/execute_with_tick.py`
- `tests/sandbox/fix_agent_activity.py`
- `tests/sandbox/fix_capital_state.py`
- `tests/sandbox/fix_state_directly.py`
- `tests/sandbox/fix_state_file.py`
- `tests/sandbox/force_execution_check.py`
- `tests/sandbox/ibis_enhanced_20x.py`
- `tests/sandbox/ibis_enhanced_integration.py`
- `tests/sandbox/ibis_fast.py`
- `tests/sandbox/ibis_health_check.py`
- `tests/sandbox/ibis_phase1_optimizations.py`
- `tests/sandbox/ibis_true_health.py`
- `tests/sandbox/ibis_true_monitor.py`
- `tests/sandbox/monitor_ibis.py`
- `tests/sandbox/quick_portfolio_check.py`
- `tests/sandbox/real_time_updater.py`
- `tests/sandbox/review_portfolio.py`
- `tests/sandbox/simple_debug.py`
- `tests/sandbox/simple_symbol_diagnostic.py`
- `tests/sandbox/websocket_data_feed.py`

#### Tests - Main
- `tests/audit_ibis.py`
- `tests/test_agi_core.py`
- `tests/test_agi_enhancements.py`
- `tests/test_enhanced.py`
- `tests/test_hyper_mode.py`
- `tests/test_hypertrading.py`
- `tests/unit/quick_test.py`
- `tests/unit/test_agent_fix.py`
- `tests/unit/test_final_trade_logic.py`
- `tests/unit/test_intelligence_streams.py`
- `tests/unit/test_real_data.py`
- `tests/unit/test_realtime_flow.py`
- `tests/unit/test_rotation.py`

## Recent Additions (2026-02-17)

### New Files
- `ibis/exchange/kucoin_websocket.py` - WebSocket integration for real-time market data
- `tools/liquidity_trade_audit.py` - Liquidity and trade audit tool
- `verify_untested_components.py` - Component testing and verification

### Updated Files
- Modified: `data/trade_history.json` - Updated trade history format
- Modified: `docs/CONFIG.md` - Enhanced configuration documentation
- Modified: `ibis/config.json` - Added trading mode configurations
- Modified: `ibis/core/trading_constants.py` - Updated trading thresholds
- Modified: `ibis/database/db.py` - Enhanced database operations
- Modified: `ibis/exchange/kucoin_client.py` - WebSocket integration
- Modified: `ibis/pnl_tracker.py` - Improved PnL calculation
- Modified: `ibis/state_sync.py` - Enhanced state synchronization
- Modified: `ibis_true_agent.py` - Core agent fixes and improvements
- Modified: `pyproject.toml` - Updated dependencies
- Modified: `tools/sync_trade_history_to_db.py` - Trade history syncing
- Modified: `tools/truth_snapshot.py` - Enhanced market data snapshot