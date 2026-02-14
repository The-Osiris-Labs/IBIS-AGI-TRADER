# Change Log

## 2026-02-14

### Operations and reliability
- Added 24/7 service/timer operational stack:
  - `ibis-healthcheck.timer`
  - `ibis-exec-integrity.timer`
  - `ibis-hourly-kpi.timer`
  - `ibis-log-retention.timer`
- Added runtime observability and integrity scripts:
  - `runtime_status.sh`
  - `run_health_check.sh`
  - `tools/deep_state_audit.py`
  - `tools/execution_integrity_check.py`
  - `tools/hourly_kpi_report.py`
  - `tools/truth_snapshot.py`

### Reconciliation/self-heal
- Improved close reconciliation behavior for insufficient-balance edge cases.
- Added startup reconciliation path correction.
- Added periodic state/db reconciliation and drift checks.

### Execution bottleneck fixes
- Preserved `priceIncrement` during symbol rule refresh to avoid invalid tick submissions.
- Replaced fragile increment rounding with Decimal-safe rounding helpers.
- Added minimum-notional quantity adjustment before limit submit to enforce `$11` at submitted price.
- Improved AGI confidence log formatting for correct percentage display.

### Documentation cleanup
- Replaced stale docs and removed outdated operational guidance.
- Standardized docs on systemd-first runtime model and current tooling.
