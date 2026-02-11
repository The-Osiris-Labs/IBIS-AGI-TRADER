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

# 🦅 IBIS - The Trading Hawk

**An autonomous trading agent that watches crypto markets, finds opportunities, executes trades, and learns from every cycle.**

Think of it as a hawk perched on your shoulder, constantly scanning the horizon for prey. When it spots something promising (score ≥ 70), it strikes. When conditions turn dangerous, it protects your capital. And every day, it gets a little smarter.

---

## What IBIS Actually Does

IBIS isn't your typical trading bot that just buys green candles. It's a complete autonomous system:

1. **Watches** - Scans 900+ crypto pairs on KuCoin every few minutes
2. **Analyzes** - Uses 8 technical indicators, sentiment analysis, and market intelligence
3. **Scores** - Every opportunity gets a confidence score from 0-100
4. **Decides** - Buys when score ≥ 70, otherwise stays on the sidelines
5. **Protects** - Auto-sells at -5% loss or +1.5% profit
6. **Learns** - Remembers which strategies work in which market conditions

---

## Philosophy

```
"NO HOPE. ONLY HUNT."
```

IBIS doesn't hope markets will go up. It doesn't hope a trade will recover. It hunts opportunities where the odds are in its favor, takes profits quickly, and cuts losses faster.

---

## The Basics

### Key Numbers to Know

| Setting | Value | What It Means |
|---------|-------|---------------|
| Stop Loss | 5% | If a trade goes against you by 5%, IBIS exits automatically |
| Take Profit | 1.5% | When a trade gains 1.5%, IBIS takes the win |
| Min Trade | $5 | Won't bother with tiny positions |
| Max Positions | 5 | Limits exposure at any given time |

### Score Breakdown

| Score | Meaning | Action |
|-------|---------|--------|
| 95-100 | God tier opportunity | Full position size |
| 85-94 | Strong setup | Larger position |
| 70-84 | Good opportunity | Standard position |
| 55-69 | Maybe, maybe not | Small position or skip |
| <55 | Not interested | Skip |

---

## Market Regimes

IBIS adapts its behavior based on current market conditions:

| Regime | Characteristics | IBIS Behavior |
|--------|-----------------|----------------|
| **STRONG_BULL** | Raging optimism | Aggressive buying |
| **BULL** | Mild optimism | Standard buys |
| **NORMAL** | Average conditions | Cautious approach |
| **VOLATILE** | Quick moves, uncertainty | Smaller positions |
| **FLAT** | No direction | Wait for clarity |
| **BEAR** | Downtrend | Defensive |
| **STRONG_BEAR** | Blood in streets | Stay out |
| **UNKNOWN** | Unclear | Extra cautious |

---

## Quick Start

```bash
# 1. Set up your API keys (see QUICKSTART.md)
nano ibis/keys.env

# 2. Start in paper mode (recommended for first run)
./start_ibis.sh watchdog

# 3. Watch what it does
tail -f data/ibis_true.log
```

---

## Documentation

| Guide | Purpose |
|-------|---------|
| [QUICKSTART.md](QUICKSTART.md) | Get up and running in 10 minutes |
| [ARCHITECTURE.md](ARCHITECTURE.md) | Understand how IBIS works |
| [CONFIG.md](CONFIG.md) | Customize settings |
| [DEVELOPMENT.md](DEVELOPMENT.md) | Add new features |
| [TROUBLESHOOTING.md](TROUBLESHOOTING.md) | Fix problems |

---

## Files You'll Touch

| File | Purpose |
|------|---------|
| `ibis/keys.env` | Your API keys - **never share this** |
| `ibis/core/trading_constants.py` | Risk settings - don't touch without understanding |
| `data/ibis_true_state.json` | Current positions and daily stats |
| `data/ibis_true_memory.json` | IBIS's brain - learned patterns |
| `data/ibis_true.log` | Activity log - what IBIS is thinking |

---

## Commands

```bash
./start_ibis.sh watchdog   # Start with auto-restart on crash
./start_ibis.sh status     # Check if running
./start_ibis.sh stop       # Stop everything
./start_ibis.sh restart    # Restart cleanly
```

---

## For Non-Technical Users

IBIS runs itself. You don't need to tell it when to buy or sell. Just:

1. Set up your API keys
2. Start it with `./start_ibis.sh watchdog`
3. Check the log occasionally with `tail -f data/ibis_true.log`
4. If something looks wrong, run `./start_ibis.sh stop`

The agent learns from every trade and adapts its behavior over time.

---

## For Developers

Want to understand how IBIS works under the hood?

- [ARCHITECTURE.md](ARCHITECTURE.md) - System design and data flow
- [CONFIG.md](CONFIG.md) - All configuration options explained
- [DEVELOPMENT.md](DEVELOPMENT.md) - Adding new features

---

## Performance (Feb 2026)

| Metric | Value |
|--------|-------|
| Portfolio | ~$70 |
| Total Trades | 72 |
| Win Rate | 51% |
| Best Strategy | `VOLATILE_take_profit` (100% WR) |

---

## Questions?

- [QUICKSTART.md](QUICKSTART.md) - Getting up and running
- [TROUBLESHOOTING.md](TROUBLESHOOTING.md) - Something broken?
- [ARCHITECTURE.md](ARCHITECTURE.md) - How it all works

---

**Happy hunting.** 🦅
