# Quickstart

## Prerequisites

1. **System Requirements**:
   - Linux-based system (tested on Ubuntu 20.04+)
   - Python 3.8 or higher
   - Systemd service manager
   - Stable internet connection

2. **KuCoin Account**:
   - Create KuCoin account
   - Enable API access (read + trade permissions)
   - Create API key, secret, and passphrase

## Initial Setup

### 1. Provision Credentials

```bash
./tools/provision_kucoin_credentials.sh
```

This will:
- Create `ibis/keys.env` file
- Prompt for API credentials
- Validate KuCoin connection
- Set appropriate file permissions

### 2. Verify Credentials

```bash
./tools/check_credentials_source.sh
```

### 3. Install Dependencies

```bash
pip3 install -r requirements.txt
pip3 install -r ibis/requirements.txt
```

### 4. Enable Systemd Services

```bash
cd deploy/
sudo cp ibis-agent.service /etc/systemd/system/
sudo cp ibis-healthcheck.timer /etc/systemd/system/
sudo cp ibis-exec-integrity.timer /etc/systemd/system/
sudo cp ibis-hourly-kpi.timer /etc/systemd/system/
sudo cp ibis-log-retention.timer /etc/systemd/system/

sudo systemctl daemon-reload
sudo systemctl enable ibis-agent.service
sudo systemctl enable ibis-healthcheck.timer
sudo systemctl enable ibis-exec-integrity.timer
sudo systemctl enable ibis-hourly-kpi.timer
sudo systemctl enable ibis-log-retention.timer
```

### 5. Start the Agent

```bash
sudo systemctl start ibis-agent.service
```

## Validation Steps

### 1. Check Service Status

```bash
systemctl status ibis-agent.service --no-pager -l
```

### 2. Verify Runtime Status

```bash
./runtime_status.sh
```

### 3. Run Health Check

```bash
./run_health_check.sh
```

### 4. Check Timers

```bash
systemctl list-timers --all --no-pager | rg 'ibis-.*timer'
```

## Expected Output

### Runtime Status Example

```
IBIS True Agent - Runtime Status
================================

Service Status: active (running) since Mon 2026-02-17 10:30:00 UTC; 10min ago
PID: 12345
CPU Usage: 0.5%
Memory Usage: 150MB

Exchange Connection: OK
Balance: $10,000.00
Active Positions: 0
Total Trades: 0

Last Health Check: 2026-02-17 10:35:00 UTC (OK)
Last KPI Report: 2026-02-17 10:00:00 UTC
```

### Health Check Example

```
IBIS True Agent - Health Check
===============================

✓ Exchange connection: OK
✓ Credentials valid: OK
✓ Database accessible: OK
✓ State file valid: OK
✓ No duplicate processes: OK
✓ System resources: OK
✓ API connectivity: OK

All health checks passed!
```

## Configuration Verification

### Check Trading Constants

```bash
cat ibis/core/trading_constants.py
```

### Check Dynamic Configuration

```bash
cat ibis/config.json
```

## Troubleshooting Initial Setup

### Common Issues

1. **Permission Denied**:
   ```bash
   sudo chmod +x ./tools/*.sh
   sudo chmod +x *.sh
   ```

2. **Dependency Installation Failures**:
   ```bash
   pip3 install --upgrade pip
   pip3 install -r requirements.txt --no-cache-dir
   ```

3. **Systemd Service Errors**:
   ```bash
   journalctl -u ibis-agent.service --no-pager -l
   ```

4. **KuCoin API Errors**:
   - Verify API key permissions (must have "Trade" permission)
   - Check API key expiration
   - Verify IP whitelisting if enabled

## Next Steps

Once the agent is running successfully:

1. Monitor the agent log: `tail -f agent.log`
2. Check trade history: `cat data/trade_history.json`
3. Review KPI reports: `cat data/kpi_reports/`
4. For paper trading, set `PAPER_TRADING=true` in ibis/keys.env

## Production Deployment Notes

1. **Security**:
   - Restrict access to credentials file: `chmod 600 ibis/keys.env`
   - Consider using a dedicated API key with limited permissions
   - Enable two-factor authentication on your KuCoin account

2. **Monitoring**:
   - Set up log rotation
   - Configure alerting for critical errors
   - Regularly review health check reports

3. **Updates**:
   - Test changes in sandbox environment first
   - Use version control for configuration changes
   - Maintain backup of critical data files