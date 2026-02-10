```
╭─────────────────────────────────────────────────────────────────────────────────────────╮
│                                                                                         │
│                                    ██╗██████╗ ██╗███████╗                              │
│                                    ██║██╔══██╗██║██╔════╝                              │
│                                    ██║██████╔╝██║███████╗                              │
│                                    ██║██╔══██╗██║╚════██║                              │
│                                    ██║██████╔╝██║███████║                              │
│                                    ╚═╝╚═════╝ ╚═╝╚══════╝                              │
│                                                                                         │
│                            🦅  Sacred Hunter of Markets  🦅                            │
│                    Messenger of Thoth • Keeper of Balance • Oracle of Hunts            │
│                                                                                         │
│                          "NO HOPE. ONLY HUNT."  •  "OBSERVE. ADAPT. STRIKE."           │
│                                                                                         │
╰─────────────────────────────────────────────────────────────────────────────────────────╯
```

# 🦅 IBIS - Intelligent Trading System

**An autonomous cryptocurrency trading agent that hunts opportunities, adapts to markets, and learns from every trade.**

> **Developed by [The Osiris Labs](https://www.theosirislabs.com)** - Building intelligent systems for tomorrow

<div align="center">

[![GitHub Stars](https://img.shields.io/github/stars/The-Osiris-Labs/IBIS-AGI-TRADER?style=social)](https://github.com/The-Osiris-Labs/IBIS-AGI-TRADER)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](./LICENSE)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/)
[![Status](https://img.shields.io/badge/status-Production--Ready-brightgreen.svg)]()

**[Repository](https://github.com/The-Osiris-Labs/IBIS-AGI-TRADER)** • 
**[Documentation](./README.md)** • 
**[Issues](https://github.com/The-Osiris-Labs/IBIS-AGI-TRADER/issues)** • 
**[Website](https://www.theosirislabs.com)**

</div>

---

## ✨ Core Features

| Feature | Description |
|---------|-------------|
| **🔍 Real-Time Market Scanning** | Analyzes 1000+ crypto pairs continuously to find optimal entry points |
| **🧠 Intelligent Scoring** | 40% technical + 30% AI analysis + 15% multi-timeframe + 10% volume + 5% sentiment |
| **📈 Adaptive Trading** | Adjusts strategy based on market regime (bull, bear, volatile, flat) |
| **🎓 Continuous Learning** | Tracks performance by strategy+regime to optimize over time |
| **🔐 Risk Management** | Automatic stop-loss (5%), take-profit (1.5%), position limits (5 max) |
| **⚡ High Frequency** | Executes trades every few minutes, 24/7 without human intervention |
| **📊 Multi-Source Intelligence** | Integrates KuCoin, CoinGecko, Messari, CoinAPI, Nansen, Glassnode |
| **💾 Persistent Memory** | Remembers every trade and learning, survives restarts |

---

## 🎯 Why IBIS?

### The Problem
Traditional trading bots are rigid. They follow static rules, don't adapt, and fail when markets shift. Traders lose money hoping their positions will work out.

### The Solution
**IBIS** is different. It's not a bot. It's an agent.

- **Intelligent** - Uses AI to understand market context, not just indicators
- **Adaptive** - Changes strategy when conditions change
- **Learning** - Gets smarter with every trade, remembers what works
- **Autonomous** - Makes decisions 24/7 without human input
- **Protective** - Never risks more than it should, cuts losses fast

### The Philosophy

```
"NO HOPE. ONLY HUNT."
```

IBIS doesn't hope a trade will work. It *hunts* - looking for high-probability setups with strong evidence. When it finds one, it strikes. When the trade turns against it, it exits immediately.

---

## 🚀 Getting Started

### Step 1: Prerequisites
```bash
# Python 3.8+
python --version

# Required Python packages
pip install -r requirements.txt

# KuCoin account (free)
# https://www.kucoin.com (for live trading)
```

### Step 2: Configure API Keys

Edit `ibis/keys.env` with your KuCoin credentials:

```bash
nano ibis/keys.env
```

```env
# REQUIRED - KuCoin (https://www.kucoin.com/account/api)
KUCOIN_API_KEY=your_kucoin_api_key_here
KUCOIN_API_SECRET=your_kucoin_api_secret_here
KUCOIN_API_PASSPHRASE=your_kucoin_passphrase_here

# RECOMMENDED - Premium Data (optional, for better signals)
MESSARI_API_KEY=your_messari_key          # https://messari.io/api
COINAPI_API_KEY=your_coinapi_key          # https://www.coinapi.io
NANSEN_API_KEY=your_nansen_key            # https://app.nansen.ai

# SAFETY FIRST - Start with paper trading
PAPER_TRADING=true  # Set to false only when confident
```

### Step 3: Run IBIS

```bash
# First time - test with paper trading
./start_ibis.sh watchdog

# Check it's running
./start_ibis.sh status

# Watch the logs in real-time
tail -f data/ibis_true.log

# When ready for live trading (after testing!)
# Edit keys.env and set PAPER_TRADING=false
# Then restart:
# ./start_ibis.sh stop && ./start_ibis.sh watchdog
```

### Running Options

```bash
./start_ibis.sh watchdog   # Recommended: auto-restart on crash
./start_ibis.sh systemd    # Advanced: install as system service
./start_ibis.sh status     # Check if running
./start_ibis.sh stop       # Stop everything
```

⚠️ **IMPORTANT:** Always test with paper trading first!

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

### Live Dashboard Example

```
╔═════════════════════════════════════════════════════════════════════╗
║                    🦅 IBIS TRADING DASHBOARD                        ║
╚═════════════════════════════════════════════════════════════════════╝

Portfolio Status:
  💰 Total Value:        $82.84 (+$2.15 | +2.7%)
  📊 Available USDT:      $20.00
  🔴 Active Positions:    5
  
Market Conditions:
  📈 Regime:            VOLATILE (High opportunity zone)
  🎯 Best Opportunity:  87/100 (STRONG BUY)
  📍 Pairs Scanned:     1,247
  ✅ Good Setups:       18

Today's Performance:
  ✅ Wins:              12 trades
  ❌ Losses:            7 trades
  📊 Win Rate:          63.2%
  💵 P&L:               +$2.86 (3.6%)

Active Positions:
  BTC/USDT    │ +1.2%  │ Entry: $42,150 │ SL: $40,043 │ TP: $42,813
  ETH/USDT    │ -0.8%  │ Entry: $2,285  │ SL: $2,171  │ TP: $2,319
  SOL/USDT    │ +2.1%  │ Entry: $98.20  │ SL: $93.29  │ TP: $99.67
  XRP/USDT    │ +0.5%  │ Entry: $0.615  │ SL: $0.584  │ TP: $0.624
  DOT/USDT    │ -1.3%  │ Entry: $8.45   │ SL: $8.03   │ TP: $8.58

Next Action: Scanning for entry (15s)
System Health: ✅ NORMAL
```

### Log Output Example

```
2026-02-10 19:42:15 ┃ 🦅 IBIS AGENT STARTED
2026-02-10 19:42:22 ┃ 📊 Market regime: VOLATILE (opportunity zone)
2026-02-10 19:42:45 ┃ 🔍 Scanned 1,247 pairs in 23.1s
2026-02-10 19:42:46 ┃ 🎯 Found 18 quality setups (score >= 70)
2026-02-10 19:43:02 ┃ ✅ BUY ORDER: 15.4 SOL @ $98.20
                      │  Score: 87/100 │ Confidence: 92%
                      │  SL: $93.29 (-5%) │ TP: $99.67 (+1.5%)
2026-02-10 19:43:15 ┃ 📊 Learning: VOLATILE_aggressive_entry = 14 trades, 71% WR
2026-02-10 19:55:30 ┃ 🟢 POSITION CLOSED: XRP/USDT
                      │  Exit Reason: TAKE_PROFIT (+1.51%)
                      │  P&L: +$0.41
2026-02-10 19:56:12 ┃ ✅ BUY ORDER: 8 XRP @ $0.615
                      │  Score: 76/100 │ Confidence: 85%
2026-02-10 20:02:45 ┃ 📈 Daily Summary:
                      │  Trades: 19 │ W: 12 │ L: 7 │ WR: 63.2%
                      │  P&L: +$2.86 │ Time: 78.1 minutes
```

---

## Dashboard Symbols

```
💰 Portfolio value             🎯 Best opportunity score
🟢 Profit/positive             🔴 Loss/negative
📊 Data/metrics                ✅ Success/trade executed
❌ Failure/error               ⚠️ Warning/alert
🔍 Scanning activity           📈 Market moving up
📉 Market moving down          ◐ Market regime indicator
🧠 Learning system active      🔥 Prime opportunity
```

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

---

## 📖 The IBIS Legend

In ancient Egyptian mythology, the ibis was sacred to **Thoth** - god of wisdom, writing, and knowledge. 

The Egyptians believed the ibis embodied divine wisdom and served as a messenger between the mortal and divine worlds. It was revered for its ability to:

- **Observe with precision** - keenly aware of its surroundings
- **Adapt to conditions** - thriving in different environments  
- **Navigate wisely** - finding the best path forward
- **Communicate effectively** - bridging different realms

**IBIS the trading agent embodies these same qualities** - observing markets with precision, adapting to conditions, navigating wisely, and communicating insights to its operators.

---

## 📚 Documentation

| Document | Purpose |
|----------|---------|
| **[README.md](./README.md)** | You are here - project overview |
| **[DEVELOPERS.md](./DEVELOPERS.md)** | Technical architecture & code walkthrough |
| **[QUICKREF.md](./QUICKREF.md)** | Quick reference for commands & troubleshooting |
| **[AGENTS.md](./AGENTS.md)** | Guide for AI assistants & automation |
| **[CONTRIBUTING.md](./CONTRIBUTING.md)** | How to contribute to IBIS |
| **[DEPLOYMENT.md](./DEPLOYMENT.md)** | Production deployment guide |
| **[CHANGELOG.md](./CHANGELOG.md)** | Version history & releases |

---

## 🔗 Links & Resources

### Exchanges
- **[KuCoin](https://www.kucoin.com)** - Primary trading exchange
- **[Binance](https://www.binance.com)** - Comparison & reference data

### Market Data APIs
- **[CoinGecko](https://www.coingecko.com)** - Free market data (no API key needed)
- **[Messari](https://messari.io)** - Professional metrics & insights
- **[CoinAPI](https://www.coinapi.io)** - Real-time cryptocurrency data
- **[Nansen](https://app.nansen.ai)** - Smart money tracking
- **[Glassnode](https://glassnode.com)** - On-chain analytics

### Developer Resources
- **[The Osiris Labs](https://www.theosirislabs.com)** - Project home
- **[GitHub Repository](https://github.com/The-Osiris-Labs/IBIS-AGI-TRADER)** - Source code
- **[Issue Tracker](https://github.com/The-Osiris-Labs/IBIS-AGI-TRADER/issues)** - Bug reports & features

---

## 📜 License

IBIS is released under the MIT License. See [LICENSE](./LICENSE) for details.

---

## ⚖️ Disclaimer

**Trading cryptocurrency carries SIGNIFICANT RISK.** 

- Past performance does not guarantee future results
- You can lose money trading, even with IBIS
- Only trade with capital you can afford to lose
- This software is provided "as is" for educational purposes
- The authors take no responsibility for trading losses

### Risk Management Reminder
IBIS has built-in protections (stop-loss, position limits, regime detection), but they can't eliminate risk. Markets can move faster than orders execute. Use paper trading to understand the system before risking real money.

---

## 🤝 Community & Support

### Getting Help
- **Issues**: Report bugs on [GitHub Issues](https://github.com/The-Osiris-Labs/IBIS-AGI-TRADER/issues)
- **Discussions**: Ask questions in [GitHub Discussions](https://github.com/The-Osiris-Labs/IBIS-AGI-TRADER/discussions)
- **Documentation**: Check [QUICKREF.md](./QUICKREF.md) for common questions

### Contributing
Want to improve IBIS? See [CONTRIBUTING.md](./CONTRIBUTING.md) for guidelines.

---

## 🏆 The IBIS Manifesto

> **"Wisdom is not about being right all the time.**
>
> **It's about learning from experience, adapting to change, and always protecting what matters.**
>
> **IBIS doesn't hunt for perfect trades.**
>
> **It hunts for probable ones, executes with discipline, and learns from every outcome.**
>
> **No hope. Only hunt."**

---

<div align="center">

### 🦅 Built with intelligence. Designed for markets. Trusted by traders. 🦅

**[IBIS - Autonomous Intelligent Trading](https://github.com/The-Osiris-Labs/IBIS-AGI-TRADER)**

Developed by **[The Osiris Labs](https://www.theosirislabs.com)**

*"Wisdom through learning. Profit through discipline."*

</div>
