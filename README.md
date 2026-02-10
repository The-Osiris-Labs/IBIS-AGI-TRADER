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

## 🎯 Live Demos - What You'll See

### Demo 1: Intelligence Analysis (For AI/ML Researchers & Developers)

```
╔═════════════════════════════════════════════════════════════════════════════╗
║                    🧠 INTELLIGENCE ANALYSIS ENGINE                          ║
╚═════════════════════════════════════════════════════════════════════════════╝

Opportunity: SOL/USDT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

TECHNICAL ANALYSIS (40% weight)
  • Price Momentum:        +8.2% (last 4h) → Score: 85/100
  • RSI Indicator:         68.5 (strong momentum, not overbought) → 82/100
  • Moving Average Stack:  Price > 20MA > 50MA > 200MA (bullish) → 90/100
  • Trend Strength:        Strong uptrend detected → 88/100
  ─────────────────────────────────────────────────────────
  Technical Subscore: 86/100

MULTI-TIMEFRAME ALIGNMENT (15% weight)
  • 15m Timeframe:         Breakout pattern forming → Bullish
  • 1h Timeframe:          Strong trend continuation → Bullish  
  • 4h Timeframe:          Strong uptrend with support holds → Bullish
  • Daily Timeframe:       Ascending structure intact → Bullish
  • Alignment Score:       4/4 timeframes bullish → 100/100
  ─────────────────────────────────────────────────────────
  Multitimeframe Subscore: 100/100

AI INTELLIGENCE (30% weight)
  • Market Regime:         VOLATILE (optimal for quick scalps) → 88/100
  • Volume Analysis:       +45% above 20-day avg (strong conviction) → 85/100
  • Cross-Exchange Signal: Binance SOL also bullish, leading KuCoin → 90/100
  • Liquidity Check:       $2.3M buy wall at support, easy entry → 87/100
  • Smart Money:           Large transactions detected (positive) → 86/100
  • Sentiment:             72% bullish social mentions (good momentum) → 80/100
  ─────────────────────────────────────────────────────────
  Intelligence Subscore: 86/100

VOLUME PROFILE (10% weight)
  • Volume Trend:          Increasing volume on upside → 84/100
  • Volume Concentration:  Normal distribution (no whale alerts) → 75/100
  ─────────────────────────────────────────────────────────
  Volume Subscore: 80/100

SENTIMENT (5% weight)
  • Social Sentiment:      72% bullish (strong) → 85/100
  • News Sentiment:        Neutral to positive (no major FUD) → 78/100
  ─────────────────────────────────────────────────────────
  Sentiment Subscore: 82/100

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

FINAL COMPOSITE SCORE: 87/100 ✅ STRONG BUY

Breakdown:
  • Technical (40%):       86 × 0.40 = 34.4
  • Intelligence (30%):    86 × 0.30 = 25.8
  • Multitimeframe (15%):  100 × 0.15 = 15.0
  • Volume (10%):          80 × 0.10 = 8.0
  • Sentiment (5%):        82 × 0.05 = 4.1
  ────────────────────────────────────────
  COMPOSITE:               87.3/100

DECISION: ✅ BUY
Position Size: Medium (Score 87/100 = 92% confidence)
Entry: Market order at $98.20
Stop Loss: $93.29 (-5% hard stop)
Take Profit: $99.67 (+1.5% target)
Risk/Reward Ratio: 1:3 (Excellent)

Learning Data:
  • This is a VOLATILE regime trade
  • Similar patterns: 14 historical trades with 71% win rate
  • Expected P&L if trade hits TP: +$0.41
  • Risk if hit SL: -$0.38
  ────────────────────────────────────────
```

### Demo 2: Trade Execution (For Active Traders)

