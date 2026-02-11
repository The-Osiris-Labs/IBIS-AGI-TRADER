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

# 🦅 IBIS - Autonomous Trading Intelligence

<div align="center">

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-3776AB?style=flat-square&logo=python)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green?style=flat-square)](./LICENSE)
[![KuCoin](https://img.shields.io/badge/exchange-KuCoin-00C7B7?style=flat-square)](https://www.kucoin.com)

**Professional-grade autonomous trading agent | Production Ready**

[Repository](https://github.com/The-Osiris-Labs/IBIS-AGI-TRADER) •
[Documentation](./docs/README.md) •
[Report Bug](https://github.com/The-Osiris-Labs/IBIS-AGI-TRADER/issues)

</div>

---

## 🎯 What IBIS Is Not

This isn't a "set and forget" script. IBIS is a sophisticated trading intelligence that:

- **Thinks** - Evaluates 900+ markets using 8 technical indicators + sentiment + on-chain data
- **Decides** - Scores every opportunity 0-100 based on multi-factor analysis
- **Adapts** - Switches strategies based on 8 market regimes (bull, bear, volatile, flat...)
- **Learns** - Remembers performance by strategy+regime, improves over time
- **Protects** - Hard stop-loss limits, circuit breakers, emergency exits

---

## 🖥️ In Action

### Market Scan & Regime Detection
```
[2026-02-11 14:09:34]    📊 Found 945 active trading pairs
[2026-02-11 14:09:34]    📊 Fear & Greed: 11 (Extreme Fear) | score: 20
[2026-02-11 14:09:34]    📊 REGIME: VOLATILE
[2026-02-11 14:09:34]       momentum: -4.57 | vol: 0.2095 | trend: 20.0
[2026-02-11 14:09:34]       consistency: 0.81 | +: 3 -: 12
```

### Multi-Source Intelligence
```
[2026-02-11 14:08:42]    🧠 Unified intel for FLOCK: 74.5 (sources: 6/6)
[2026-02-11 14:08:42]       sentiment: 52.0 | onchain: 85.0 | social: 65.0
[2026-02-11 14:08:42]       news: 45.0 | whale: 78.0 | volume: 72.0
```

### Technical Indicator Analysis
```
[2026-02-11 14:08:42]    📊 INDICATORS: RSI:32/OVERSOLD MACD:BULLISH
[2026-02-11 14:08:42]       BB:BULLISH MA:BULLISH OBV:BULLISH STOCH:OVERSOLD
[2026-02-11 14:08:42]       Composite:68.5
```

### Capital Awareness
```
[2026-02-11 14:10:10]    💰 CAPITAL: $4.92 total | $4.92 avail
[2026-02-11 14:10:10]       $0.00 in buy orders | $70.86 in holdings
[2026-02-11 14:10:10]       Today's PnL: +$0.12 | Win Rate: 51%
```

### Trade Execution
```
[2026-02-11 14:08:42]    🎯 BUY SIGNAL: FLOCK (Score: 87/100)
[2026-02-11 14:08:42]       Price: $0.0421 | TP: $0.0427 | SL: $0.0400
[2026-02-11 14:08:42]       📊 INDICATORS: RSI:32/OVERSOLD MACD:BULLISH
[2026-02-11 14:08:42]       ✅ SUCCESS: Buy order placed for 119.1 FLOCK @ $0.0421
```

### Position Management
```
[2026-02-11 14:15:23]    🔴 EXIT TRIGGER: FLOCK
[2026-02-11 14:15:23]       Reason: TAKE_PROFIT | Exit: $0.0428
[2026-02-11 14:15:23]       PnL: +$0.07 (+1.66%)
[2026-02-11 14:15:23]       🎉 Target achieved! Locking in profits.
```

---

## 🧠 Intelligence Architecture

### The 8 Technical Indicators

| Indicator | Purpose | Signal Strength |
|-----------|---------|-----------------|
| **RSI (14)** | Momentum speed | Oversold (<30) / Overbought (>70) |
| **MACD (12/26/9)** | Trend direction | Bullish/Bearish histogram |
| **Bollinger Bands (20/2)** | Volatility | Breakout detection |
| **Moving Averages (20/50)** | Trend strength | Price above/below MA |
| **ATR (14)** | Volatility level | Stop loss sizing |
| **OBV** | Volume flow | Trend confirmation |
| **Stochastic (14/3)** | Momentum | Oversold/overbought |
| **VWAP** | Fair value | Institutional benchmark |

### Scoring Formula

```
Final Score = Technical (60%) + Unified Intel (20%) + Volume (15%) + Regime Fit (5%)
```

### Market Regimes

| Regime | Market Condition | IBIS Behavior |
|--------|------------------|----------------|
| `STRONG_BULL` | Raging optimism | Aggressive, larger positions |
| `BULL` | Mild uptrend | Standard buys |
| `NORMAL` | Average | Cautious approach |
| `VOLATILE` | Quick moves | Smaller positions |
| `FLAT` | Sideways | Wait for clarity |
| `BEAR` | Downtrend | Defensive |
| `STRONG_BEAR` | Crash | Stay out |
| `UNKNOWN` | Unclear | Extra cautious |

### Intelligence Sources

1. **Technical Analysis** - 8 indicators from candle data
2. **Sentiment Analysis** - VADER, news, social media
3. **On-Chain Data** - Whale movements, exchange flows
4. **Fear & Greed Index** - Market sentiment
5. **Cross-Exchange Monitoring** - Arbitrage opportunities
6. **Volume Analysis** - 24h volume, order flow

---

## ⚙️ Risk Management

IBIS has hard limits that protect your capital:

### Hard Limits (Unchangeable)

| Setting | Value | Protection |
|---------|-------|-------------|
| Stop Loss | 5% | Max loss per trade |
| Take Profit | 1.5% | Lock in profits |
| Max Positions | 5 | Diversification limit |
| Max Position Size | 50% | Concentration limit |
| Portfolio Heat | 60% | Max exposure |

### Adaptive Protections

- **Circuit Breaker** - Stops trading after X losses
- **Regime Switch** - Adapts to market conditions
- **Alpha Decay** - Exits weakening signals
- **Capital Recycling** - Reallocates from losers to winners

---

## 📁 Project Structure

```
IBIS/
├── ibis_true_agent.py           # Main agent (5000+ lines)
├── ibis/                        # Core modules
│   ├── core/
│   │   └── trading_constants.py # Risk settings (100+ params)
│   ├── exchange/
│   │   └── kucoin_client.py     # KuCoin API integration
│   ├── indicators/
│   │   └── indicators.py        # RSI, MACD, BB, MA, ATR, OBV...
│   ├── enhanced_intel.py        # Multi-source intelligence
│   ├── free_intelligence.py     # Free data APIs
│   └── cross_exchange_monitor.py # Multi-exchange analysis
├── data/                        # Runtime data (gitignored)
│   ├── ibis_true_state.json    # Current positions, capital
│   ├── ibis_true_memory.json   # Learned patterns
│   └── ibis_true.log           # Full activity log
└── docs/                       # Documentation
    ├── ARCHITECTURE.md         # System design
    ├── CONFIG.md               # Configuration reference
    ├── DEVELOPMENT.md          # Developer guide
    ├── QUICKSTART.md           # Setup guide
    └── TROUBLESHOOTING.md      # Common issues
```

---

## 🚀 Quick Start

```bash
# 1. Configure API keys
nano ibis/keys.env

# 2. Start in paper mode
./start_ibis.sh watchdog

# 3. Watch the logs
tail -f data/ibis_true.log
```

**⚠️ Always test in paper mode first!**

---

## 📊 System Capabilities

| Capability | Value |
|------------|-------|
| Markets Scanned | 900+ crypto pairs |
| Scan Frequency | Continuous (configurable) |
| Technical Indicators | 8 (RSI, MACD, BB, MA, ATR, OBV, Stochastic, VWAP) |
| Intelligence Sources | 6 (technical, sentiment, on-chain, news, whale, volume) |
| Market Regimes | 8 (bull, bear, volatile, flat...) |
| Risk Controls | Hard stop-loss, take-profit, position limits |
| Learning | Persistent memory across restarts |

### Production-Ready Features

- **Zero Human Intervention** - Runs 24/7 with watchdog auto-restart
- **Hard Risk Limits** - Stop-loss, position caps, circuit breakers
- **Multi-Source Intelligence** - Technical + sentiment + on-chain + volume
- **Adaptive Strategies** - 8 regimes, 8+ strategy modes
- **Persistent Learning** - Remembers performance by strategy+regime
- **Production Security** - API keys isolated, data gitignored

---

## 🎓 Philosophy

```
"NO HOPE. ONLY HUNT."
```

IBIS doesn't hope markets will go up. It doesn't hope a trade will recover. It hunts opportunities where the odds are in its favor, takes profits quickly, and cuts losses faster.

---

## 📖 Documentation

| Guide | Audience | Purpose |
|-------|----------|---------|
| [QUICKSTART.md](./docs/QUICKSTART.md) | New Users | Setup in 10 minutes |
| [ARCHITECTURE.md](./docs/ARCHITECTURE.md) | Everyone | How IBIS works |
| [CONFIG.md](./docs/CONFIG.md) | Devs | All settings explained |
| [DEVELOPMENT.md](./docs/DEVELOPMENT.md) | Devs | Add indicators, strategies |
| [TROUBLESHOOTING.md](./docs/TROUBLESHOOTING.md) | Everyone | Fix problems |

---

## 🔒 Security

- **API Keys** - Stored in `ibis/keys.env` (gitignored)
- **State Data** - `data/` directory (gitignored)
- **No External Dependencies** - All data sources optional
- **Circuit Breakers** - Emergency stop mechanisms

---

## 🤝 License

MIT License - See [LICENSE](./LICENSE)

---

## 🦅 About

**IBIS** (Intelligent Banking & Investment System) is developed by **The Osiris Labs** - building intelligent systems for tomorrow's markets.

*"Messenger of Thoth • Keeper of Balance • Oracle of Hunts"*

---

**Happy hunting.** 🦅
