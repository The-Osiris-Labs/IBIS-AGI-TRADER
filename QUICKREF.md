# IBIS Quick Reference

## Running IBIS

```bash
# Start IBIS (recommended)
./start_ibis.sh watchdog

# Check if running
./start_ibis.sh status

# Stop IBIS
./start_ibis.sh stop
```

## Dashboard Reading

```
💰 $82.84     Your total portfolio value
🟢 +$0.50     Today's profit (green = profit, red = loss)
📊 5           Number of opportunities found
🎯 87/100     Best score (higher = better)
🔥 PRIMED      Market is ready for trades
◐ NORMAL      Regular market conditions
```

## Current Status

| Metric | Value |
|--------|-------|
| Total Portfolio | $82.84 |
| Today's P&L | -$2.70 |
| Win Rate | 50.9% |
| Open Positions | 6 |
| Pending Orders | 4 |

## What IBIS Does

1. **Scans** the market every few seconds
2. **Analyzes** each coin for trading opportunities
3. **Scores** opportunities (0-100)
4. **Trades** when score is 70+
5. **Learns** from every trade

## Key Numbers

| Setting | Value | Meaning |
|---------|-------|---------|
| Stop Loss | 5% | Auto-sell if down 5% |
| Take Profit | 1.5% | Auto-sell if up 1.5% |
| Min Profit | $0.50 | Must profit $0.50 after fees |
| Max Positions | 5 | Never hold more than 5 coins |
| Max Positions | 5 | Maximum 5 concurrent trades |
| Max Per Trade | $30 | Never invest more than $30 |

## Strategies

IBIS learns what works best:

| Strategy | Win Rate | Status |
|----------|----------|--------|
| Recycle Profit | 100% | ✅ Best |
| Take Profit | 100% | ✅ Good |
| Stop Loss | 0% | ❌ All losing |

## Risk Protections

✅ Max 5 positions at once
✅ Max 5 concurrent positions
✅ Max $30 per trade
✅ Auto-sell at -5% loss
✅ Auto-sell at +1.5% profit
✅ Ignores tiny positions (<$1)
✅ Doesn't trade in chaos

## Common Messages

| Message | Meaning |
|---------|---------|
| 🔴 EXIT TRIGGER | Position closed |
| 🎯 BUY SIGNAL | New opportunity found |
| ⚠️ WARNING | Something needs attention |
| ✅ SUCCESS | Order executed |

## If Something Goes Wrong

1. **Check if running:**
   ```bash
   ./start_ibis.sh status
   ```

2. **View recent activity:**
   ```bash
   tail -50 data/ibis_true.log
   ```

3. **Restart IBIS:**
   ```bash
   ./start_ibis.sh stop
   ./start_ibis.sh watchdog
   ```

## API Keys

Edit: `ibis/keys.env`

| Service | Status | Get Key From |
|---------|--------|--------------|
| KuCoin | ✅ Set | kucoin.com/account/api |
| Messari | ✅ Set | messari.io/api |
| CoinAPI | ✅ Set | coinapi.io |
| Nansen | ✅ Set | nansen.ai |
| Glassnode | ⚠️ Empty | glassnode.com |

## Files You Might Need

| File | Purpose |
|------|---------|
| `ibis/keys.env` | Your API keys |
| `ibis/core/trading_constants.py` | Risk settings |
| `data/ibis_true_state.json` | Current positions |
| `data/ibis_true_memory.json` | Learning history |
| `data/ibis_true.log` | Activity log |

## Changing Settings

### In ibis/keys.env:
```
PAPER_TRADING=true    # Test mode (no real trades)
PAPER_TRADING=false   # Live trading
```

### In ibis/core/trading_constants.py:
```python
STOP_LOSS_PCT = 0.05        # 5% stop loss
TAKE_PROFIT_PCT = 0.015    # 1.5% take profit
MAX_TOTAL_POSITIONS = 5     # Max 5 concurrent positions
MAX_CAPITAL_PER_TRADE = 30  # $30 max per trade
```

## Learning Terms

- **Win Rate** - Percentage of winning trades
- **P&L** - Profit and Loss (money made/lost)
- **Position** - A coin IBIS is currently holding
- **Order** - A buy or sell instruction
- **Regime** - Market condition (bull, bear, volatile)
- **Score** - IBIS confidence (0-100)

## Getting Help

1. Check the logs: `tail -100 data/ibis_true.log`
2. Check status: `./start_ibis.sh status`
3. Restart IBIS: `./start_ibis.sh stop && ./start_ibis.sh watchdog`

---

**IBIS is running and trading. Happy hunting! 🦅**
