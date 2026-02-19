# IBIS AGI Trader - Comprehensive Documentation

## Project Overview

IBIS AGI Trader is a **production-grade, autonomous cryptocurrency trading system** designed for 24/7 operation on the KuCoin exchange. It combines sophisticated market analysis, AI-driven intelligence, and robust risk management to create a self-adapting trading solution.

**Core Philosophy:**
- Truly autonomous with no hardcoded trading symbols
- Real-time market discovery and dynamic intelligence analysis  
- Self-adapting to ALL market conditions
- Centralized configuration and threshold management
- Production-proven reliability with comprehensive monitoring

## Current Runtime Model

- **Supervisor**: `systemd` (`ibis-agent.service`)
- **Main Loop**: `ibis_true_agent.py`
- **State Stores**:
  - `data/ibis_true_state.json`
  - `data/ibis_v8.db` (SQLite database)
- **Operational Checks**:
  - `./runtime_status.sh` - Real-time runtime status
  - `./run_health_check.sh` - Comprehensive health verification

## Fast Start

1. **Provision Credentials**:
   ```bash
   ./tools/provision_kucoin_credentials.sh
   ```

2. **Confirm Service is Active**:
   ```bash
   systemctl status ibis-agent.service --no-pager -l
   ```

3. **Validate Runtime**:
   ```bash
   ./runtime_status.sh
   ```

## 24/7 Services and Timers

- `ibis-agent.service` - Always-on trading process
- `ibis-healthcheck.timer` - 5-minute health checks
- `ibis-exec-integrity.timer` - 15-minute execution integrity checks
- `ibis-hourly-kpi.timer` - 1-hour KPI reporting
- `ibis-log-retention.timer` - 24-hour log rotation

## Important Constraints

- **Minimum Trade Notional**: $11 enforced
- **Duplicate Order Prevention**: No duplicate buy/order for the same symbol
- **Strategy Modification**: Runtime docs and tooling do not intentionally modify strategy definition files

## Logging System

The IBIS AGI Trader includes a sophisticated centralized logging system designed for production-grade reliability, structured data capture, and efficient log management.

### Architecture

The logging system is implemented in `ibis/core/logging_config.py` and provides:
- Centralized configuration with environment variable support
- File and console logging with log rotation
- Structured JSON logging for machine readability
- External library log level management
- Automatic log directory creation

### Configuration

#### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `IBIS_LOG_LEVEL` | Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL) | INFO |
| `IBIS_LOG_DIR` | Directory to store log files | logs/ |
| `IBIS_JSON_LOGGING` | Enable structured JSON logging (true/false) | false |

#### Programmatic Configuration

```python
from ibis.core.logging_config import configure_logging

# Basic configuration (uses defaults)
configure_logging()

# Custom configuration
configure_logging(
    log_level="DEBUG",
    log_dir="/var/log/ibis",
    json_logging=True,
    max_bytes=50*1024*1024,  # 50MB per file
    backup_count=10  # Keep 10 backup files
)
```

### Using the Logger

#### In Modules

```python
from ibis.core.logging_config import get_logger

# Get a logger for the current module
logger = get_logger(__name__)

# Log messages at different levels
logger.debug("Debug message - detailed information for debugging")
logger.info("Info message - general operational information")
logger.warning("Warning message - potential problem")
logger.error("Error message - error occurred")
logger.critical("Critical message - critical error, system may fail")

# Log exceptions
try:
    raise ValueError("Something went wrong")
except Exception as e:
    logger.error("An error occurred", exc_info=True)
```

### Log File Management

#### Log Rotation

The system automatically handles log rotation with the following defaults:
- **File Size Limit**: 10MB per log file
- **Backup Count**: 5 rotated log files
- **Log File Path**: logs/ibis.log

Rotated files are named: `ibis.log.1`, `ibis.log.2`, etc.

#### Log Directory Structure

```
logs/
├── ibis.log          # Current active log file
├── ibis.log.1        # Most recent rotated log
├── ibis.log.2        # Next rotated log
└── ...
```

### Structured JSON Logging

When enabled (`IBIS_JSON_LOGGING=true`), each log entry is written as JSON:

```json
{
  "timestamp": "2024-02-18T10:30:00.123456",
  "level": "INFO",
  "name": "ibis.trader",
  "message": "Trading session started",
  "module": "trader",
  "function": "start_session",
  "line": 42
}
```

#### JSON Log Fields

| Field | Description |
|-------|-------------|
| `timestamp` | ISO-8601 timestamp with microseconds (UTC) |
| `level` | Log level (DEBUG/INFO/WARNING/ERROR/CRITICAL) |
| `name` | Logger name |
| `message` | Log message |
| `module` | Source module name |
| `function` | Source function name |
| `line` | Source line number |
| `exc_info` | Exception information (if exception occurred) |
| `stack_info` | Stack trace (if stack_info=True) |

### Benefits of the New System

1. **Centralized Configuration**: Single source of truth for all logging settings
2. **Environment Variable Support**: Easy configuration without code changes
3. **Structured Logging**: JSON format for easier parsing and analysis
4. **Automatic Rotation**: Prevents log files from growing indefinitely
5. **Console and File Output**: Dual logging for debugging and persistent storage
6. **External Library Control**: Manages log levels from third-party libraries
7. **Production-Grade Reliability**: Designed for 24/7 operation
8. **Scalability**: Handles high-volume logging with efficient file management

### Documentation Index

- `docs/QUICKSTART.md`: Bootstrap and first validation
- `docs/OPERATIONS_24_7.md`: Systemd/timer operations and health model
- `docs/TROUBLESHOOTING.md`: Fault isolation and recovery actions
- `docs/ARCHITECTURE.md`: Runtime architecture and data flow
- `docs/CONFIG.md`: Active configuration surfaces
- `docs/DEVELOPMENT.md`: Safe development workflow
- `docs/CHANGES.md`: Curated change log
- `MANIFEST.md`: Project manifest

## Runtime-Truth Commands

```bash
./runtime_status.sh
./run_health_check.sh
systemctl status ibis-agent.service --no-pager -l
systemctl list-timers --all --no-pager | rg 'ibis-.*timer'
```

**History Reconciliation:**
```bash
python3 tools/sync_trade_history_to_db.py --apply
```

## Source of Truth Rule

When docs and runtime differ, runtime output is authoritative. Update docs immediately after validated runtime changes.