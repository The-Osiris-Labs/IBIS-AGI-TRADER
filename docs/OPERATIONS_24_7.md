# 24/7 Operations

## Runtime Topology

- **Service**: `ibis-agent.service`
- **Working directory**: `/root/projects/ibis_trader`
- **Active script**: `/root/projects/ibis_trader/ibis_true_agent.py`
- **Credential file**: `/root/projects/Dont enter unless solicited/AGI Trader/ibis/keys.env`

## Scheduled Jobs

- `ibis-healthcheck.timer` -> `ibis-healthcheck.service` (5 minutes) - Comprehensive health verification
- `ibis-exec-integrity.timer` -> `ibis-exec-integrity.service` (15 minutes) - Execution reconciliation
- `ibis-hourly-kpi.timer` -> `ibis-hourly-kpi.service` (hourly) - KPI reporting
- `ibis-log-retention.timer` -> `ibis-log-retention.service` (daily) - Log rotation

## Core Runbooks

### Health & Status

```bash
./runtime_status.sh
./run_health_check.sh
```

### Agent Lifecycle

```bash
systemctl restart ibis-agent.service
systemctl status ibis-agent.service --no-pager -l
```

### Timer Lifecycle

```bash
systemctl list-timers --all --no-pager | rg 'ibis-.*timer'
```

## Healthy State

- `service_active: active`
- `service_enabled: enabled`
- `state_positions == db_positions`
- `trade_history_records` increasing over time
- `overall: OK`

**Notes**: `db_trades` can lag `trade_history_records`; runtime execution reporting uses `data/trade_history.json`.

## Degraded State

Most common reasons:
- Live/state symbol parity mismatch
- Stale live orders not yet reflected in state
- Transient exchange DNS/rate-limit issues

**Immediate action**:
```bash
./run_health_check.sh
./runtime_status.sh
```

If still degraded, inspect:
```bash
journalctl -u ibis-agent.service --since '30 minutes ago' --no-pager
```

## System Overview

The IBIS AGI Trader is designed for continuous 24/7 operation using systemd services and timers. This document covers the operational aspects of maintaining a production deployment.

## Service Architecture

### Core Services

1. **ibis-agent.service** - Main trading process
   - Always-on operation
   - Handles market scanning, analysis, and execution
   - Manages position tracking and risk management
   - Auto-restarts on failure

2. **ibis-healthcheck.timer** - 5-minute health checks
   - Runs comprehensive system health verification
   - Checks exchange connectivity, credentials, database, and state
   - Logs results to `health_check.log`

3. **ibis-exec-integrity.timer** - 15-minute execution checks
   - Verifies trade execution integrity
   - Reconciles exchange positions with local state
   - Identifies and resolves discrepancies

4. **ibis-hourly-kpi.timer** - 1-hour KPI reporting
   - Generates performance metrics reports
   - Tracks profitability, win rate, risk metrics
   - Saves reports to `data/kpi_reports/`

5. **ibis-log-retention.timer** - 24-hour log rotation
   - Manages log file sizes and retention
   - Prevents disk space issues
   - Compresses old logs for archival

## Key Operational Commands

### Service Management

```bash
# Check agent status
systemctl status ibis-agent.service --no-pager -l

# Start/Stop/Restart
sudo systemctl start ibis-agent.service
sudo systemctl stop ibis-agent.service
sudo systemctl restart ibis-agent.service

# Enable/Disable on boot
sudo systemctl enable ibis-agent.service
sudo systemctl disable ibis-agent.service
```

### Timer Management

```bash
# List active timers
systemctl list-timers --all --no-pager | rg 'ibis-.*timer'

# Check timer status
systemctl status ibis-healthcheck.timer
systemctl status ibis-exec-integrity.timer
systemctl status ibis-hourly-kpi.timer
systemctl status ibis-log-retention.timer
```

### Runtime Status

```bash
# Real-time runtime status
./runtime_status.sh

# Comprehensive health check
./run_health_check.sh

# Execution integrity check
./run_execution_integrity_check.sh

# Hourly KPI report
./run_hourly_kpi_report.sh

# Market data snapshot
./run_truth_snapshot.sh
```

## Monitoring & Logging

### Log Files

| File | Purpose | Rotation |
|------|---------|----------|
| `agent.log` | Main agent activity log | Daily |
| `health_check.log` | Health check results | Daily |
| `ibis_true_agent.log` | Agent-specific log | Daily |
| `truth_stream.log` | Market data stream | Daily |
| `data/trade_history.json` | Complete trade history | Persistent |

### Journalctl Access

```bash
# Show agent journal
journalctl -u ibis-agent.service --no-pager -l

# Follow live log
journalctl -u ibis-agent.service -f

# Show log for specific time range
journalctl -u ibis-agent.service --since "2026-02-17 00:00:00" --until "2026-02-17 10:00:00"
```

## Performance Monitoring

### KPI Reports

Located in `data/kpi_reports/`:
- Daily performance summaries
- Win rate and profitability metrics
- Risk exposure and drawdown analysis
- Symbol-specific performance

### Runtime Metrics

```bash
# Current portfolio status
./runtime_status.sh

# Process resource usage
ps aux | grep ibis_true_agent

# System resource monitoring
htop
```

## Maintenance Procedures

### Trade History Reconciliation

```bash
# Sync trade history to database
python3 tools/sync_trade_history_to_db.py --apply

# Reconcile state and database
python3 tools/reconcile_state_db.py

# Deep state audit
python3 tools/deep_state_audit.py

# Liquidity trade audit
python3 tools/liquidity_trade_audit.py
```

### Configuration Updates

1. **Stop the agent**
2. Edit configuration file
3. Validate syntax
4. Restart the agent

```bash
sudo systemctl stop ibis-agent.service
# Edit configuration (e.g., ibis/core/trading_constants.py)
python3 -m py_compile ibis_true_agent.py
sudo systemctl start ibis-agent.service
./run_health_check.sh
```

### Software Updates

```bash
# Pull latest changes
git pull origin main

# Run tests
pytest tests/

# Stop and restart agent
sudo systemctl stop ibis-agent.service
python3 -m py_compile ibis_true_agent.py
sudo systemctl start ibis-agent.service

# Verify operation
./runtime_status.sh
./run_health_check.sh
```