# 🦅 IBIS - Intelligent Trading System

**An autonomous cryptocurrency trading agent that hunts opportunities, adapts to markets, and learns from every trade.**

---

## What Is IBIS?

IBIS isn't your typical trading bot. It doesn't blindly follow indicators or execute simple signals. Think of it as a digital trader that:

- **Discovers opportunities on its own** - scans the market, finds the best setups
- **Adapts to conditions** - knows when to be aggressive, when to be cautious
- **Learns from experience** - gets smarter with every trade
- **Protects your capital** - never risks more than it should

The name IBIS comes from Egyptian mythology - a sacred bird associated with wisdom and knowledge. This agent is built to be wise about trading.

---

## The Philosophy

```
"NO HOPE. ONLY HUNT."
```

Trading often fails because people *hope* a trade will work out. IBIS doesn't hope. It *hunts*.

This means:
- Only take trades with strong evidence
- Cut losses fast, don't argue with the market
- Let winners run, take profits systematically
- Always adapt, never assume the market will cooperate

---

## Quick Start

### Running IBIS

```bash
# Run with watchdog (auto-restart on crashes)
./start_ibis.sh watchdog

# Install as system service (24/7)
./start_ibis.sh systemd

# Check status
./start_ibis.sh status

# Stop everything
./start_ibis.sh stop
```

### Your First Run

**Always start with paper trading!**

```bash
# Edit keys.env
nano ibis/keys.env
# Set PAPER_TRADING=true for testing
```

---

## Project Structure

```
IBIS/
├── ibis_true_agent.py           # Main agent - the brain
├── start_ibis.sh               # Startup script (use this!)
│
├── ibis/
│   ├── keys.env                # YOUR API KEYS - EDIT THIS!
│   │
│   ├── core/
│   │   ├── trading_constants.py  # All settings (SL, TP, limits)
│   │   └── config.py           # Configuration helpers
│   │
│   ├── exchange/
│   │   ├── kucoin_client.py    # KuCoin integration
│   │   ├── ccxt_client.py      # Multi-exchange support
│   │   └── trade_executor.py   # Order handling
│   │
│   ├── intelligence/
│   │   ├── market_intelligence.py  # Data aggregation
│   │   ├── free_intelligence.py     # Free data sources
│   │   └── enhanced_intel.py    # Enhanced analysis
│   │
│   ├── cross_exchange_monitor.py  # Binance comparison
│   ├── data_consolidation.py   # State sync
│   └── position_rotation.py     # Position management
│
└── data/
    ├── ibis_true_state.json    # Current positions, capital
    ├── ibis_true_memory.json   # Learning history
    └── ibis_true.log          # Activity log
```

---

## Configuration

### API Keys

**Important:** Edit `ibis/keys.env` before running!

```bash
# KuCoin (required for live trading)
KUCOIN_API_KEY=your_key_here
KUCOIN_API_SECRET=your_secret_here
KUCOIN_API_PASSPHRASE=your_passphrase

# Premium APIs (optional but recommended)
MESSARI_API_KEY=        # Institutional-grade data
COINAPI_API_KEY=        # Real-time data
NANSEN_API_KEY=         # Smart money tracking
GLASSNODE_API_KEY=      # On-chain metrics
```

### Risk Settings

Located in `ibis/core/trading_constants.py`:

```python
# Risk Management
STOP_LOSS_PCT: 0.05       # 5% - cut losses here
TAKE_PROFIT_PCT: 0.015     # 1.5% - take profits here
MIN_PROFIT_BUFFER: 0.50     # $0.50 minimum to cover fees

# Position Limits
MAX_TOTAL_POSITIONS: 5      # Max 5 concurrent positions
MAX_CAPITAL_PER_TRADE: 30.0 # Max $30 per position
MIN_CAPITAL_PER_TRADE: 5.0   # Min $5 per position
```

**Note:** Position limit is set to 5 concurrent positions maximum. The agent's intelligence determines how many positions to open based on available capital and opportunity quality.

**Don't change TP/SL schema** - the system is tuned for these values.

---

## How IBIS Works

### The Loop (Every Few Minutes)

```
1. SCAN
   └─ Check market regime (bull, bear, volatile, etc.)
   └─ Scan all KuCoin pairs
   └─ Filter out noise (stablecoins, illiquid markets)

2. ANALYZE
   └─ Technical analysis (momentum, volatility)
   └─ Multi-timeframe alignment
   └─ Cross-exchange signals
   └─ Calculate opportunity score (0-100)

3. DECIDE
   └─ Score >= 70? → Buy
   └─ Position size based on confidence
   └─ Set automatic stop loss (5%)
   └─ Set take profit (1.5%)

4. EXECUTE
   └─ Place order on KuCoin
   └─ Track position in real-time
   └─ Monitor for exit conditions

5. LEARN
   └─ Record trade outcome
   └─ Update strategy performance
   └─ Adapt to regime
```

---

## Market Regimes

IBIS detects and adapts to different market conditions:

| Regime | Behavior |
|--------|----------|
| **STRONG_BULL** | Aggressive, longer scans |
| **BULL** | Normal buying |
| **BEAR** | Defensive, smaller positions |
| **STRONG_BEAR** | Very cautious |
| **VOLATILE** | Quick entries/exits |
| **NORMAL** | Standard approach |
| **FLAT** | Minimal trading |
| **UNKNOWN** | Wait for clarity |

---

## Scoring System

Each opportunity gets scored (0-100):

