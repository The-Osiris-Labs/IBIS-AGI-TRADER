# Configuration Reference

This document covers all configuration options in IBIS.

---

## Configuration Files

IBIS has three configuration layers:

| File | Purpose | Edit While Running? |
|------|---------|---------------------|
| `ibis/keys.env` | API credentials | No - restart required |
| `ibis/core/trading_constants.py` | Risk settings | No - restart required |
| Environment variables | Runtime options | Yes - apply on restart |

---

## API Keys (`ibis/keys.env`)

This file stores your exchange credentials:

```bash
# KuCoin API credentials
KUCOIN_API_KEY=your_api_key
KUCOIN_API_SECRET=your_api_secret
KUCOIN_API_PASSPHRASE=your_passphrase

# Paper trading mode (true/false)
PAPER_TRADING=false

# Debug modes
DEBUG=false
VERBOSE=false
```

### Required Fields

| Variable | Description | Required? |
|----------|-------------|-----------|
| `KUCOIN_API_KEY` | KuCoin API key | Yes |
| `KUCOIN_API_SECRET` | KuCoin API secret | Yes |
| `KUCOIN_API_PASSPHRASE` | KuCoin API passphrase | Yes |
| `PAPER_TRADING` | Use fake money | No (default: false) |

### Optional Fields

| Variable | Description | Default |
|----------|-------------|---------|
| `DEBUG` | Extra debug logging | false |
| `VERBOSE` | Verbose logging | false |
| `KUCOIN_IS_SANDBOX` | Use sandbox API | false |
| `KUCOIN_DNS` | Custom DNS servers | (none) |
| `KUCOIN_API_HOST` | Custom API host | api.kucoin.com |
| `KUCOIN_API_IP` | Custom API IP | (none) |

---

## Trading Constants (`ibis/core/trading_constants.py`)

This file contains all risk and trading parameters. **Edit with caution.**

### ExchangeConfig

Exchange-specific settings:

```python
@dataclass
class ExchangeConfig:
    EXCHANGE: str = "kucoin"          # Exchange name
    FEE_TIER: str = "Taker"            # Fee tier
    MAKER_FEE: float = 0.0010          # 0.10%
    TAKER_FEE: float = 0.0010          # 0.10%
    ESTIMATED_SLIPPAGE: float = 0.0005 # 0.05%
```

### CriticalThresholds

Critical trading thresholds:

```python
@dataclass
class CriticalThresholds:
    MIN_VIABLE_TARGET: float = 0.0150    # 1.5% minimum to cover fees
    MIN_CAPITAL_PER_TRADE: float = 10.0  # $10 minimum per trade
    MAX_CAPITAL_PER_TRADE: float = 20.0  # $20 maximum per trade
    MAX_POSITIONS: int = 5                # Max concurrent positions
    MIN_SCORE_THRESHOLD: float = 0.70    # 70% confidence threshold
```

### ScoreThresholds

Opportunity grading thresholds:

```python
@dataclass
class ScoreThresholds:
    GOD_TIER: int = 95          # Exceptional (95-100)
    HIGH_CONFIDENCE: int = 90   # High confidence (90-94)
    STRONG_SETUP: int = 85     # Strong buy (85-89)
    GOOD_SETUP: int = 80       # Good buy (80-84)
    STANDARD: int = 70         # Standard (70-79)
    MIN_THRESHOLD: int = 55    # Minimum to consider (55-69)
```

### PositionConfig

Position sizing:

```python
@dataclass
class PositionConfig:
    MAX_TOTAL_POSITIONS: int = 5           # Max concurrent positions
    MIN_CAPITAL_PER_TRADE: float = 5.0     # $5 minimum
    FINAL_TRADE_MIN_CAPITAL: float = 5.0   # $5 minimum for final trade
    MAX_CAPITAL_PER_TRADE: float = 30.0    # $30 maximum
    MAX_POSITION_PCT: float = 50.0         # 50% max of portfolio
    BASE_POSITION_PCT: float = 40.0        # 40% base position size
```

### ScanConfig

Market scanning:

```python
@dataclass
class ScanConfig:
    DEFAULT_SCAN_INTERVAL: int = 10    # Seconds between scans
    DEFAULT_MAX_POSITIONS: int = 20    # Max positions to consider
    TIMEFRAME: str = "5m"              # Candle timeframe
    LOOKBACK_PERIOD: int = 30           # Candles to analyze
```

