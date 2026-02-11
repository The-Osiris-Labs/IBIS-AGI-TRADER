# Getting Started with IBIS

This guide walks you through setting up IBIS and making your first run.

---

## Prerequisites

- A Linux server (Ubuntu 20.04+ recommended)
- Python 3.9 or higher
- KuCoin account with API credentials
- About 10 minutes of free time

---

## Step 1: Get Your API Keys

IBIS trades on KuCoin, so you need API access:

1. Log into [KuCoin](https://www.kucoin.com)
2. Go to **API Management**
3. Create a new API key:
   - Name: "IBIS Trading"
   - Permissions: **Spot Trading** (read and trade)
   - IP Restriction: Optional but recommended
4. Copy your:
   - API Key
   - API Secret
   - Passphrase

---

## Step 2: Configure IBIS

Edit the keys file:

```bash
nano ibis/keys.env
```

Add your credentials:

```bash
KUCOIN_API_KEY=your_api_key_here
KUCOIN_API_SECRET=your_api_secret_here
KUCOIN_API_PASSPHRASE=your_passphrase_here
```

Save and exit (Ctrl+X, then Y, then Enter).

---

## Step 3: Test with Paper Trading

**IMPORTANT:** Always test in paper mode first!

Paper mode simulates trading with fake money. It feels exactly like real trading - same prices, same logic - but your money stays safe.

```bash
# Set paper mode
export PAPER_TRADING=true

# Start IBIS
./start_ibis.sh watchdog
```

Watch the logs:

```bash
tail -f data/ibis_true.log
```

You should see IBIS starting up, scanning markets, and either finding opportunities or waiting for better conditions.

---

## Step 4: Go Live (When You're Ready)

Once you're comfortable with paper mode:

```bash
# Unset paper mode
unset PAPER_TRADING

# Or edit keys.env to remove PAPER_TRADING=true

# Restart IBIS
./start_ibis.sh restart
```

---

## What You'll See

When IBIS runs, you'll see output like this:

```
🦅 IBIS TRUE TRADER v1.0
   Initializing...
   Loading state...
   🚀 Initializing LIMITLESS optimizations...
   ✅ Enhanced Intel Streams: ACTIVE
   📊 Found 847 active trading pairs
   🔍 DISCOVERING TRADING PAIRS...
   📊 Found 520 active trading pairs after filtering
   🔍 Analyzing 30 priority symbols...
   ✅ Analyzed 12 high-quality opportunities
   📊 Regime: NORMAL
   🤖 Mode: HYPER_INTELLIGENT
   🎯 ANALYZING 12 opportunities for trade entry...
   🔥 FOUND 3 TRADEABLE candidates
```

When it finds a trade, you'll see:

```
🎯 BUY SIGNAL: FLOCK (Score: 87/100)
   Price: $0.0421 | TP: $0.0427 | SL: $0.0400
   📊 INDICATORS: RSI:32/OVERSOLD MACD:BULLISH Composite:68.5
✅ SUCCESS: Buy order placed for 119.1 FLOCK @ $0.0421
```

When it closes a trade:

```
🔴 EXIT TRIGGER: FLOCK
   Reason: TAKE_PROFIT | Exit: $0.0428
   PnL: +$0.07 (+1.66%)
```

---

## Checking on IBIS

```bash
# Is it running?
./start_ibis.sh status

# View recent activity
tail -100 data/ibis_true.log

# View current positions
python3 -c "import json; print(json.dumps(
    json.load(open('data/ibis_true_state.json'))['positions'], 
    indent=2
))"

# View learning memory
python3 -c "import json; print(json.dumps(
    json.load(open('data/ibis_true_memory.json']))['performance_by_symbol'], 
    indent=2, default=str
))"
```

---

## Common First-Run Questions

### "It found 0 opportunities - is it broken?"

Probably not. IBIS is selective. It won't trade unless conditions are favorable. Try:

1. Checking the log: `tail -f data/ibis_true.log`
2. Looking at the regime: Is it FLAT or UNKNOWN?
3. Waiting a few cycles - IBIS scans every 10 minutes by default

### "Paper mode vs real mode - what's the difference?"

Nothing in the logic. Paper mode just doesn't execute real orders. Same prices, same decisions, zero risk.

### "Can I change the risk settings?"

Yes, but be careful. Start with paper trading and the default settings. Understand what each setting does before changing it.

---

## Next Steps

- Read [ARCHITECTURE.md](ARCHITECTURE.md) to understand how IBIS works
- Read [CONFIG.md](CONFIG.md) to customize settings
- Read [TROUBLESHOOTING.md](TROUBLESHOOTING.md) if something goes wrong

---

## Pro Tips

1. **Start with paper trading** - Seriously, don't skip this
2. **Check the log daily** - `tail -f data/ibis_true.log`
3. **Let it run** - IBIS needs time to learn. Don't micromanage
4. **Back up your state** - Copy `data/ibis_true_state.json` and `data/ibis_true_memory.json` regularly
5. **Watch the regime** - IBIS behaves differently in bull vs bear markets

---

**Need help?** Check [TROUBLESHOOTING.md](TROUBLESHOOTING.md) or review the log for clues.
