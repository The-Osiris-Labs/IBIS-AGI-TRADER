# Troubleshooting

This guide provides troubleshooting steps for common issues with the IBIS AGI Trader.

## First Commands

```bash
./runtime_status.sh
./run_health_check.sh
systemctl status ibis-agent.service --no-pager -l
journalctl -u ibis-agent.service --since '30 minutes ago' --no-pager
```

## Issue: `overall: DEGRADED`

Typical causes:
- Temporary live/state parity mismatch
- Stale live order not yet reflected in state
- Exchange connectivity transient

Actions:
```bash
./run_health_check.sh
python3 tools/reconcile_state_db.py --apply
./runtime_status.sh
```

## Issue: Frequent Order Rejections

Check for:
- `LIMIT VALUE TOO LOW`
- `Price increment invalid`

Commands:
```bash
journalctl -u ibis-agent.service --since '30 minutes ago' --no-pager | rg 'LIMIT VALUE TOO LOW|Price increment invalid|ORDER SUCCESS'
```

If seen repeatedly, verify symbol rule loading and runtime code path in `ibis_true_agent.py`.

## Issue: Service Not Running

```bash
systemctl restart ibis-agent.service
systemctl status ibis-agent.service --no-pager -l
```

If restart fails, inspect journal and credentials wiring:
```bash
./tools/check_credentials_source.sh
journalctl -u ibis-agent.service -n 200 --no-pager
```

## Issue: Multiple Agent Processes

Health runner now suppresses duplicates, but manual verification:
```bash
ps -ef | rg 'ibis_true_agent.py' | rg -v rg
```

Expected: one process.

## Issue: Credentials Not Loaded by Service

```bash
./tools/check_credentials_source.sh
./tools/bootstrap_service_credentials.sh /root/projects/Dont\ enter\ unless\ solicited/AGI\ Trader/ibis/keys.env
systemctl daemon-reload
systemctl restart ibis-agent.service
```

## Issue: DB/State Drift

```bash
python3 tools/reconcile_state_db.py --apply
python3 tools/deep_state_audit.py --live-exchange
```

## Issue: `db_trades` Looks Too Low

`ibis_true_agent.py` execution metrics are derived from `data/trade_history.json`.
If `db_trades` is lower than `trade_history_records`, treat it as reporting drift unless other health checks fail.

Commands:
```bash
./runtime_status.sh
python3 tools/execution_econ_report.py
```

Optional DB backfill:
```bash
python3 tools/sync_trade_history_to_db.py --apply
```

## Verification Target

Healthy target after fixes:
- Service active
- Parity aligned (`state_positions == db_positions`)
- No repeating execution validation errors

## Initial Diagnosis

### 1. Check Service Status

```bash
systemctl status ibis-agent.service --no-pager -l
```

Look for:
- Service active (running) status
- Recent log messages
- Error codes or exceptions

### 2. Run Health Check

```bash
./run_health_check.sh
```

This will validate:
- Exchange connectivity
- Credentials
- Database accessibility
- State file validity
- System resources
- API connectivity

### 3. Check Runtime Status

```bash
./runtime_status.sh
```

### 4. Review Logs

```bash
# Main agent log
tail -200 agent.log

# System journal
journalctl -u ibis-agent.service --no-pager -l | tail -200

# Health check log
tail -50 health_check.log
```

## Common Issues & Solutions

### Issue 1: Agent Failed to Start

**Symptoms**: Service status shows "failed"

**Check**:
```bash
journalctl -u ibis-agent.service --no-pager -l
```

**Possible Causes & Fixes**:

1. **Missing Credentials**:
   ```bash
   ./tools/provision_kucoin_credentials.sh
   ```

2. **Invalid Configuration**:
   - Check `ibis/keys.env` for syntax errors
   - Verify API credentials are correct
   - Check `ibis/core/trading_constants.py` for valid values

3. **Dependency Issues**:
   ```bash
   pip3 install -r requirements.txt
   pip3 install -r ibis/requirements.txt
   ```

4. **File Permissions**:
   ```bash
   sudo chmod +x *.sh
   sudo chmod +x tools/*.sh
   sudo chmod 600 ibis/keys.env
   ```

