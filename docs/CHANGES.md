# Change Log

## 2026-02-17

### Comprehensive Documentation Update
- Complete rewrite of all documentation files
- Updated `README.md` with comprehensive project overview
- Enhanced `docs/ARCHITECTURE.md` with 5-tier architecture diagram
- Detailed `docs/CONFIG.md` with all configuration options
- Expanded `docs/OPERATIONS_24_7.md` with complete operations guide
- Comprehensive `docs/TROUBLESHOOTING.md` with all common issues
- Updated `docs/QUICKSTART.md` with step-by-step setup
- Enhanced `docs/DEVELOPMENT.md` with complete development guide

### Core Agent Fixes
1. **Unassigned Variable Error**: Fixed `agi_action` variable not defined for all score ranges in ibis_true_agent.py line 4558
2. **Price Rounding**: Added take profit and stop loss price rounding to valid price increments in ibis_true_agent.py:
   - Lines 4804-4805: Main execution path
   - Lines 5083-5087: Alternative execution path
3. **Decimal Precision**: Updated print statements from .4f to .8f to display sufficient decimal places for cryptocurrency prices
4. **Import Error**: Fixed missing `clear_kucoin_client_instance` import in ibis_true_agent.py line 22

### Recent Improvements (Previous 20 Commits)

1. **Reduce entry churn on spread rejects and auto-sync trade history** - Optimized entry logic
2. **Add retry backoff for live integrity snapshots** - Improved reliability
3. **Fix DB trade logging parity and add history sync utility** - Data consistency
4. **Harden ops observability and monitoring compatibility** - Enhanced monitoring
5. **Use realized daily metrics in dashboard summary and adaptive risk** - Risk optimization
6. **Align runtime status metrics with realized daily performance** - Metrics consistency
7. **Fix recycle guard math and separate synced PnL from daily runtime** - PnL calculation
8. **Tighten intel observability and scoring consistency** - Intelligence improvements
9. **Fix unified scoring pass-through for momentum and volume** - Scoring accuracy
10. **Harden momentum quality and pass-through scoring** - Momentum detection

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