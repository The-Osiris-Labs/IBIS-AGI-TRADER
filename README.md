# IBIS AGI Trader

Production runtime for the IBIS autonomous KuCoin spot agent.

## Current Runtime Model

- Supervisor: `systemd` (`ibis-agent.service`)
- Main loop: `ibis_true_agent.py`
- State stores:
  - `data/ibis_true_state.json`
  - `data/ibis_v8.db`
- Operational checks:
  - `./runtime_status.sh`
  - `./run_health_check.sh`

## Fast Start

1. Provision credentials:

```bash
./tools/provision_kucoin_credentials.sh
```

2. Confirm service is active:

```bash
systemctl status ibis-agent.service --no-pager -l
```

3. Validate runtime:

```bash
./runtime_status.sh
```

## 24/7 Services and Timers

- `ibis-agent.service` (always-on trading process)
- `ibis-healthcheck.timer` (5 min)
- `ibis-exec-integrity.timer` (15 min)
- `ibis-hourly-kpi.timer` (1 hour)
- `ibis-log-retention.timer` (24 hours)

## Important Constraints

- Minimum trade notional: `$11` enforced.
- No duplicate buy/order for the same symbol.
- Runtime docs and tooling do not intentionally modify strategy definition files.

## Documentation

- `docs/README.md`
- `docs/QUICKSTART.md`
- `docs/OPERATIONS_24_7.md`
- `docs/TROUBLESHOOTING.md`
- `docs/ARCHITECTURE.md`
- `docs/CONFIG.md`
- `docs/DEVELOPMENT.md`
- `docs/CHANGES.md`
- `MANIFEST.md`
