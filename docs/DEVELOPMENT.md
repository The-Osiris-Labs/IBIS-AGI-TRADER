# Development Guide

## Repository Areas

- Core runtime: `ibis_true_agent.py`
- Core modules: `ibis/`
- Operations scripts: `tools/`, `run_*.sh`
- Service/timer units: `deploy/`
- Runtime data: `data/`

## Safe Workflow

1. Edit code.
2. Compile-check touched Python files.
3. Run local health checks.
4. Restart `ibis-agent.service` only when required.
5. Validate with runtime and journal evidence.

Example:

```bash
python3 -m py_compile ibis_true_agent.py tools/*.py
./run_health_check.sh
./runtime_status.sh
journalctl -u ibis-agent.service --since '10 minutes ago' --no-pager
```

## Runtime-Sensitive Rules

- The service executes `/root/projects/ibis_trader/ibis_true_agent.py`.
- In this environment, it resolves to this repository path; verify before editing in new environments.
- Avoid parallel agent processes.

## Common Development Tasks

Reconcile state/db:

```bash
python3 tools/reconcile_state_db.py --apply
```

Deep audit with live exchange checks:

```bash
python3 tools/deep_state_audit.py --live-exchange
```

Execution integrity snapshot:

```bash
python3 tools/execution_integrity_check.py --live-open-orders
```

## Documentation Discipline

After operational changes, update:
- `docs/OPERATIONS_24_7.md`
- `docs/TROUBLESHOOTING.md`
- `docs/CHANGES.md`

Keep docs aligned with actual service/runtime behavior.
