# IBIS 24/7 Operations

## Runtime authority
- Primary supervisor: `ibis-agent.service` (systemd)
- Do not run parallel supervisors when systemd is active.
- Canonical runtime check: `./runtime_status.sh`

## Health commands
- Quick runtime summary:
  - `./runtime_status.sh`
- Health check (scheduled/manual):
  - `./run_health_check.sh`
- Deep state/db audit:
  - `./tools/deep_state_audit.py`

## What "healthy" looks like
- `service_active: active`
- `service_enabled: enabled`
- `agent_pid` present
- `state_positions == db_positions`
- `overall: OK` in `runtime_status.sh`

## Degraded states
- `overall: DEGRADED` currently indicates at least one non-fatal risk, usually:
  - credential restart survivability not verified
  - deep audit warnings

## Credential survivability
- Verify source:
  - `./tools/check_credentials_source.sh`
- Configure systemd credential source from env file:
  - `./tools/bootstrap_service_credentials.sh /path/to/keys.env`
- The bootstrap script writes a systemd drop-in and reloads daemon config.
- Restart is manual and deliberate:
  - `sudo systemctl restart ibis-agent.service`

## Data consistency model
- Agent state file (`data/ibis_true_state.json`) is written atomically.
- Memory file (`data/ibis_true_memory.json`) is written atomically.
- DB is synchronized periodically from in-memory state in agent runtime.
- DB recovery and DB sync are lock-coordinated via `data/ibis_db.lock`.

## Non-strategy guarantee
- Operational tooling and integrity checks must not alter:
  - TP/SL values
  - risk/reward ratios
  - strategy decision logic
