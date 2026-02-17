# IBIS AGI Trader - Comprehensive Documentation

## Project Overview

IBIS AGI Trader is a **production-grade, autonomous cryptocurrency trading system** designed for 24/7 operation on the KuCoin exchange. It combines sophisticated market analysis, AI-driven intelligence, and robust risk management to create a self-adapting trading solution.

**Core Philosophy:**
- Truly autonomous with no hardcoded trading symbols
- Real-time market discovery and dynamic intelligence analysis  
- Self-adapting to ALL market conditions
- Centralized configuration and threshold management
- Production-proven reliability with comprehensive monitoring

## Current Runtime Model

- **Supervisor**: `systemd` (`ibis-agent.service`)
- **Main Loop**: `ibis_true_agent.py`
- **State Stores**:
  - `data/ibis_true_state.json`
  - `data/ibis_v8.db` (SQLite database)
- **Operational Checks**:
  - `./runtime_status.sh` - Real-time runtime status
  - `./run_health_check.sh` - Comprehensive health verification

## Fast Start

1. **Provision Credentials**:
   ```bash
   ./tools/provision_kucoin_credentials.sh
   ```

2. **Confirm Service is Active**:
   ```bash
   systemctl status ibis-agent.service --no-pager -l
   ```

3. **Validate Runtime**:
   ```bash
   ./runtime_status.sh
   ```

## 24/7 Services and Timers

- `ibis-agent.service` - Always-on trading process
- `ibis-healthcheck.timer` - 5-minute health checks
- `ibis-exec-integrity.timer` - 15-minute execution integrity checks
- `ibis-hourly-kpi.timer` - 1-hour KPI reporting
- `ibis-log-retention.timer` - 24-hour log rotation

## Important Constraints

- **Minimum Trade Notional**: $11 enforced
- **Duplicate Order Prevention**: No duplicate buy/order for the same symbol
- **Strategy Modification**: Runtime docs and tooling do not intentionally modify strategy definition files

## Documentation Index

- `docs/QUICKSTART.md`: Bootstrap and first validation
- `docs/OPERATIONS_24_7.md`: Systemd/timer operations and health model
- `docs/TROUBLESHOOTING.md`: Fault isolation and recovery actions
- `docs/ARCHITECTURE.md`: Runtime architecture and data flow
- `docs/CONFIG.md`: Active configuration surfaces
- `docs/DEVELOPMENT.md`: Safe development workflow
- `docs/CHANGES.md`: Curated change log
- `MANIFEST.md`: Project manifest

## Runtime-Truth Commands

```bash
./runtime_status.sh
./run_health_check.sh
systemctl status ibis-agent.service --no-pager -l
systemctl list-timers --all --no-pager | rg 'ibis-.*timer'
```

**History Reconciliation:**
```bash
python3 tools/sync_trade_history_to_db.py --apply
```

## Source of Truth Rule

When docs and runtime differ, runtime output is authoritative. Update docs immediately after validated runtime changes.