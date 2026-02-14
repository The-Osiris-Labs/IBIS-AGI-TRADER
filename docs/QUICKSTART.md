# Quickstart

## 1) Credentials

```bash
./tools/provision_kucoin_credentials.sh
```

This writes `ibis/keys.env` with mode `600` and can restart `ibis-agent.service`.

## 2) Service Check

```bash
systemctl status ibis-agent.service --no-pager -l
systemctl is-active ibis-agent.service
systemctl is-enabled ibis-agent.service
```

## 3) Runtime Validation

```bash
./runtime_status.sh
./run_health_check.sh
```

Expected target: `overall: OK` in `runtime_status.sh`.

## 4) Logs

```bash
journalctl -u ibis-agent.service -f
```

## 5) Timer Validation

```bash
systemctl list-timers --all --no-pager | rg 'ibis-(healthcheck|exec-integrity|hourly-kpi|log-retention)\.timer'
```

## Notes

- Primary supervisor is systemd. Avoid launching parallel agent instances.
- Use `tools/bootstrap_service_credentials.sh` only when changing credential source wiring.
