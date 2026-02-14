# Architecture

## Runtime Layers

1. Exchange access
- `ibis/exchange/kucoin_client.py`
- market data, balances, orders, fills

2. Intelligence and scoring
- `ibis_true_agent.py` market scan path
- `ibis/core/unified_scoring.py`
- `ibis/intelligence/enhanced_sniping.py`
- `ibis/brain/agi_brain.py`

3. Execution
- `ibis_true_agent.py` order decision and placement
- symbol rule normalization (`baseIncrement`, `priceIncrement`)
- minimum notional enforcement (`$11`)
- duplicate-order prevention via state buy-order tracking

4. State and reconciliation
- state JSON: `data/ibis_true_state.json`
- DB: `data/ibis_v8.db`
- parity/recovery tooling:
  - `tools/reconcile_state_db.py`
  - `tools/deep_state_audit.py`
  - `tools/execution_integrity_check.py`

5. Operations/watchdog
- systemd service and timers under `deploy/`
- health and KPI runners:
  - `run_health_check.sh`
  - `run_execution_integrity_check.sh`
  - `run_hourly_kpi_report.sh`
  - `run_truth_snapshot.sh`

## Live Data Paths

- Journal: `journalctl -u ibis-agent.service`
- Runtime status: `./runtime_status.sh`
- Health check log: `health_check.log`
- Truth stream: `data/truth_stream.log`

## Reliability Model

- service auto-restarts by systemd
- periodic reconciliations correct drift between state/db/live exchange
- duplicate process suppression in health runner
- lock files prevent overlapping maintenance scripts

## Known Failure Domains

- exchange DNS/rate limiting
- symbol rule drift affecting valid tick/lot increments
- notional constraints near minimum trade threshold

The current execution path includes safeguards for increment-safe rounding and minimum-notional adjustment before submit.