### RiskConfig

Risk management:

```python
@dataclass
class RiskConfig:
    BASE_RISK_PER_TRADE: float = 0.02   # 2% base risk per trade
    MIN_RISK_PER_TRADE: float = 0.005   # 0.5% minimum risk
    MAX_RISK_PER_TRADE: float = 0.05    # 5% maximum risk
    STOP_LOSS_PCT: float = 0.05         # 5% stop loss
    TAKE_PROFIT_PCT: float = 0.015      # 1.5% take profit
    MIN_PROFIT_BUFFER: float = 0.50     # $0.50 minimum profit
    FEE_BUDGET_DAILY: float = 0.0001    # 0.01% for fees
    PORTFOLIO_HEAT: float = 0.60        # 60% max portfolio exposure
    MAX_PORTFOLIO_RISK: float = 0.6     # 60% max risk
```

### IntelligenceConfig

AI/ML thresholds:

```python
@dataclass
class IntelligenceConfig:
    AGI_CONFIDENCE_THRESHOLD: float = 0.70    # 70% confidence
    MIN_VIABLE_TARGET: float = 0.008          # 0.8% minimum target
    CROSS_EXCHANGE_LEAD_THRESHOLD: float = 0.002 # 0.2%
    INTELLIGENCE_GAP_THRESHOLD: int = 10      # Gap threshold
    SAME_SCORE_PROTECTION_THRESHOLD: int = 5   # Score protection
```

### PrecisionExecutionConfig

Entry/exit precision:

```python
@dataclass
class PrecisionExecutionConfig:
    MAX_WAIT_SECONDS: float = 5.0              # Max wait for entry
    MIN_PRICE_IMPROVEMENT_PCT: float = 0.02    # 0.02% min improvement
    SPREAD_THRESHOLD_TIGHT: float = 0.05       # <0.05% = tight
    SPREAD_THRESHOLD_MODERATE: float = 0.15    # <0.15% = moderate

    # ATR-based stops
    TARGET_AVG_SL_PCT: float = 0.02            # 2% average stop
    ATR_MULTIPLIER_TIGHT: float = 1.0          # Low volatility
    ATR_MULTIPLIER_NORMAL: float = 1.5          # Normal volatility
    ATR_MULTIPLIER_WIDE: float = 2.0            # High volatility
    MIN_SL_PCT: float = 0.005                   # 0.5% minimum
    MAX_SL_PCT: float = 0.04                    # 4% maximum

    # Trailing stops
    TRAILING_ACTIVATION_PCT: float = 1.0        # Activate at +1%
    TRAILING_50_PCT_LEVEL: float = 2.0          # 50% at +2%
    TRAILING_70_PCT_LEVEL: float = 3.0          # 70% at +3%
```

### ExecutionConfig

Execution limits:

```python
@dataclass
class ExecutionConfig:
    TOP_CANDIDATES_LIMIT: int = 25         # Top candidates to analyze
    PRIORITY_SYMBOLS_LIMIT: int = 30         # Priority symbols limit
    PARALLEL_ANALYSIS_SIZE: int = 5         # Parallel analysis
    MIN_TRADE_VALUE: float = 0.10           # $0.10 minimum
    DECAY_TIMEOUT_SECONDS: int = 7200       # 2 hours
    MARKET_PRIMED_MULTIPLIER: float = 1.5   # 1.5x when primed
```

### MultiplierConfig

Position sizing multipliers:

```python
@dataclass
class MultiplierConfig:
    GOD_TIER_MULTIPLIER: float = 4.0        # Score >= 95
    HIGH_CONFIDENCE_MULTIPLIER: float = 3.0 # Score >= 90
    STRONG_SETUP_MULTIPLIER: float = 2.0   # Score >= 85
    GOOD_SETUP_MULTIPLIER: float = 1.5      # Score >= 80
    STANDARD_MULTIPLIER: float = 1.0        # Score < 80

    REGIME_TRENDING_MULTIPLIER: float = 1.25  # Bull market
    REGIME_FLAT_MULTIPLIER: float = 0.75      # Flat market
    REGIME_DEFAULT_MULTIPLIER: float = 1.0     # Normal

    MARKET_PRIMED_MULTIPLIER: float = 1.5   # When market primed
    BASE_SIZE_PCT: float = 0.25            # Base size percentage
```

