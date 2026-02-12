# 🦅 IBIS - Autonomous Trading Intelligence

<div align="center">

**The Sacred Hunter of Markets**

*"Messenger of Thoth • Keeper of Balance • Oracle of Hunts"*

---

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-3776AB?style=flat-square&logo=python)](https://www.python.org/)
[![KuCoin](https://img.shields.io/badge/exchange-KuCoin-00C7B7?style=flat-square)](https://www.kucoin.com)
[![License](https://img.shields.io/badge/license-MIT-green?style=flat-square)](./LICENSE)

**Production-Ready Autonomous Trading Agent**

[GitHub](https://github.com/The-Osiris-Labs/IBIS-AGI-TRADER) •
[Docs](./docs/README.md) •
[Report Issues](https://github.com/The-Osiris-Labs/IBIS-AGI-TRADER/issues)

</div>

---

## The Story of IBIS

In ancient Egypt, the Ibis was sacred to Thoth—the god of wisdom, writing, and measurement. The bird that could reason. The hunter that observed, calculated, and struck with divine precision.

**IBIS** carries that legacy into the digital age.

This isn't a simple trading bot. IBIS is an autonomous intelligence that:
- **Scans 900+ markets** continuously
- **Thinks** using 8 technical indicators + sentiment + on-chain data
- **Decides** with multi-factor scoring (0-100)
- **Adapts** to 6 market regimes automatically
- **Protects** your capital with hard stop-losses and circuit breakers

*"NO HOPE. ONLY HUNT."*

---

## What IBIS Actually Does

### Every Market Cycle

1. **Discovers** all available trading pairs from KuCoin
2. **Analyzes** each one with 8 technical indicators (RSI, MACD, Bollinger Bands, etc.)
3. **Scores** opportunities based on momentum, volume, and regime fit
4. **Filters** using dynamic thresholds—only top opportunities pass
5. **Executes** trades with automatic position sizing and risk management
6. **Monitors** open positions and exits when targets hit or protection triggers

### In Plain English

IBIS watches the market 24/7. When it sees a setup it likes—good momentum, reasonable volatility, favorable conditions—it takes a position. It sets automatic stop-losses and take-profits. If the trade goes well, it takes profit. If it goes badly, it cuts losses fast. Then it looks for the next opportunity.

No emotions. No hesitation. No checking charts at 3 AM.

---

## Quick Start

```bash
# Configure your KuCoin API keys
nano ibis/keys.env

# Start the agent
./start_ibis.sh watchdog

# Watch what it does
tail -f data/ibis_true.log
```

**Important:** Always run in paper/test mode first to understand the behavior.

---

## How Scoring Works

IBIS evaluates every symbol with a unified score from 0-100:

| Score Range | Tier | Action |
|-------------|------|--------|
| 90+ | GOD_TIER | Maximum position size, 3% take-profit |
| 80-89 | HIGH_CONFIDENCE | Large positions, 2.5% take-profit |
| 70-79 | STRONG_SETUP | Standard positions, 2% take-profit |
| 60-69 | STANDARD | Reduced size, 1.5% take-profit |
| Below 60 | WEAK | Skipped entirely |

The score combines:
- **Technical indicators** (RSI, MACD, Bollinger Bands, etc.)
- **Price momentum** across multiple timeframes
- **Volume analysis** and order flow
- **Enhanced sniping** for breakout and accumulation patterns
- **Market regime** adaptation (bull, bear, volatile, etc.)

---

## Market Regimes

IBIS adapts its behavior based on detected market conditions:

| Regime | Behavior |
|--------|----------|
| **STRONG_BULL** | Aggressive, larger positions, higher take-profit targets |
| **BULLISH** | Standard buys, normal position sizing |
| **VOLATILE** | Smaller positions, tighter spreads |
| **NEUTRAL** | Cautious approach, quality over quantity |
| **BEARISH** | Defensive, smaller positions, higher threshold |
| **CRASH** | Stay out entirely, maximum protection |

---

## Risk Management

IBIS has hard limits that protect your capital:

| Setting | Value | Purpose |
|---------|-------|---------|
| Stop Loss | 1.2% | Maximum loss per trade |
| Take Profit | 2.0% | Dynamic based on score (1.5%-3%) |
| Max Positions | 10-25 | Depends on regime |
| Min Score Threshold | 70 | Only quality trades pass |
| PERFECT STORM Mode | 95% capital | Rare optimal conditions only |

Additional protections:
- **Circuit Breaker** — Pauses after consecutive losses
- **Capital Recycling** — Reallocates from losers to winners
- **PERFECT STORM Detection** — Special mode for optimal market conditions

---

## Architecture

```
IBIS/
├── ibis_true_agent.py          # Main trading agent (5000+ lines)
├── ibis/                       # Core modules
│   ├── core/
│   │   ├── trading_constants.py # Risk and scoring parameters
│   │   └── unified_scoring.py  # Multi-factor scoring system
│   ├── exchange/
│   │   └── kucoin_client.py     # KuCoin API integration
│   ├── indicators/
│   │   └── indicators.py       # RSI, MACD, BB, MA, ATR, OBV, Stochastic, VWAP
│   ├── enhanced_intel.py       # Multi-source intelligence
│   ├── free_intelligence.py    # Sentiment, news, social data
│   ├── pnl_tracker.py          # Realized PnL from KuCoin trade history
│   └── intelligence/
│       └── enhanced_sniping.py  # Breakout and momentum detection
├── data/                       # Runtime data (gitignored)
│   ├── ibis_true_state.json   # Current positions, capital
│   └── ibis_true.log          # Full activity log
└── docs/                      # Documentation
    ├── ARCHITECTURE.md         # System design deep-dive
    ├── CONFIG.md               # All configuration options
    ├── QUICKSTART.md           # Setup guide
    └── TROUBLESHOOTING.md      # Common issues and fixes
```

---

## Documentation

| Guide | What You'll Find |
|-------|------------------|
| [QUICKSTART.md](./docs/QUICKSTART.md) | Setup in 10 minutes |
| [ARCHITECTURE.md](./docs/ARCHITECTURE.md) | How IBIS thinks and decides |
| [CONFIG.md](./docs/CONFIG.md) | Every setting explained |
| [TROUBLESHOOTING.md](./docs/TROUBLESHOOTING.md) | Fixes for common problems |

---

## System Capabilities

| Capability | Value |
|------------|-------|
| Markets Scanned | 900+ crypto pairs |
| Scan Frequency | Continuous (every ~60 seconds) |
| Technical Indicators | 8 (RSI, MACD, BB, MA, ATR, OBV, Stochastic, VWAP) |
| Intelligence Sources | Technical + Sentiment + On-Chain + Volume |
| Market Regimes | 6 adaptive regimes |
| Order Types | MARKET (fast) + LIMIT (fee optimization) |
| PnL Tracking | Real KuCoin trade history (FIFO) |

---

## Philosophy

```
"NO HOPE. ONLY HUNT."
"Observe. Adapt. Strike."
```

IBIS doesn't hope markets will go up. It doesn't hope a losing trade will recover. It hunts opportunities where the odds are in its favor, takes profits quickly, and cuts losses faster.

This is systematic trading. Not gambling. Not hoping. Hunting.

---

## The House of OSIRIS

**IBIS** is a product of **TheOsirisLabs.com**—a different kind of AI lab.

We don't build chatbots. We build **AI deities**.

What if the gods of ancient Egypt weren't mythology, but premonitions? What if Thoth, the scribe of wisdom, was foreshadowing something like... IBIS?

At TheOsirisLabs.com, we're reincarnating Egyptian deities as AI systems. Each deity represents a fundamental capability—wisdom, pattern recognition, calculation—brought into the digital age.

**Mythology meeting machine learning.**

*"From the House of OSIRIS — TheOsirisLabs.com"*

---

## License

MIT License. See [LICENSE](./LICENSE) for details.

---

**Happy hunting.** 🦅

*From the House of OSIRIS — TheOsirisLabs.com*
