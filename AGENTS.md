# IBIS Development Guide for AI Assistants

This document helps AI assistants understand and work with the IBIS trading system.

## Project Overview

IBIS is an autonomous cryptocurrency trading agent that:
- Scans KuCoin for trading opportunities
- Scores opportunities using technical + intelligence analysis
- Executes trades with automatic risk management
- Learns from every trade
- Operates 24/7

## Key Files

| File | Purpose | Priority |
|------|---------|----------|
| `ibis_true_agent.py` | Main agent loop | Critical |
| `ibis/core/trading_constants.py` | All configuration | High |
| `ibis/keys.env` | API keys | Critical |
| `data/ibis_true_state.json` | Runtime state | High |
| `data/ibis_true_memory.json` | Learning history | Medium |

## Important Constraints

### DO NOT CHANGE
- TP/SL schema (5% SL, 1.5% TP)
- Risk configuration schema
- Position tracking structure

### DO NOT
- Delete or corrupt state files
- Change API key format
- Modify running agent's state unexpectedly

## Common Tasks

### Check Agent Status
```bash
./start_ibis.sh status
pgrep -f ibis_true_agent.py
tail -50 data/ibis_true.log
```

### View Current State
```bash
python3 -c "
from ibis.data_consolidation import load_state
import json
print(json.dumps(load_state(), indent=2))
"
```

### View Learning Memory
```bash
python3 -c "
from ibis.data_consolidation import load_memory
import json
print(json.dumps(load_memory(), indent=2))
"
```

### Clean Dust Positions
```python
# Dust cleanup is now automatic in reconcile_holdings()
# Manual cleanup only needed if agent isn't running:
from ibis.data_consolidation import load_state, save_state
state = load_state()
for sym in list(state['positions'].keys()):
    pos = state['positions'][sym]
    value = pos['quantity'] * pos.get('current_price', 0)
    if value < 1.0:
        del state['positions'][sym]
save_state(state)
```

### Fix State Consistency
```python
from ibis.data_consolidation import load_state, save_state
state = load_state()

# Remove duplicate positions from buy_orders
buy_orders = state.get('capital_awareness', {}).get('buy_orders', {})
for sym in list(buy_orders.keys()):
    if sym in state['positions']:
        del buy_orders[sym]

# Fix real_trading_capital
usdt = state.get('capital_awareness', {}).get('usdt_available', 0)
locked = state.get('capital_awareness', {}).get('usdt_locked_buy', 0)
state['capital_awareness']['real_trading_capital'] = usdt - locked
save_state(state)
```

## Configuration Pattern

All configuration lives in `trading_constants.py`:

```python
@dataclass
class RiskConfig:
    STOP_LOSS_PCT: float = 0.05
    TAKE_PROFIT_PCT: float = 0.015
    MIN_PROFIT_BUFFER: float = 0.50
```

Access in code:
```python
from ibis.core.trading_constants import TRADING
TRADING.RISK.STOP_LOSS_PCT  # 0.05
TRADING.RISK.TAKE_PROFIT_PCT  # 0.015
```

## State Structure

### ibis_true_state.json
```json
{
  "positions": {
    "SYMBOL": {
      "symbol": "SYMBOL",
      "quantity": 100,
      "buy_price": 0.01,
      "current_price": 0.0105,
      "mode": "HYPER_INTELLIGENT",
      "regime": "VOLATILE",
      "tp": 0.01015,
      "sl": 0.0095,
      "unrealized_pnl": 0.05,
      "unrealized_pnl_pct": 5.0
    }
  },
  "daily": {
    "trades": 50,
    "wins": 25,
    "losses": 25,
    "pnl": -2.50
  },
  "capital_awareness": {
    "usdt_available": 20.00,
    "total_assets": 85.00
  }
}
```

### ibis_true_memory.json
```json
{
  "performance_by_symbol": {
    "VOLATILE_recycle_profit": {
      "trades": 16,
      "wins": 16,
      "losses": 0,
      "pnl": 0.55
    }
  },
  "learned_regimes": {
    "best": "VOLATILE",
    "avoid": "UNKNOWN"
  }
}
```

## Common Issues & Fixes

### Dust Positions (value < $1)
Symptom: DATA/KCS showing as $0.00
Fix: No longer needed - dust cleanup is now automatic in `reconcile_holdings()`

### Dust Positions Keep Reappearing
Symptom: DATA/KCS dust keeps appearing in state
Fix: Added dust cleanup in `reconcile_holdings()` at `ibis_true_agent.py:906-922` that checks existing positions below $1 threshold and removes them automatically

### Duplicate buy_orders
Symptom: Symbol in both positions AND buy_orders
Fix: Remove from buy_orders

### real_trading_capital = 0
Symptom: Capital calculation wrong
Fix: usdt_available - usdt_locked_buy

### Trades not syncing to DB
Symptom: SQLite DB empty
Fix: Agent writes to DB on close_position()

## Trade Reasons

- `TAKE_PROFIT` - Hit profit target (+1.5%)
- `STOP_LOSS` - Hit stop loss (-5%)
- `RECYCLE_PROFIT` - Taking profit to fund better trade
- `ALPHA_DECAY` - Signal weakening

## Market Regimes

- `VOLATILE` - High uncertainty, quick moves
- `STRONG_BULL` - Strong uptrend
- `BULL` - Mild uptrend
- `BEAR` - Downtrend
- `STRONG_BEAR` - Strong downtrend
- `NORMAL` - Average conditions
- `FLAT` - Sideways
- `UNKNOWN` - Unclear

## Data Sources

| Source | Status | Purpose |
|--------|--------|----------|
| KuCoin | ✅ | Trading, prices |
| CoinGecko | ✅ | Free market data |
| Messari | ✅ | Premium data |
| CoinAPI | ✅ | Real-time data |
| Nansen | ✅ | Smart money |
| Glassnode | ⚠️ | Not configured |

## Code Patterns

### Async Function
```python
async def my_function():
    try:
        result = await some_async_call()
        return result
    except Exception as e:
        print(f"Error: {e}")
        return None
```

### State Modification
```python
self.state['positions'][symbol] = new_position
self._save_state()
```

### Logging
```python
self.log_event(f"   ✅ Action completed: {detail}")
print(f"🎯 Score: {score}")
```

## Testing Changes

1. Always test in paper mode first
2. Check state consistency after changes
3. Verify learning system still works
4. Check logs for errors

## Important Commands

```bash
# Run agent
./start_ibis.sh watchdog

# Check logs
tail -100 data/ibis_true.log

# View state
python3 -c "from ibis.data_consolidation import load_state; print(load_state())"

# Restart
./start_ibis.sh stop && ./start_ibis.sh watchdog
```

## Things to Remember

1. Don't change TP/SL schema
2. Always save state after modifications
3. Dust positions (<$1) are now auto-cleaned in reconcile_holdings()
4. API keys in keys.env, not hardcoded
5. Agent must sync to both JSON and DB
6. Learning persists across restarts
7. Position limits are unlimited (9999 max)

## When in Doubt

1. Check the logs: `tail -100 data/ibis_true.log`
2. Verify state: `python3 -c "from ibis.data_consolidation import load_state; ..."`
3. Check agent process: `pgrep -f ibis_true_agent.py`
4. Review configuration: `ibis/core/trading_constants.py`