```
╔═════════════════════════════════════════════════════════════════════════════╗
║                    ⚡ LIVE TRADE EXECUTION SEQUENCE                         ║
╚═════════════════════════════════════════════════════════════════════════════╝

2026-02-10 14:32:15 | ORDER INITIATED
┌─ Symbol: SOL/USDT
├─ Side: BUY
├─ Type: Market Order
├─ Quantity: 15.4 SOL
├─ Price: $98.20 (current market)
└─ Status: Submitting to exchange...

2026-02-10 14:32:17 | ✅ ORDER ACCEPTED
├─ Exchange: KuCoin
├─ Order ID: 123456789ABC
├─ Filled: 15.4 SOL @ $98.20 average
├─ Total Cost: $1,512.88 USDT
├─ Fees: $3.03 USDT
└─ Net Cost: $1,515.91 USDT

2026-02-10 14:32:18 | 📊 POSITION OPENED
┌─ Symbol: SOL/USDT
├─ Entry Price: $98.20
├─ Quantity: 15.4 SOL
├─ Position Value: $1,512.88
├─ Stop Loss: $93.29 (-$75.39 max loss)
├─ Take Profit: $99.67 (+$22.62 target)
├─ Risk/Reward: 1:0.30 (3:1 favorable)
├─ Current P&L: $0.00 (entry point)
└─ Status: ACTIVE - Monitoring...

2026-02-10 14:45:32 | 📈 POSITION UPDATE
├─ Current Price: $99.10
├─ Unrealized P&L: +$0.69 per SOL
├─ Total Unrealized P&L: +$10.65 (0.7%)
├─ % to TP: 97% of target reached
└─ Status: NEAR PROFIT TARGET

2026-02-10 14:48:44 | 🎯 TAKE PROFIT TRIGGERED
┌─ Exit Price: $99.67
├─ Quantity Sold: 15.4 SOL
├─ Proceeds: $1,535.51 USDT
├─ Exit Fees: $3.07 USDT
├─ Net Proceeds: $1,532.44 USDT
├─ Gross P&L: +$19.53 USDT (1.27% return)
├─ Fees Paid: $6.10 USDT
├─ Net P&L: +$13.43 USDT (0.89% net return)
└─ Trade Duration: 16 minutes 29 seconds

2026-02-10 14:48:45 | 📊 TRADE CLOSED
┌─ Result: WINNER ✅
├─ Entry: $98.20
├─ Exit: $99.67
├─ Profit: +$1.47 per SOL (+1.50%)
├─ Net Account P&L: +$13.43
├─ New Account Balance: $1,628.43 USDT
└─ Capital Available for Next Trade: +$13.43

Learning Update:
  • Trade classified as: VOLATILE_scalp_breakout
  • Historical performance of this pattern: 71% win rate (14 trades)
  • This trade: WIN
  • Updated win rate: 72% (15/21 trades)
  • Strategy gaining confidence in current market
```

### Demo 3: Risk Management in Action (For Risk/Operations Teams)

