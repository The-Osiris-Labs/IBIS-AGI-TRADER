# Architecture

## Runtime Layers (5-Tier Architecture)

```
┌─────────────────────────────────────────────────────────────┐
│  1. Exchange Access Layer (kucoin_client.py)                │
│  - Market data, balances, orders, fills                     │
└─────────────────────────────────────────────────────────────┘
          ↓
┌─────────────────────────────────────────────────────────────┐
│  2. Intelligence & Scoring Layer                            │
│  - Market scanning (ibis_true_agent.py)                     │
│  - Unified scoring (unified_scoring.py)                     │
│  - Enhanced sniping (enhanced_sniping.py)                   │
│  - AGI brain (agi_brain.py)                                │
└─────────────────────────────────────────────────────────────┘
          ↓
┌─────────────────────────────────────────────────────────────┐
│  3. Execution Layer (ibis_true_agent.py)                    │
│  - Order decision and placement                              │
│  - Symbol rule normalization (tick/lot increments)           │
│  - Minimum notional enforcement ($11)                        │
│  - Duplicate-order prevention                                │
└─────────────────────────────────────────────────────────────┘
          ↓
┌─────────────────────────────────────────────────────────────┐
│  4. State & Reconciliation Layer                             │
│  - State: data/ibis_true_state.json                          │
│  - DB: data/ibis_v8.db (SQLite)                             │
│  - Reconciliation tools in tools/ directory                  │
└─────────────────────────────────────────────────────────────┘
          ↓
┌─────────────────────────────────────────────────────────────┐
│  5. Operations & Watchdog Layer                              │
│  - systemd service and timers (deploy/)                      │
│  - Health check & KPI runners                                │
└─────────────────────────────────────────────────────────────┘
```

## Core Components

### 1. Exchange Access Layer
- **File**: `ibis/exchange/kucoin_client.py`
- **Responsibilities**: Market data, balances, orders, fills
- **Features**: Real-time WebSocket data, REST API polling, order book snapshots

### 2. Intelligence & Scoring Layer
- **Market Scanning**: `ibis_true_agent.py`
- **Unified Scoring**: `ibis/core/unified_scoring.py`
- **Enhanced Sniping**: `ibis/intelligence/enhanced_sniping.py`
- **AGI Brain**: `ibis/brain/agi_brain.py`
- **Free Intelligence**: `ibis/intelligence/free_intelligence.py`
- **Enhanced Intelligence**: `ibis/intelligence/enhanced_intel.py`

### 3. Execution Layer
- **Main File**: `ibis_true_agent.py`
- **Order Decision & Placement**: Core execution logic
- **Symbol Rule Normalization**: Price and quantity increment validation
- **Minimum Notional Enforcement**: $11 minimum per trade
- **Duplicate-Order Prevention**: State-based buy-order tracking
- **Execution Engines**: `ibis/execution/engine.py`, `engine_v2.py`

### 4. State & Reconciliation Layer
- **State Storage**: `data/ibis_true_state.json`
- **Database**: `data/ibis_v8.db` (SQLite)
- **Reconciliation Tools**:
  - `tools/reconcile_state_db.py`
  - `tools/deep_state_audit.py`
  - `tools/execution_integrity_check.py`
  - `tools/sync_trade_history_to_db.py`

### 5. Operations & Watchdog Layer
- **Systemd Services & Timers**: `deploy/` directory
- **Health & KPI Runners**:
  - `run_health_check.sh` - Comprehensive health verification
  - `run_execution_integrity_check.sh` - Execution reconciliation
  - `run_hourly_kpi_report.sh` - Hourly performance metrics
  - `run_truth_snapshot.sh` - Market data snapshot
- **Maintenance Tools**:
  - `runtime_status.sh` - Real-time runtime status
  - `agent_watchdog.sh` - Process monitoring
  - `ibis_247_monitor.sh` - 24/7 operations monitoring

## Live Data Paths

- **Journal**: `journalctl -u ibis-agent.service`
- **Runtime Status**: `./runtime_status.sh`
- **Health Check Log**: `health_check.log`
- **Truth Stream**: `data/truth_stream.log`
- **Main Agent Log**: `agent.log`
- **Trade History**: `data/trade_history.json`

## Reliability Model

- **Service Auto-Restarts**: systemd managed
- **Periodic Reconciliations**: Correct drift between state/db/live exchange
- **Duplicate Process Suppression**: Health runner prevention
- **Lock Files**: Prevent overlapping maintenance scripts
- **Execution Safeguards**: Increment-safe rounding, minimum-notional adjustment, duplicate order prevention

## Known Failure Domains

- Exchange DNS/rate limiting
- Symbol rule drift affecting valid tick/lot increments
- Notional constraints near minimum trade threshold
- API rate limiting potential
- Market volatility and liquidity risks

## Trading Strategies

### Primary Strategy - Limitless Swing Strategy
- Targets >2% moves to overcome fee tiers
- EMA-based trend detection (20-period and 50-period)
- RSI momentum filtering (45 < RSI < 70)
- AGI score confirmation (>= 70)
- Cross-exchange validation (Binance lead signal)
- Minimum score threshold: 85 for high-conviction trades

### Advanced Trading Modes
```json
{
  "aggressive_mode": { "min_score": 75, "target_profit": 0.025, "max_positions": 25 },
  "micro_hunter_mode": { "min_score": 60, "target_profit": 0.003, "max_positions": 30 },
  "hyper_mode": { "min_score": 60, "target_profit": 0.0015, "max_positions": 40 }
}
```

## Risk Management System

**Position Sizing:**
- Base risk per trade: 2%
- Max risk per trade: 5%
- Portfolio heat limit: 60%
- Min position size: $11
- Max position size: $40

**Risk Parameters:**
```python
@dataclass
class RiskParams:
    base_risk_per_trade: float = 0.02        # 2% per trade
    max_risk_per_trade: float = 0.05        # 5% max per trade
    portfolio_heat_limit: float = 0.60      # 60% max exposure
    stop_loss_pct: float = 0.05             # 5% stop loss
    take_profit_pct: float = 0.02           # 2% take profit
    min_position_size: float = 11.0         # $11 minimum
    max_position_size: float = 40.0         # $40 maximum
    risk_reward_ratio: float = 0.4          # 1:2.5 risk-reward
```

**Portfolio Risk Assessment:**
- Total risk calculation
- Exposure monitoring
- Risk concentration analysis
- Drawdown risk assessment
- Volatility and liquidity risk scoring