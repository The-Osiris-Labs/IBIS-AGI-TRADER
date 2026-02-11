# How IBIS Works - Architecture Guide

This document explains how IBIS works under the hood. No code snippets, just the concepts you need to understand the system.

---

## The Big Picture

IBIS is organized into four main layers that work together:

```
┌─────────────────────────────────────────────────────┐
│                   INTELLIGENCE LAYER               │
│   (Scans markets, analyzes opportunities, scores)   │
├─────────────────────────────────────────────────────┤
│                   DECISION LAYER                    │
│   (Chooses when to buy, sell, or wait)             │
├─────────────────────────────────────────────────────┤
│                   EXECUTION LAYER                   │
│   (Places orders, manages positions)                │
├─────────────────────────────────────────────────────┤
│                   MEMORY LAYER                      │
│   (Learns from past, improves over time)            │
└─────────────────────────────────────────────────────┘
```

Each layer is independent but feeds into the next. This separation makes IBIS robust - if one part fails, the others keep working.

---

## Intelligence Layer

This layer answers: "What's happening in the market?"

### What IBIS Monitors

1. **Price Data** - 900+ crypto pairs on KuCoin
2. **Order Book** - Buy/sell orders on the exchange
3. **Volume** - Trading activity levels
4. **News & Social** - Sentiment from Twitter, Reddit, news
5. **On-Chain Data** - Whale movements, exchange flows

### The 8 Technical Indicators

IBIS calculates 8 indicators for every opportunity:

| Indicator | What It Measures | Why It Matters |
|-----------|-----------------|----------------|
| RSI | Momentum speed | Finds oversold/overbought conditions |
| MACD | Trend direction | Catches trend changes early |
| Bollinger Bands | Volatility | Spot breakouts from consolidation |
| Moving Averages | Trend strength | Confirms uptrends/downtrends |
| ATR | Volatility level | Sets proper stop losses |
| OBV | Volume flow | Confirms moves with volume |
| Stochastic | Momentum | Another oversold/overbought check |
| VWAP | Fair value | Institutional benchmark |

### Scoring System

Each opportunity gets scored 0-100 based on:

- Technical indicators (60%)
- Unified intelligence (20%)
- Volume & liquidity (15%)
- Market regime fit (5%)

Score thresholds:
- **≥ 70**: Trade opportunity
- **< 70**: Wait for better conditions

---

## Decision Layer

This layer answers: "What should I do now?"

### The Main Loop

IBIS runs in an infinite loop, each cycle following the same pattern:

1. **Update awareness** - Check positions, capital, pending orders
2. **Learn** - Update memory from recent trades
3. **Scan markets** - Find new opportunities
4. **Detect regime** - What's the market doing?
5. **Execute strategy** - Buy, sell, or wait
6. **Monitor positions** - Check for TP/SL triggers
7. **Sleep** - Wait for next cycle

### Market Regimes

IBIS adapts its behavior based on 8 market regimes:

| Regime | Characteristics | IBIS Behavior |
|--------|----------------|---------------|
| STRONG_BULL | Raging bull market | Aggressive buying |
| BULL | Mild uptrend | Standard buys |
| NORMAL | Average conditions | Cautious approach |
| VOLATILE | Quick moves, high uncertainty | Smaller positions |
| FLAT | No direction | Wait for clarity |
| BEAR | Downtrend | Defensive |
| STRONG_BEAR | Crash | Stay out |
| UNKNOWN | Unclear | Extra cautious |

### Strategy Selection

IBIS has 8 built-in strategies:

- **HUNT** - Look for opportunities
- **HUNT_QUICK** - Fast-moving opportunities
- **ACCUMULATE** - Buy dips
- **REST** - Wait out bad conditions
- **DEFEND** - Protect capital
- **PRESERVE** - Maximum caution
- **OBSERVING** - Watch only, no trades
- **OPPORTUNISTIC** - Take what's given

---

## Execution Layer

This layer answers: "How do I actually trade?"

### Order Types

IBIS uses two order types:

1. **Limit Orders** - Specify price, waits for market to reach it
2. **Market Orders** - Execute immediately at best available price

### Position Management

For every position, IBIS calculates:

- **Entry size** - How much to buy
- **Take Profit (TP)** - Exit target (typically +1.5%)
- **Stop Loss (SL)** - Exit cutoff (typically -5%)
- **Trailing Stop** - Locks in profits (optional)

### Risk Limits

IBIS enforces these hard limits:

- Max 5 concurrent positions
- Max $30 per trade
- Min $5 per trade
- Max portfolio exposure: 60%

---

## Memory Layer

