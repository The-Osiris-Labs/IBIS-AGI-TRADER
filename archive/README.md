# Archive - Development History

This directory contains historical development scripts and experiments used during IBIS development.

## Directory Structure

- **analysis/** - Data analysis scripts exploring trading patterns and metrics
- **testing/** - Experimental test configurations and validation scripts
- **debug/** - Debugging utilities and diagnostic tools
- **experiments/** - Experimental strategies and optimization attempts

## Note

These files represent the evolution of IBIS. The production system is defined by:
- `ibis_true_agent.py` - Main agent
- `ibis/` - Core package
- `tests/` - Current test suite

Archived scripts are kept for reference and historical understanding of development.

## Reactivating Old Code

If you need to run any archived script:
```bash
python3 archive/analysis/script_name.py
python3 archive/debug/diagnostic_script.py
```

Ensure you understand the script's purpose before running, as some may expect older state formats.
