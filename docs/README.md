# Documentation Index

## Core

- `docs/QUICKSTART.md`: bootstrap and first validation
- `docs/OPERATIONS_24_7.md`: systemd/timer operations and health model
- `docs/TROUBLESHOOTING.md`: fault isolation and recovery actions
- `docs/ARCHITECTURE.md`: runtime architecture and data flow
- `docs/CONFIG.md`: active configuration surfaces
- `docs/DEVELOPMENT.md`: safe development workflow
- `docs/CHANGES.md`: curated change log

## Runtime-Truth Commands

```bash
./runtime_status.sh
./run_health_check.sh
systemctl status ibis-agent.service --no-pager -l
systemctl list-timers --all --no-pager | rg 'ibis-.*timer'
```

## Source of Truth Rule

When docs and runtime differ, runtime output is authoritative. Update docs immediately after validated runtime changes.
