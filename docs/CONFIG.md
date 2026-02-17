# Configuration Reference

This file documents active runtime configuration surfaces for the IBIS AGI Trader.

## 1) Credentials

**File**: `ibis/keys.env`

**Required Fields:**
- `KUCOIN_API_KEY` - KuCoin API key
- `KUCOIN_API_SECRET` - KuCoin API secret
- `KUCOIN_API_PASSPHRASE` - KuCoin API passphrase

**Optional Fields:**
- `PAPER_TRADING` - Enable paper trading mode
- `KUCOIN_IS_SANDBOX` - Use KuCoin sandbox environment
- `DEBUG` - Enable debug logging
- `VERBOSE` - Enable verbose output

**Validation Command:**
```bash
./tools/check_credentials_source.sh
```

## 2) Core Trading Constants

**File**: `ibis/core/trading_constants.py`

**Primary Configuration Groups:**

### TRADING.EXCHANGE
```python
EXCHANGE: str = "kucoin"
MAKER_FEE: float = 0.0010
TAKER_FEE: float = 0.0010
```

### TRADING.CRITICAL
```python
MIN_VIABLE_TARGET: float = 0.005      # 0.5% minimum target profit
MIN_CAPITAL_PER_TRADE: float = 11.0   # $11 minimum trade size
MAX_CAPITAL_PER_TRADE: float = 100.0  # $100 maximum trade size
MAX_POSITIONS: int = 25              # Maximum concurrent positions
```

### TRADING.SCORE
```python
GOD_TIER: int = 95
HIGH_CONFIDENCE: int = 90
STRONG_SETUP: int = 85
GOOD_SETUP: int = 80
STANDARD: int = 75
MIN_THRESHOLD: int = 60
```

### TRADING.POSITION
```python
MIN_CAPITAL_PER_TRADE: float = 11.0
MAX_CAPITAL_PER_TRADE: float = 100.0
MAX_POSITIONS: int = 25
```

### TRADING.SCAN
```python
DEFAULT_SCAN_INTERVAL: int = 5
TIMEFRAME: str = "1min"
LOOKBACK_PERIOD: int = 15
```

### TRADING.RISK
```python
STOP_LOSS_PCT: float = 0.05           # 5% stop loss
TAKE_PROFIT_PCT: float = 0.02         # 2% take profit
BASE_RISK_PER_TRADE: float = 0.02     # 2% risk per trade
MAX_RISK_PER_TRADE: float = 0.05     # 5% max risk per trade
PORTFOLIO_HEAT_LIMIT: float = 0.60   # 60% max exposure
```

### TRADING.EXECUTION
```python
MIN_TRADE_VALUE: float = 11.0
```

### Additional Scoring Knobs
```python
liquidity_volume_spike_ratio_threshold: float = 1.05
liquidity_orderbook_imbalance_threshold: float = 0.03
liquidity_accumulation_confidence_threshold: float = 1.1
```

**Note**: Runtime reads these constants on process start. Restart the service after edits.

## 3) Dynamic Configuration

**File**: `ibis/config.json`

Supports multiple trading modes with dynamic parameters:

```json
{
  "aggressive_mode": { 
    "min_score": 75, 
    "target_profit": 0.025, 
    "max_positions": 25 
  },
  "micro_hunter_mode": { 
    "min_score": 60, 
    "target_profit": 0.003, 
    "max_positions": 30 
  },
  "hyper_mode": { 
    "min_score": 60, 
    "target_profit": 0.0015, 
    "max_positions": 40 
  }
}
```

## 4) Service Configuration

**Systemd Unit**: `/etc/systemd/system/ibis-agent.service`

**Credential Drop-in**: `/etc/systemd/system/ibis-agent.service.d/credentials.conf`

**After Service Config Edits**:
```bash
systemctl daemon-reload
systemctl restart ibis-agent.service
```

## 5) Operational Script Configuration

Managed jobs in `deploy/` directory call:
- `run_health_check.sh` - Comprehensive health verification
- `run_execution_integrity_check.sh` - Execution reconciliation
- `run_hourly_kpi_report.sh` - Hourly performance metrics
- `run_truth_snapshot.sh` - Market data snapshot

## 6) What Not to Configure Blindly

Do not alter strategy/risk fields without explicit intent and validation. Use staged validation:

```bash
python3 -m py_compile ibis_true_agent.py
./run_health_check.sh
./runtime_status.sh
```

## 7) Technical Stack & Dependencies

**Core Framework:**
- Python 3.8+ with asyncio
- Textual (Terminal UI)
- Rich (Terminal formatting)
- Colorama (Cross-platform color support)

**Async & Networking:**
- aiohttp (Async HTTP client)
- websockets (WebSocket communication)

**Data Processing:**
- pandas (Data analysis)
- numpy (Numerical computations)

**Database:**
- SQLAlchemy (ORM)
- SQLite (Local storage)

**Configuration:**
- python-dotenv (Environment variables)
- PyYAML (YAML configuration)

**Security:**
- cryptography (Encryption utilities)

**HTTP & API:**
- requests (HTTP requests)

**Development & Testing:**
- pytest (Testing framework)
- pytest-asyncio (Async testing)
- black (Code formatting)
- flake8 (Linting)
- mypy (Type checking)

**Optional Trading Capabilities:**
- ccxt (Unified exchange integration)
- TA-Lib (Technical analysis)
- vectorbt (Backtesting)
- flask (Web dashboard)
- backtrader (Backtesting framework)
- zipline (Algorithmic trading)