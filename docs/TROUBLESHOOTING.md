# Troubleshooting

## First Commands

```bash
./runtime_status.sh
./run_health_check.sh
systemctl status ibis-agent.service --no-pager -l
journalctl -u ibis-agent.service --since '30 minutes ago' --no-pager
```

## Issue: `overall: DEGRADED`

Typical causes:
- temporary live/state parity mismatch
- stale live order not yet reflected in state
- exchange connectivity transient

Actions:

```bash
./run_health_check.sh
python3 tools/reconcile_state_db.py --apply
./runtime_status.sh
```

## Issue: Frequent order rejections

Check for:
- `LIMIT VALUE TOO LOW`
- `Price increment invalid`

Commands:

```bash
journalctl -u ibis-agent.service --since '30 minutes ago' --no-pager | rg 'LIMIT VALUE TOO LOW|Price increment invalid|ORDER SUCCESS'
```

If seen repeatedly, verify symbol rule loading and runtime code path in `ibis_true_agent.py`.

## Issue: Service not running

```bash
systemctl restart ibis-agent.service
systemctl status ibis-agent.service --no-pager -l
```

If restart fails, inspect journal and credentials wiring:

```bash
./tools/check_credentials_source.sh
journalctl -u ibis-agent.service -n 200 --no-pager
```

## Issue: Multiple agent processes

Health runner now suppresses duplicates, but manual verification:

```bash
ps -ef | rg 'ibis_true_agent.py' | rg -v rg
```

Expected: one process.

## Issue: Credentials not loaded by service

```bash
./tools/check_credentials_source.sh
./tools/bootstrap_service_credentials.sh /root/projects/Dont\ enter\ unless\ solicited/AGI\ Trader/ibis/keys.env
systemctl daemon-reload
systemctl restart ibis-agent.service
```

## Issue: DB/state drift

```bash
python3 tools/reconcile_state_db.py --apply
python3 tools/deep_state_audit.py --live-exchange
```

## Issue: `db_trades` looks too low

`ibis_true_agent.py` execution metrics are derived from `data/trade_history.json`.
If `db_trades` is lower than `trade_history_records`, treat it as reporting drift unless other health checks fail.

Commands:

```bash
./runtime_status.sh
python3 tools/execution_econ_report.py
```

## Verification Target

Healthy target after fixes:
- service active
- parity aligned (`state_positions == db_positions`)
- no repeating execution validation errors
