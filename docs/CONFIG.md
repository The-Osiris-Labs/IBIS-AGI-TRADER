# Configuration Reference

This file documents active runtime configuration surfaces.

## 1) Credentials

File: `ibis/keys.env`

Required:
- `KUCOIN_API_KEY`
- `KUCOIN_API_SECRET`
- `KUCOIN_API_PASSPHRASE`

Optional:
- `PAPER_TRADING`
- `KUCOIN_IS_SANDBOX`
- `DEBUG`
- `VERBOSE`

Validate wiring:

```bash
./tools/check_credentials_source.sh
```

## 2) Core Trading Constants

File: `ibis/core/trading_constants.py`

Primary groups:
- `TRADING.EXCHANGE`
- `TRADING.CRITICAL`
- `TRADING.SCORE`
- `TRADING.POSITION`
- `TRADING.SCAN`
- `TRADING.RISK`
- `TRADING.EXECUTION`

Current key runtime values include:
- `TRADING.POSITION.MIN_CAPITAL_PER_TRADE = 11.0`
- `TRADING.EXECUTION.MIN_TRADE_VALUE = 11.0`

Runtime reads these on process start; restart service after edits.

## 3) Service Configuration

Systemd unit:
- `/etc/systemd/system/ibis-agent.service`

Credential drop-in:
- `/etc/systemd/system/ibis-agent.service.d/credentials.conf`

After service config edits:

```bash
systemctl daemon-reload
systemctl restart ibis-agent.service
```

## 4) Operational Script Configuration

Managed jobs are in `deploy/` and call:
- `run_health_check.sh`
- `run_execution_integrity_check.sh`
- `run_hourly_kpi_report.sh`
- `run_truth_snapshot.sh`

## 5) What Not to Configure Blindly

Do not alter strategy/risk fields without explicit intent and validation.
Use staged validation:

```bash
python3 -m py_compile ibis_true_agent.py
./run_health_check.sh
./runtime_status.sh
```
