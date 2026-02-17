# Development Guide

## Repository Areas

- **Core runtime**: `ibis_true_agent.py`
- **Core modules**: `ibis/` - Contains all intelligence, execution, and utility modules
- **Operations scripts**: `tools/`, `run_*.sh` - Maintenance and monitoring tools
- **Service/timer units**: `deploy/` - Systemd service and timer configurations
- **Runtime data**: `data/` - State files, database, and trade history
- **Tests**: `tests/` - Unit, integration, sandbox, and diagnostic tests

## Safe Workflow

1. Edit code
2. Compile-check touched Python files
3. Run local health checks
4. Restart `ibis-agent.service` only when required
5. Validate with runtime and journal evidence

**Example**:
```bash
python3 -m py_compile ibis_true_agent.py tools/*.py
./run_health_check.sh
./runtime_status.sh
journalctl -u ibis-agent.service --since '10 minutes ago' --no-pager
```

## Runtime-Sensitive Rules

- The service executes `/root/projects/ibis_trader/ibis_true_agent.py`
- In this environment, it resolves to this repository path; verify before editing in new environments
- Avoid parallel agent processes

## Common Development Tasks

### Reconciliation/self-heal
```bash
python3 tools/reconcile_state_db.py --apply
```

### Deep audit with live exchange checks
```bash
python3 tools/deep_state_audit.py --live-exchange
```

### Execution integrity snapshot
```bash
python3 tools/execution_integrity_check.py --live-open-orders
```

### Liquidity trade audit
```bash
python3 tools/liquidity_trade_audit.py
```

### Sync trade history to database
```bash
python3 tools/sync_trade_history_to_db.py --apply
```

## Documentation Discipline

After operational changes, update:
- `docs/OPERATIONS_24_7.md` - System operations
- `docs/TROUBLESHOOTING.md` - Issue resolution
- `docs/CHANGES.md` - Change log
- `docs/ARCHITECTURE.md` - System architecture
- `docs/CONFIG.md` - Configuration reference
- `README.md` - Project overview

Keep docs aligned with actual service/runtime behavior.

## Core Components Development

### Intelligence & Scoring Layer
- **AGI Brain**: `ibis/brain/agi_brain.py` - Multi-model reasoning
- **Unified Scoring**: `ibis/core/unified_scoring.py` - Opportunity scoring
- **Enhanced Sniping**: `ibis/intelligence/enhanced_sniping.py` - Breakout detection
- **Free Intelligence**: `ibis/free_intelligence.py` - Market data sources
- **Enhanced Intelligence**: `ibis/enhanced_intel.py` - Advanced analysis

### Execution Layer
- **Main Agent**: `ibis_true_agent.py` - Core execution logic
- **Exchange Client**: `ibis/exchange/kucoin_client.py` - API integration
- **Execution Engines**: `ibis/execution/engine.py`, `engine_v2.py` - Trade orchestration

### Risk Management
- **Risk Manager**: `ibis/core/risk_manager.py` - Position sizing and limits
- **PNL Tracker**: `ibis/pnl_tracker.py` - Profit/loss calculation
- **Position Rotation**: `ibis/position_rotation.py` - Position management

### Market Data & Analysis
- **Indicators**: `ibis/indicators/indicators.py` - Technical indicators
- **Market Intelligence**: `ibis/market_intelligence.py` - Comprehensive analysis
- **Cross-Exchange Monitor**: `ibis/cross_exchange_monitor.py` - Binance validation

## Testing Framework

### Test Types
- **Unit Tests**: `tests/unit/` - Component-level tests
- **Integration Tests**: `tests/integration/` - System integration tests
- **Diagnostic Tests**: `tests/diagnostics/` - Troubleshooting and debugging
- **Sandbox Tests**: `tests/sandbox/` - Live testing with real data
- **AGI Tests**: `tests/test_agi_core.py`, `tests/test_agi_enhancements.py` - AI components

### Running Tests
```bash
# Run all tests
pytest tests/

# Run specific test file
pytest tests/test_agi_core.py

# Run tests with coverage
pytest tests/ -v -x --tb=short

# Run tests in parallel
pytest tests/ -n 4
```

## Backtesting

### Historical Strategy Testing
```bash
cd tests/sandbox/
python3 ibis_enhanced_integration.py
```

### Strategy Performance Analysis
```bash
python3 -c "
from ibis.backtest.backtester import Backtester
bt = Backtester()
results = bt.run_strategy('RSI', symbol='BTC-USDT', timeframe='1h', lookback=30)
print(f'Win Rate: {results[\"win_rate\"]:.2%}')
print(f'Profit Factor: {results[\"profit_factor\"]:.2f}')
print(f'Max Drawdown: {results[\"max_drawdown\"]:.2%}')
"
```

## Performance Optimization

### Profiling Tools
```bash
# Install profiling tools
pip3 install line_profiler memory_profiler

# Run with CPU profiler
python3 -m cProfile -o profile.stats ibis_true_agent.py

# Run with line profiler
kernprof -l -v ibis_true_agent.py

# Run with memory profiler
python -m memory_profiler ibis_true_agent.py
```

### Code Quality
```bash
# Run black formatter
black .

# Run flake8 linter
flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
flake8 . --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics

# Run mypy type checker
mypy ibis_true_agent.py ibis/
```

## Dependency Management

### Install Dependencies
```bash
pip3 install -r requirements.txt
pip3 install -r ibis/requirements.txt
```

### Check for Updates
```bash
pip3 list --outdated
```

### Freeze Dependencies
```bash
pip3 freeze > requirements.txt
```

## Security Best Practices

1. **Credentials Management**:
   - Keep `ibis/keys.env` permissions at 600
   - Use separate API keys for development and production
   - Rotate API keys periodically

2. **Code Security**:
   - Avoid hardcoding sensitive information
   - Validate all user inputs
   - Use secure communication protocols

3. **System Security**:
   - Keep system packages updated
   - Use firewalls and intrusion detection
   - Regularly audit file permissions

## Development Environment Setup

### Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate
pip3 install -r requirements.txt
pip3 install -r ibis/requirements.txt
```

### Environment Variables
```bash
# Development mode
export DEBUG=true
export VERBOSE=true
export PAPER_TRADING=true
```

## Common Development Scenarios

### Adding New Intelligence Source
1. Create new module in `ibis/intelligence/`
2. Implement data acquisition and processing
3. Add scoring logic to `unified_scoring.py`
4. Test integration in sandbox environment
5. Update documentation

### Modifying Trading Strategy
1. Edit strategy in `ibis/strategies/` or `ibis/core/trading_constants.py`
2. Test strategy in backtesting framework
3. Validate with historical data
4. Implement changes in production cautiously
5. Monitor performance closely