### Issue 2: Exchange Connection Failed

**Symptoms**: Health check shows "Exchange connection: FAIL"

**Check**:
```bash
# Test internet connectivity
ping api.kucoin.com

# Check API endpoint
curl -s "https://api.kucoin.com/api/v1/market/symbols" | head -c 200
```

**Possible Causes & Fixes**:

1. **API Credentials Invalid**:
   - Verify API key, secret, and passphrase in `ibis/keys.env`
   - Check KuCoin API key permissions (must have "Trade" access)

2. **Network Issues**:
   - Check internet connectivity
   - Verify DNS resolution
   - Check firewall settings

3. **API Rate Limiting**:
   - Reduce scan frequency in `trading_constants.py`
   - Check KuCoin API rate limits

4. **Exchange Maintenance**:
   - Check KuCoin status page: https://status.kucoin.com/

### Issue 3: No Trades Being Executed

**Symptoms**: Agent running but no trades appear in history

**Check**:
```bash
# Check trade history
cat data/trade_history.json

# Check active positions
cat data/ibis_true_state.json
```

**Possible Causes & Fixes**:

1. **Market Conditions**:
   - Check if any symbols meet the scoring thresholds
   - Verify market data stream (`truth_stream.log`)

2. **Configuration Issues**:
   - Check `MIN_THRESHOLD` in `trading_constants.py`
   - Verify trading mode configuration in `config.json`

3. **Risk Constraints**:
   - Check `PORTFOLIO_HEAT_LIMIT` - portfolio may be fully allocated
   - Verify `MIN_CAPITAL_PER_TRADE` and available balance

4. **Symbol Rule Validation**:
   - Check if valid price increments are being calculated
   - Run liquidity trade audit: `python3 tools/liquidity_trade_audit.py`

### Issue 4: Invalid Price Increment Error

**Symptoms**: Errors like "Order price increment invalid"

**Root Cause**: Price calculation not respecting symbol's tick size

**Solution**: 
- Ensure `baseIncrement` and `priceIncrement` are correctly retrieved from KuCoin
- Verify price rounding logic in `ibis_true_agent.py`
- Run liquidity trade audit: `python3 tools/liquidity_trade_audit.py`

### Issue 5: Position Mismatch

**Symptoms**: Local state doesn't match exchange positions

**Check**:
```bash
# Reconcile state and exchange
python3 tools/reconcile_state_db.py

# Deep state audit
python3 tools/deep_state_audit.py

# Sync trade history
python3 tools/sync_trade_history_to_db.py --apply
```

**Solution**:
```bash
# Stop agent
sudo systemctl stop ibis-agent.service

# Reconcile
python3 tools/reconcile_state_db.py --force

# Start agent
sudo systemctl start ibis-agent.service
```

### Issue 6: High CPU Usage

**Symptoms**: Process uses >100% CPU

**Check**:
```bash
# Check process status
ps aux | grep ibis_true_agent

# Check for infinite loops in logs
grep -i "loop" agent.log
```

**Solution**:
1. Restart the agent
2. Check for recent code changes that might cause loops
3. Adjust scan interval or lookback period

### Issue 7: Memory Leak

**Symptoms**: Memory usage continuously increasing

**Check**:
```bash
# Monitor memory usage
ps aux --sort=-%mem | grep ibis

# Check garbage collection
grep -i "memory" agent.log
```

**Solution**:
1. Restart the agent
2. Check for large data structures not being garbage collected
3. Optimize market data processing

### Issue 8: Database Corruption

**Symptoms**: Errors accessing `ibis_v8.db`

**Check**:
```bash
# Try to repair SQLite database
sqlite3 data/ibis_v8.db "PRAGMA integrity_check;"
```

**Solution**:
1. Restore from backup
2. Recreate the database:
   ```bash
   sudo systemctl stop ibis-agent.service
   rm data/ibis_v8.db
   sudo systemctl start ibis-agent.service
   python3 tools/sync_trade_history_to_db.py --apply
   ```

### Issue 9: Timer Failures

**Symptoms**: Timers not running or failing

