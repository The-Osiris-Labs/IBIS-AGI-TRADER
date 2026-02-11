# Troubleshooting IBIS

Problems you might encounter and how to fix them.

---

## Quick Diagnostics

Before diving into specific issues, run these quick checks:

```bash
# Is IBIS running?
./start_ibis.sh status

# Check recent errors
tail -100 data/ibis_true.log | grep -i error

# View state
python3 -c "from ibis.data_consolidation import load_state; import json; s = load_state(); print('Positions:', len(s.get('positions', {})), '| Daily PnL:', s.get('daily', {}).get('pnl', 0))"

# Check memory
python3 -c "from ibis.data_consolidation import load_memory; m = load_memory(); print('Total trades in memory:', sum(p.get('trades', 0) for p in m.get('performance_by_symbol', {}).values()))"
```

---

## Common Issues

### "No opportunities found"

**Symptoms:**
- Log shows "FOUND 0 TRADEABLE candidates"
- Agent seems idle

**Causes:**
1. Market conditions aren't favorable (regime: FLAT, UNKNOWN)
2. Score threshold too high (no opportunities ≥ 70)
3. API connectivity issues

**Fixes:**

1. Check the regime:
   ```bash
   python3 -c "from ibis.data_consolidation import load_state; print('Regime:', s.get('market_regime', 'unknown'))"
   ```

2. Check if API is working:
   ```bash
   python3 -c "from ibis.exchange.kucoin_client import get_kucoin_client; import asyncio; async def test(): c = get_kucoin_client(); print(await c.get_ticker('BTC-USDT')); asyncio.run(test())"
   ```

3. Wait it out - IBIS won't trade in bad conditions

---

### Position showing but no trade happened

**Symptoms:**
- Position in state file but no trade record in memory
- Stuck buy orders

**Causes:**
1. Order placed but not yet filled
2. State desync between execution and logging

**Fix:**
```bash
# Check pending orders
python3 -c "
from ibis.data_consolidation import load_state
s = load_state()
print('Buy orders:', s.get('capital_awareness', {}).get('buy_orders', {}))
print('Positions:', list(s.get('positions', {}).keys()))
"
```

If orders are stuck, you may need to manually cancel:
```bash
./start_ibis.sh stop
# Delete the stale orders from state file manually
nano data/ibis_true_state.json
./start_ibis.sh watchdog
```

---

### Stop Loss not triggering

**Symptoms:**
- Trade goes past -5% without being closed
- Losses accumulating

**Causes:**
1. Slippage on volatile assets
2. Order book gap
3. API delay

**Fix:**
1. Check the actual fill price:
   ```bash
   python3 -c "
   from ibis.data_consolidation import load_state
   s = load_state()
   for sym, pos in s.get('positions', {}).items():
       pnl = (pos['current_price'] - pos['buy_price']) / pos['buy_price'] * 100
       print(f'{sym}: PnL {pnl:.2f}%')
   "
   ```

2. IBIS has a circuit breaker - if too many losses, it stops trading. Check:
   ```bash
   python3 -c "
   from ibis.data_consolidation import load_state
   s = load_state()
   print('Circuit breaker triggered:', s.get('agent_mode') == 'OBSERVING')
   "
   ```

---

### Memory and State are desynchronized

**Symptoms:**
- Memory shows 50 trades, state shows 5
- Performance data doesn't match reality

**Causes:**
1. State file was reset but memory wasn't
2. Bug in trade recording
3. Manual state modification without updating memory

**Fix:**
```bash
# Check the difference
python3 -c "
from ibis.data_consolidation import load_state, load_memory
s = load_state()
m = load_memory()

state_trades = s.get('daily', {}).get('trades', 0)
mem_trades = sum(p.get('trades', 0) for p in m.get('performance_by_symbol', {}).values())

print(f'State daily trades: {state_trades}')
print(f'Memory total trades: {mem_trades}')
print(f'Difference: {mem_trades - state_trades}')
"
```

If desync is significant, you can resync (caution: this resets learning):

```bash
./start_ibis.sh stop

# Backup first
cp data/ibis_true_memory.json data/ibis_true_memory.json.backup

# Reset memory (loses learning history)
python3 -c "
from ibis.data_consolidation import load_state, load_memory, save_memory

state = load_state()
daily = state.get('daily', {})

memory = load_memory()
memory['performance_by_symbol'] = {}
memory['learned_regimes'] = {}
memory['market_insights'] = []
memory['total_cycles'] = 0

save_memory(memory)
print('Memory reset complete')
"

./start_ibis.sh watchdog
```

---

### API Authentication Failed

**Symptoms:**
- Log shows "API authentication failed"
- No market data being fetched

**Causes:**
1. Wrong API credentials
2. API key permissions incorrect
3. IP restriction on API key

**Fix:**

1. Verify credentials:
   ```bash
   cat ibis/keys.env
   ```

2. Recreate API key on KuCoin:
   - Go to API Management
   - Delete old key
   - Create new key with Spot Trading permissions
   - Update `ibis/keys.env`

3. If using IP restriction, ensure server IP is whitelisted

---

### Agent keeps crashing

**Symptoms:**
- "IBIS has stopped working" messages
- Frequent restarts