### FilterConfig

Symbol filtering:

```python
@dataclass
class FilterConfig:
    MIN_LIQUIDITY: int = 1000              # Min 24h volume
    MAX_SPREAD: float = 0.02               # 2% max spread
    STABLECOINS: set = {"USDT", "USDC", "DAI", "BUSD"}
    IGNORED_SYMBOLS: set = set()           # Symbols to skip
```

### TechnicalIndicatorConfig

Technical indicator settings:

```python
@dataclass
class TechnicalIndicatorConfig:
    # Period settings
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

    # Weights (must sum to 1.0)
    WEIGHT_RSI: float = 0.10
    WEIGHT_MACD: float = 0.15
    WEIGHT_BOLLINGER: float = 0.10
    WEIGHT_MA: float = 0.15
    WEIGHT_OBV: float = 0.10
    WEIGHT_STOCH: float = 0.10
    WEIGHT_VWAP: float = 0.10
    WEIGHT_ATR: float = 0.05
    WEIGHT_VOLUME: float = 0.15
```

---

## Environment Variables

These can be set at runtime:

| Variable | Values | Effect |
|----------|---------|--------|
| `PAPER_TRADING` | true/false | Use fake money |
| `DEBUG` | true/false | Extra debug logging |
| `VERBOSE` | true/false | Verbose logging |

---

## Accessing Config in Code

```python
from ibis.core.trading_constants import TRADING

# Risk settings
TRADING.RISK.STOP_LOSS_PCT        # 0.05
TRADING.RISK.TAKE_PROFIT_PCT      # 0.015
TRADING.RISK.BASE_RISK_PER_TRADE  # 0.02

# Position settings
TRADING.POSITION.MIN_CAPITAL_PER_TRADE   # 5.0
TRADING.POSITION.MAX_CAPITAL_PER_TRADE   # 30.0
TRADING.POSITION.MAX_TOTAL_POSITIONS     # 5

# Score thresholds
TRADING.SCORE.GOD_TIER          # 95
TRADING.SCORE.STANDARD           # 70
TRADING.SCORE.MIN_THRESHOLD      # 55

# Technical weights
TRADING.TECHNICAL.WEIGHT_RSI    # 0.10
TRADING.TECHNICAL.WEIGHT_MACD   # 0.15
TRADING.TECHNICAL.WEIGHT_MA     # 0.15
```

---

## Recommended Changes

### For More Conservative Trading

```python
@dataclass
class RiskConfig:
    BASE_RISK_PER_TRADE: float = 0.01   # 1% instead of 2%
    STOP_LOSS_PCT: float = 0.03         # 3% instead of 5%

@dataclass
class PositionConfig:
    MAX_TOTAL_POSITIONS: int = 3        # 3 instead of 5
    BASE_POSITION_PCT: float = 0.20      # 20% instead of 40%
```

### For More Aggressive Trading

```python
@dataclass
class RiskConfig:
    BASE_RISK_PER_TRADE: float = 0.03   # 3%
    STOP_LOSS_PCT: float = 0.08         # 8%

@dataclass
class PositionConfig:
    MAX_TOTAL_POSITIONS: int = 10
    BASE_POSITION_PCT: float = 0.50      # 50%
```

### For Higher Take Profits

```python
@dataclass
class RiskConfig:
    TAKE_PROFIT_PCT: float = 0.03       # 3% instead of 1.5%
```

---

## Common Mistakes

1. **Changing STOP_LOSS_PCT without understanding** - This protects your capital
2. **Setting MIN_CAPITAL_PER_TRADE too low** - Small trades don't cover fees
3. **Setting MAX_TOTAL_POSITIONS too high** - Too much diversification
4. **Changing TechnicalIndicatorConfig weights** - Can break scoring
5. **Editing while running** - Always restart after changes

---

## Verification

After making changes:

```bash
# Check config loads correctly
python3 -c "from ibis.core.trading_constants import TRADING; print('Config OK')"

# Restart IBIS
./start_ibis.sh restart

# Check logs
tail -f data/ibis_true.log
```

---

## Full Config Reference

For the complete picture, see `ibis/core/trading_constants.py` which contains the source of truth for all configuration.