This layer answers: "What have I learned?"

### State File (`ibis_true_state.json`)

The current snapshot of everything:

```json
{
  "positions": {
    "FLOCK": {
      "quantity": 119.1,
      "buy_price": 0.0421,
      "current_price": 0.0425,
      "mode": "HYPER_INTELLIGENT",
      "regime": "VOLATILE",
      "tp": 0.0427,
      "sl": 0.0400
    }
  },
  "daily": {
    "trades": 5,
    "wins": 3,
    "losses": 2,
    "pnl": +0.45
  },
  "capital_awareness": {
    "usdt_available": 25.00,
    "total_assets": 95.00
  }
}
```

### Memory File (`ibis_true_memory.json`)

IBIS's learned experience:

```json
{
  "performance_by_symbol": {
    "FLOCK": {
      "trades": 3,
      "wins": 2,
      "losses": 1,
      "avg_pnl": 0.12
    }
  },
  "learned_regimes": {
    "VOLATILE": {
      "best_strategy": "VOLATILE_take_profit",
      "win_rate": 1.0
    }
  },
  "market_insights": [
    "FLOCK works well in VOLATILE regime"
  ]
}
```

### Learning Process

Every cycle, IBIS:

1. Records the current regime and what it did
2. Notes which trades won and which lost
3. Updates win rates for each strategy in each regime
4. Adapts behavior based on what worked

---

## Data Flow

Here's how data flows through the system:

```
MARKET DATA (prices, volume, order book)
         ↓
   INTELLIGENCE LAYER
   - Calculates 8 indicators
   - Gets sentiment data
   - Calculates composite score
         ↓
   DECISION LAYER
   - Detects regime
   - Selects strategy
   - Calculates position size
         ↓
   EXECUTION LAYER
   - Places order
   - Monitors TP/SL
   - Updates position state
         ↓
   MEMORY LAYER
   - Records trade result
   - Updates win rates
   - Adapts parameters
```

---

## Key Files

| File | Purpose | Changes? |
|------|---------|----------|
| `ibis_true_agent.py` | Main agent logic | Yes, when adding features |
| `ibis/core/trading_constants.py` | Risk settings | Rarely, with caution |
| `ibis/keys.env` | API keys | Never share |
| `data/ibis_true_state.json` | Current state | Auto-updated |
| `data/ibis_true_memory.json` | Learned memory | Auto-updated |
| `data/ibis_true.log` | Activity log | Auto-updated |

---

## Configuration Hierarchy

IBIS has three configuration layers:

### 1. Hard Limits (Unchangeable)

These protect your capital and can't be overridden:

- Stop Loss: 5%
- Take Profit: 1.5%
- Max Positions: 5
- Max Position Size: 50% of portfolio

### 2. Tunable Parameters (Can Change)

These adapt behavior within safe bounds:

- Min Trade Amount: $5-$50
- Scan Interval: 3-30 seconds
- Position Size: 20%-40% of available capital
- Regime Thresholds: Adjustable

### 3. Learning Data (Auto-Updated)

IBIS learns these from experience:

- Best strategies per regime
- Win rates per symbol
- Optimal entry conditions

---

## Failure Modes

IBIS handles failures gracefully:

1. **Network timeout** - Retries request up to 3 times
2. **API error** - Falls back to cached data
3. **Order rejected** - Logs error, continues trading
4. **Memory corruption** - Loads last known good state
5. **Crash** - Watchdog restarts agent automatically

---

## Monitoring Points

To understand what IBIS is doing:

1. **Log file** - `data/ibis_true.log` - Full activity stream
2. **State file** - Current positions and capital
3. **Memory file** - Historical performance
4. **Dashboard** - Console output each cycle

---

## For Developers

If you want to extend IBIS:

1. **Add new intelligence** - Extend `EnhancedIntelStreams`
2. **New indicators** - Add to `ibis/indicators/`
3. **New strategies** - Add to `execute_strategy()`
4. **New exchanges** - Implement exchange adapter
5. **New data sources** - Extend `FreeIntelligence`

See [DEVELOPMENT.md](DEVELOPMENT.md) for details.

---

## Summary

IBIS is a closed-loop autonomous system:

1. **Observes** - Collects market data continuously
2. **Thinks** - Analyzes using 8 indicators + sentiment
3. **Decides** - Scores opportunities, selects strategy
4. **Acts** - Executes trades with risk controls
5. **Learns** - Improves from every cycle

This loop runs continuously, making IBIS a truly autonomous trading agent.

---

**Questions?** Check [TROUBLESHOOTING.md](TROUBLESHOOTING.md) or dive into the code.
