# IBIS Examples

Practical examples of using and extending IBIS.

## Contents

- **basic_usage/** - Getting started with IBIS
- **configuration/** - Configuration examples
- **monitoring/** - Monitoring and analysis scripts
- **integration/** - Integration with external systems
- **strategies/** - Custom strategy examples (read-only, don't modify core)

## Quick Start Examples

### Run IBIS

```bash
# Paper trading (test mode)
PAPER_TRADING=true python3 ../ibis_true_agent.py

# Production trading
python3 ../ibis_true_agent.py

# Single scan test
python3 ../ibis_true_agent.py --scan-once

# With debug output
DEBUG=true VERBOSE=true python3 ../ibis_true_agent.py
```

### Monitor IBIS

```bash
# View current state
python3 basic_usage/view_state.py

# Check portfolio
python3 monitoring/portfolio_status.py

# View learning progress
python3 monitoring/learning_progress.py
```

### Analyze Performance

```bash
# Trade statistics
python3 monitoring/trade_stats.py

# Strategy effectiveness
python3 monitoring/strategy_performance.py

# Market regime analysis
python3 monitoring/regime_analysis.py
```

---

See individual example files for usage and documentation.