**Causes:**
1. Memory leak
2. API rate limiting
3. Network instability

**Fix:**

1. Check crash logs:
   ```bash
   tail -200 data/ibis_true.log | grep -A5 "Exception\|Error"
   ```

2. Enable more verbose logging:
   ```bash
   export DEBUG=true
   ./start_ibis.sh restart
   ```

3. Check system resources:
   ```bash
   free -h
   df -h
   ```

4. If memory leak suspected, schedule periodic restarts:
   ```bash
   # Add to crontab
   crontab -e
   # Add: 0 4 * * * /root/projects/Dont enter unless solicited/AGI Trader/start_ibis.sh restart
   ```

---

### "Circuit Breaker Triggered"

**Symptoms:**
- Agent stops trading
- Mode switches to OBSERVING

**Causes:**
1. Too many losses in short period
2. Market conditions too dangerous
3. Manual trigger via `_should_stop_all_ops()`

**Fix:**
1. Check why it triggered:
   ```bash
   python3 -c "
   from ibis.data_consolidation import load_state
   s = load_state()
   print('Current mode:', s.get('agent_mode'))
   print('Recent losses:', s.get('daily', {}).get('losses', 0))
   print('Daily PnL:', s.get('daily', {}).get('pnl', 0))
   "
   ```

2. If market conditions are bad, wait them out

3. If it's a bug, restart:
   ```bash
   ./start_ibis.sh stop && ./start_ibis.sh watchdog
   ```

4. Manual reset (clears streak):
   ```bash
   python3 -c "
   from ibis.data_consolidation import load_state, save_state
   s = load_state()
   s['daily']['losses'] = 0
   s['agent_mode'] = 'HYPER_INTELLIGENT'
   save_state(s)
   "
   ```

---

### Out of Memory

**Symptoms:**
- Process killed by OOM killer
- "Cannot allocate memory" errors

**Fix:**

1. Check memory usage:
   ```bash
   ps aux | grep ibis
   ```

2. Clear caches:
   ```bash
   sync && echo 3 | sudo tee /proc/sys/vm/drop_caches
   ```

3. Restart with memory limits:
   ```bash
   ./start_ibis.sh stop
   ulimit -v 500000  # 500MB limit
   ./start_ibis.sh watchdog
   ```

4. If persistent, check for memory leaks in custom code

---

### Logs are too verbose

**Symptoms:**
- Log file growing too fast (GBs per day)
- Hard to find important messages

**Fix:**

1. Reduce logging level:
   ```bash
   export VERBOSE=false
   ./start_ibis.sh restart
   ```

2. Rotate logs daily:
   ```bash
   # Add to crontab
   crontab -e
   # Add: 0 0 * * * /usr/bin/find /root/projects/Dont enter unless solicited/AGI Trader/data -name "*.log" -mtime +7 -delete
   ```

3. Use logrotate:
   ```bash
   cat > /etc/logrotate.d/ibis <<EOF
   /root/projects/Dont enter unless solicited/AGI Trader/data/ibis_true.log {
       daily
       rotate 7
       compress
       delaycompress
       notifempty
       create 0644 root root
   }
   EOF
   ```

---

## Recovery Procedures

### Complete State Reset

When things are really broken:

```bash
./start_ibis.sh stop

# Backup everything
cp data/ibis_true_state.json state_backup.json
cp data/ibis_true_memory.json memory_backup.json

# Reset state
python3 -c "
from ibis.data_consolidation import save_state, save_memory

save_state({
    'positions': {},
    'market_regime': 'UNKNOWN',
    'agent_mode': 'HYPER_INTELLIGENT',
    'daily': {'trades': 0, 'wins': 0, 'losses': 0, 'pnl': 0},
    'capital_awareness': {'usdt_available': 100, 'usdt_locked_buy': 0, 'total_assets': 100}
})

save_memory({
    'learned_regimes': {},
    'performance_by_symbol': {},
    'market_insights': [],
    'adaptation_history': [],
    'total_cycles': 0
})

print('State and memory reset to defaults')
"

./start_ibis.sh watchdog
```

---

## Getting Help

When you need to ask for help:

1. Gather this information:
   - Output of `./start_ibis.sh status`
   - Last 50 lines of log: `tail -50 data/ibis_true.log`
   - State snapshot: `python3 -c "import json; print(json.dumps(load_state(), indent=2, default=str))"`
   - Python version: `python3 --version`

2. Check existing issues in the repo

3. Describe:
   - What you expected to happen
   - What actually happened
   - When it started
   - Any recent changes

---

## Prevention Tips

1. **Run in paper mode first** - Always test changes with fake money
2. **Check logs daily** - Catch issues early
3. **Back up state files** - Copy before major changes
4. **Limit position sizes** - Don't risk more than you can lose
5. **Schedule restarts** - Prevent memory leaks with weekly restarts
6. **Monitor disk space** - Logs can fill up fast

---

## Emergency Contacts

For critical situations:

1. **Stop everything:** `./start_ibis.sh stop`
2. **Kill processes:** `pkill -f ibis`
3. **Check holdings:** Log into KuCoin directly

---

**Still stuck?** Check [ARCHITECTURE.md](ARCHITECTURE.md) to understand the system better.