| Factor | Weight | What It Checks |
|--------|--------|----------------|
| **Technical** | 40% | Price action, momentum, trends |
| **Intelligence** | 30% | AI analysis of conditions |
| **Multi-Timeframe** | 15% | Alignment across timeframes |
| **Volume** | 10% | Trading activity |
| **Sentiment** | 5% | News, social mood |

**70+** → Buy signal
**55-69** → Monitor
**<55** → Ignore

---

## Learning System

IBIS tracks performance by strategy + regime:

```
VOLATILE_recycle_profit  │ N trades │ High WR │ +$X.XX  ← EXAMPLE
VOLATILE_take_profit     │  3 trades │ 100% WR │ +$0.41
VOLATILE_stop_loss       │ 15 trades │   0% WR │ -$2.02  ← WORST
```

Over time, it gravitates toward what works and away from what doesn't.

---

## Risk Protections

IBIS has multiple safety nets:

1. **Position Limits** - Maximum 5 concurrent positions (IBIS intelligence decides when to open/close)
2. **Size Limits** - Max $30 per trade
3. **Stop Loss** - Auto-exit at -5%
4. **Take Profit** - Auto-exit at +1.5%
5. **Fee Buffer** - Won't close at TP unless actual profit >= $0.50
6. **Dust Filter** - Ignores positions < $1 (too small to matter)
7. **Regime Awareness** - Doesn't trade aggressively in chaos

---

## Understanding the Output

### Dashboard Symbols

```
💰 $82.84    Total portfolio value
🟢 +$0.50    Today's profit
📊 5          Opportunities found
🎯 87/100    Best opportunity score
🔥 PRIMED     Market ready for action
◐ NORMAL     Regular conditions
```

### Log Messages

| Symbol | Meaning |
|--------|---------|
| ✅ | Order success |
| ❌ | Order failed |
| 🔴 | Position closed |
| 🧠 | Learning observation |
| ⚠️ | Warning |

---

## File Descriptions

### ibis_true_agent.py
The main brain. Contains the loop that runs forever. Handles scanning, scoring, trading, and learning.

### ibis/keys.env
**YOUR API KEYS.** Edit this file before running. Contains all credentials.

### ibis/core/trading_constants.py
All configuration. Risk settings, thresholds, limits. Don't change TP/SL values.

### ibis/exchange/kucoin_client.py
Talks to KuCoin API. Handles orders, balances, prices.

### ibis/market_intelligence.py
Aggregates data from multiple sources. Calculates intelligence scores.

### ibis/data_consolidation.py
Syncs data between JSON state and SQLite database.

### data/ibis_true_state.json
Current state. Positions, capital, daily stats. Auto-saved.

### data/ibis_true_memory.json
Learning history. Performance by strategy. Persists across restarts.

### data/ibis_true.log
Activity log. Everything IBIS does is recorded here.

---

## Troubleshooting

### "No opportunities found"
- Market might be in a bad regime
- Thresholds might be too high
- Check liquidity filters

### "Orders not executing"
- Verify API keys in keys.env
- Check KuCoin status
- Ensure sufficient USDT balance

### "State not saving"
- Check data/ directory exists
- Verify file permissions
- Check disk space: `df -h`

### IBIS keeps crashing
- Run with watchdog: `./start_ibis.sh watchdog`
- Check logs: `tail -50 data/ibis_true.log`

---

## Data Sources

IBIS uses multiple data sources:

| Source | Type | What's Used For |
|--------|------|----------------|
| **KuCoin** | Exchange | Trading, balances |
| **CoinGecko** | Free | Market data |
| **Messari** | Premium (key needed) | Institutional metrics |
| **CoinAPI** | Premium (key needed) | Real-time data |
| **Nansen** | Premium (key needed) | Smart money tracking |
| **Glassnode** | Premium (key needed) | On-chain data |

---

## Current Performance

```
Today: 58 trades | 31W 27L | 53.4% WR | -$2.86
Total: $82.67 portfolio
Active Positions: 5 (DATA/KCS dust removed)
```

---

## API Keys Location

When you get new API keys, add them here:

```
File: ibis/keys.env
Section: PREMIUM MARKET DATA API KEYS

MESSARI_API_KEY=      # Get from: https://messari.io/api
COINAPI_API_KEY=       # Get from: https://www.coinapi.io
NANSEN_API_KEY=        # Get from: https://app.nansen.ai
GLASSNODE_API_KEY=     # Get from: https://docs.glassnode.com/
```

Restart IBIS after adding keys:
```bash
./start_ibis.sh stop
./start_ibis.sh watchdog
```

---

## Commands Reference

```bash
./start_ibis.sh watchdog   # Run with auto-restart
./start_ibis.sh systemd    # Install as service
./start_ibis.sh status     # Check if running
./start_ibis.sh stop       # Stop everything
```

---

## Philosophy

Built on these principles:

- **Autonomy** over simple automation
- **Intelligence** over rigid rules
- **Adaptation** over static strategies
- **Learning** over fixed systems

---

## Disclaimer

**Trading cryptocurrency carries significant risk. Past performance does not guarantee future results.**

This software is provided "as is" for educational purposes. Never trade with money you cannot afford to lose.

---

## The Name

In ancient Egyptian mythology, the ibis was sacred to Thoth - god of wisdom, writing, and knowledge. Egyptians believed the ibis embodied wisdom and served as a messenger between worlds.

Just like the ibis, this agent is designed to be wise about trading - observing patterns, adapting to conditions, and making informed decisions.

---

**Happy hunting. 🦅**
