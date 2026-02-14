# 24/7 Operations

## Runtime Topology

- Service: `ibis-agent.service`
- Working directory: `/root/projects/ibis_trader`
- Active script: `/root/projects/ibis_trader/ibis_true_agent.py`
- Credential file: `/root/projects/Dont enter unless solicited/AGI Trader/ibis/keys.env`

## Scheduled Jobs

- `ibis-healthcheck.timer` -> `ibis-healthcheck.service` (5m)
- `ibis-exec-integrity.timer` -> `ibis-exec-integrity.service` (15m)
- `ibis-hourly-kpi.timer` -> `ibis-hourly-kpi.service` (hourly)
- `ibis-log-retention.timer` -> `ibis-log-retention.service` (daily)

## Core Runbooks

Health:

```bash
./runtime_status.sh
./run_health_check.sh
```

Agent lifecycle:

```bash
systemctl restart ibis-agent.service
systemctl status ibis-agent.service --no-pager -l
```

Timer lifecycle:

```bash
systemctl list-timers --all --no-pager | rg 'ibis-.*timer'
```

## Healthy State

- `service_active: active`
- `service_enabled: enabled`
- `state_positions == db_positions`
- `overall: OK`

## Degraded State

Most common reasons:
- live/state symbol parity mismatch
- stale live orders not yet reflected in state
- transient exchange DNS/rate-limit issues

Immediate action:

```bash
./run_health_check.sh
./runtime_status.sh
```

If still degraded, inspect:

```bash
journalctl -u ibis-agent.service --since '30 minutes ago' --no-pager
```