**Check**:
```bash
# List timer status
systemctl list-timers --all --no-pager | rg 'ibis-.*timer'

# Check specific timer log
journalctl -u ibis-healthcheck.timer --no-pager -l
```

**Solution**:
1. Restart the timer:
   ```bash
   sudo systemctl restart ibis-healthcheck.timer
   ```
2. If problem persists, re-enable:
   ```bash
   sudo systemctl disable ibis-healthcheck.timer
   sudo systemctl enable ibis-healthcheck.timer
   ```

### Issue 10: Paper Trading Not Working

**Symptoms**: Orders not appearing in paper trading mode

**Check**:
```bash
# Verify paper trading configuration
grep -i "paper" ibis/keys.env
```

**Solution**:
1. Ensure `PAPER_TRADING=true` in `ibis/keys.env`
2. Restart the agent
3. Check paper trading order history in `agent.log`

## Advanced Troubleshooting

### Running in Debug Mode

```bash
# Stop agent
sudo systemctl stop ibis-agent.service

# Edit keys.env
echo "DEBUG=true" >> ibis/keys.env
echo "VERBOSE=true" >> ibis/keys.env

# Start agent in debug mode
sudo systemctl start ibis-agent.service

# Check detailed logs
tail -f agent.log
```

### Manual Execution Test

```bash
# Run health check manually
./run_health_check.sh

# Test exchange connection
python3 -c "
from ibis.exchange.kucoin_client import KuCoinClient
client = KuCoinClient()
print('Connected:', client.is_connected())
print('Balance:', client.get_available_balance())
"

# Test market data retrieval
python3 -c "
from ibis.exchange.kucoin_client import KuCoinClient
client = KuCoinClient()
symbols = client.get_all_symbols()
print(f'Found {len(symbols)} symbols')
btc_price = client.get_current_price('BTC-USDT')
print(f'BTC Price: ${btc_price:.2f}')
"
```

### Performance Profiling

```bash
# Install profiling tools
pip3 install line_profiler memory_profiler

# Run agent with profiler
python3 -m cProfile -o profile.stats ibis_true_agent.py

# Analyze profile
python3 -m pstats profile.stats
```

## Collecting Debug Information

When reporting issues, include:

1. **System Information**:
   ```bash
   uname -a
   cat /etc/os-release
   python3 --version
   pip3 list | grep -E 'pandas|numpy|aiohttp'
   ```

2. **Agent Version**:
   ```bash
   git log --oneline | head -1
   ```

3. **Relevant Logs**:
   - Last 200 lines of `agent.log`
   - Last 50 lines of `health_check.log`
   - System journal for ibis-agent.service

4. **Configuration**:
   - `ibis/keys.env` (mask sensitive information)
   - `ibis/core/trading_constants.py`
   - `ibis/config.json`

5. **State Information**:
   - `data/ibis_true_state.json`
   - `data/trade_history.json` (last 10 trades)

## Emergency Recovery

### Complete System Reset

```bash
# Stop all services
sudo systemctl stop ibis-agent.service
sudo systemctl stop ibis-healthcheck.timer
sudo systemctl stop ibis-exec-integrity.timer
sudo systemctl stop ibis-hourly-kpi.timer
sudo systemctl stop ibis-log-retention.timer

# Create backup
cp -r data/ data_backup_$(date +%Y%m%d_%H%M%S)/

# Cleanup state
rm -f data/ibis_true_state.json
rm -f data/ibis_v8.db
rm -f agent.log health_check.log ibis_true_agent.log truth_stream.log

# Re-provision credentials
./tools/provision_kucoin_credentials.sh

# Start services
sudo systemctl start ibis-agent.service
sudo systemctl start ibis-healthcheck.timer
sudo systemctl start ibis-exec-integrity.timer
sudo systemctl start ibis-hourly-kpi.timer
sudo systemctl start ibis-log-retention.timer

# Verify
./run_health_check.sh
./runtime_status.sh
```

## Support

If you're unable to resolve an issue, please:

1. Check the project's issue tracker for similar problems
2. Gather all relevant debug information
3. Create a detailed issue report including:
   - Problem description
   - Steps to reproduce
   - Expected vs actual behavior
   - System information
   - Debug logs