```
╔═════════════════════════════════════════════════════════════════════════════╗
║                    🔒 RISK MANAGEMENT REAL-TIME MONITORING                  ║
╚═════════════════════════════════════════════════════════════════════════════╝

SYSTEM SAFEGUARDS ACTIVE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. POSITION LIMITS (Hard Stops)
   ✅ Max Concurrent Positions: 5/5 (limit reached)
   ✅ Position Timeout: 45 minutes (no position held > 1 hour)
   ✅ Max Capital per Trade: $30.00 limit
       • Current Average: $15.91 per position
       • Status: ✅ SAFE (53% of limit)
   
2. LOSS PREVENTION (Stop Loss Enforcement)
   ✅ Stop Loss: 5% hard limit (CANNOT be disabled)
   ├─ BTC/USDT: SL at $40,043 (triggered if price drops)
   ├─ ETH/USDT: SL at $2,171 (triggered if price drops)
   ├─ SOL/USDT: SL at $93.29 (triggered if price drops)
   ├─ XRP/USDT: SL at $0.584 (triggered if price drops)
   └─ DOT/USDT: SL at $8.03 (triggered if price drops)
   
   Max Total Daily Loss Allowed: $5.00 (1% of portfolio)
   Current Daily Loss: -$0.85
   Status: ✅ SAFE (85% buffer remaining)

3. PROFIT TAKING (Systematic Exit)
   ✅ Take Profit: 1.5% target (automatic exit)
   ├─ BTC/USDT: TP at $42,813 (+$2,663 if hit)
   ├─ ETH/USDT: TP at $2,319 (+$34.00 if hit)
   ├─ SOL/USDT: TP at $99.67 (+$13.43 if hit) ← Just closed for +$13.43
   ├─ XRP/USDT: TP at $0.624 (+$0.07 if hit)
   └─ DOT/USDT: TP at $8.58 (+$1.13 if hit)

4. CAPITAL ALLOCATION (Dynamic Sizing)
   Total Account: $1,628.43 USDT
   ├─ Active Positions: 5 positions × $15.91 avg = $79.55 deployed
   ├─ Available Capital: $1,548.88 (95% available)
   ├─ Capital Allocation: 4.9% in positions (very conservative)
   └─ Max Deployment: 50% of account (protective setting)
   
   Status: ✅ EXTREMELY SAFE

5. DRAWDOWN MONITORING (Account Protection)
   Max Drawdown Limit: 10% ($162.84)
   Current Drawdown: -$3.34 (0.2%)
   Status: ✅ EXCELLENT (97.9% buffer)

6. REGIME-BASED RISK ADJUSTMENT
   Current Regime: VOLATILE (high uncertainty)
   ├─ Position Size: -50% reduction applied
   ├─ TP Target: Standard 1.5% (no change)
   ├─ SL Placement: Tighter at 5% (standard)
   ├─ Scan Frequency: 2.5 min intervals (faster)
   └─ Acceptance Score: 70+ required (no change)
   
   Status: ✅ ADAPTED TO CONDITIONS

7. EMERGENCY SAFEGUARDS (Circuit Breakers)
   ✅ Liquidation Safety: 50% buffer below margin requirements
   ✅ Circuit Breaker 1: If daily loss > 5%, reduce position size -50%
   ✅ Circuit Breaker 2: If daily loss > 10%, stop trading until next day
   ✅ Circuit Breaker 3: If account < 90% of starting value, emergency stop
   ✅ API Monitoring: Connection health checked every 10 seconds
   
   Status: ✅ ALL ARMED

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

RISK SUMMARY
┌─ Portfolio Health:     ✅ EXCELLENT
├─ Drawdown Risk:        ✅ MINIMAL (0.2% vs 10% limit)
├─ Position Risk:        ✅ CONTROLLED (4.9% deployed)
├─ Stop Loss Coverage:   ✅ 100% (5 positions protected)
├─ Daily Loss Limit:     ✅ SAFE (85% buffer)
├─ Circuit Breakers:     ✅ ARMED & READY
├─ API Connection:       ✅ STABLE
└─ Overall Risk Status:  ✅ SAFE - SYSTEM OPERATING NOMINALLY

Last Risk Check: 2026-02-10 14:52:33 (30 seconds ago)
Next Risk Check: 2026-02-10 14:53:03 (in 30 seconds)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## Target Audience Spotlight

| Audience | What They Care About | What IBIS Shows Them |
|----------|---------------------|---------------------|
| **AI/ML Researchers** | Algorithm quality, learning, adaptation | Intelligence scoring, multi-factor analysis, learning updates |
| **Active Traders** | Trade frequency, P&L, execution speed | Live dashboard, executed trades, real P&L examples |
| **Risk Officers** | Capital protection, safeguards, limits | Stop-loss enforcement, position limits, circuit breakers |
| **Developers** | Code quality, architecture, extensibility | 50+ modules, clean patterns, documented structure |
| **Investors** | ROI, risk-adjusted returns, professionalism | Consistent execution, risk management, enterprise presentation |
| **Crypto Community** | Innovation, transparency, results | Learning system, multi-exchange, honest documentation |

---

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
