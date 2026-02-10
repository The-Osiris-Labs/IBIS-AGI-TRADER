# IBIS Developer Guide

This guide is for developers who want to understand, modify, or extend IBIS.

## Architecture

```
ibis_true_agent.py
    │
    ├── Main Loop
    │   ├── scan_market() - Find opportunities
    │   ├── analyze_opportunities() - Score each one
    │   ├── execute_trades() - Buy/Sell
    │   └── check_positions() - Monitor exits
    │
    ├── State Management
    │   ├── _save_state() - Persist to JSON
    │   └── _save_memory() - Record learning
    │
    └── Learning
        └── learn_from_trade() - Update performance

ibis/exchange/
    └── kucoin_client.py - KuCoin API wrapper
    └── ccxt_client.py - Multi-exchange support

ibis/intelligence/
    └── market_intelligence.py - Data aggregation
    └── free_intelligence.py - Free data sources

data/
    └── ibis_true_state.json - Current state
    └── ibis_true_memory.json - Learning history
```

## Key Functions

### Main Agent Loop

```python
async def main_loop()
    while True:
        await scan_market()
        await analyze_opportunities()
        await execute_trades()
        await check_positions()
        await save_state()
        await asyncio.sleep(scan_interval)
```

### Opportunity Scoring

```python
async def analyze_opportunities(symbols):
    for symbol in symbols:
        score = await calculate_score(symbol)
        if score >= 70:
            opportunities.append({
                'symbol': symbol,
                'score': score,
                'tp': current * 1.015,  # +1.5%
                'sl': current * 0.95,    # -5%
            })
```

### Position Management

```python
async def check_positions():
    for symbol, pos in state.positions:
        current = get_price(symbol)
        pnl = (current - pos.entry) / pos.entry
        
        if pnl >= 0.015 and actual_profit >= 0.50:
            close_position(symbol, 'TAKE_PROFIT')
        elif pnl <= -0.05:
            close_position(symbol, 'STOP_LOSS')
```

## Adding New Strategies

1. Define strategy in `trading_constants.py`:
```python
MY_STRATEGY = StrategyConfig(
    name="my_strategy",
    min_score=70,
    max_positions=3,
)
```

2. Add scoring logic in `analyze_opportunities()`:
```python
if conditions_met:
    score = base_score + my_bonus
```

3. Record in learning:
```python
key = f"{regime}_my_strategy"
memory.performance[key].trades += 1
```

## Configuration Pattern

All configuration in `trading_constants.py`:

```python
@dataclass
class MyConfig:
    my_setting: float = 0.05
    another_setting: int = 10
```

Access in code:
```python
TRADING.MY.my_setting
```

## State Management

### Reading State
```python
state = load_state()
positions = state['positions']
daily = state['daily']
```

### Modifying State
```python
state['positions'][symbol] = new_position
state['daily']['trades'] += 1
save_state(state)
```

### Memory/Learning
```python
memory = load_memory()
perf = memory['performance_by_symbol']
key = f"{regime}_{strategy}"
perf[key]['trades'] += 1
save_memory(memory)
```

## Common Modifications

### Change Scan Interval
```python
# ibis/core/trading_constants.py
DEFAULT_SCAN_INTERVAL: int = 10  # seconds
```

### Adjust Position Size
```python
MAX_CAPITAL_PER_TRADE: float = 30.0  # $30 max
```

### Position Limits
```python
# Position limits are set to 5 concurrent maximum
# Controlled by IBIS intelligence, not hard caps
```

### Add New Data Source
1. Add API call in `market_intelligence.py`
2. Use in scoring function
3. Add to `calculate_intelligence_score()`

## Testing

```bash
# Run agent in paper mode
PAPER_TRADING=true python ibis_true_agent.py

# Check logs
tail -f data/ibis_true.log

# Monitor state
python3 -c "from ibis.data_consolidation import load_state; print(load_state())"
```

## Debugging

### Enable Debug Mode
```bash
DEBUG=true python ibis_true_agent.py
```

### Check Specific Symbol
```python
# In code
print(f"Symbol {symbol}: score={score}, price={price}")
```

### View All Positions
```bash
python3 -c "
from ibis.data_consolidation import load_state
state = load_state()
for sym, pos in state['positions'].items():
    print(f\"{sym}: {pos}\")
"
```

## Performance Optimization

1. **Reduce scan frequency** - Lower `DEFAULT_SCAN_INTERVAL`
2. **Limit symbols** - Reduce `symbols_cache` size
3. **Cache data** - Intelligence data is cached for 60s

## Common Errors

### "Balance insufficient"
- Check USDT balance
- Reduce position size
- Close some positions

### "No API key"
- Add key to `ibis/keys.env`
- Restart IBIS

### "Position not found"
- Position already closed
- Check if duplicate close attempt

## File Locations

```
/root/projects/Dont enter unless solicited/AGI Trader/
├── ibis_true_agent.py          # Main logic
├── ibis/core/trading_constants.py  # Config
├── ibis/keys.env              # API keys
├── ibis/exchange/kucoin_client.py  # Exchange
└── data/
    ├── ibis_true_state.json   # State
    ├── ibis_true_memory.json  # Learning
    └── ibis_true.log         # Logs
```

## Code Style

- Use async/await for I/O operations
- Use dataclasses for configuration
- Log important events with emojis
- Test changes in paper mode first
