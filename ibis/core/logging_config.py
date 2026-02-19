"""
Centralized logging configuration for the IBIS project.

This module provides a single function to configure logging with best practices,
including log rotation, file/console handlers, and structured logging support.
"""

import logging
import logging.config
import os
from typing import Optional
import json
from datetime import datetime
from logging.handlers import RotatingFileHandler


class JSONFormatter(logging.Formatter):
    """JSON structured logging formatter."""

    def format(self, record: logging.LogRecord) -> str:
        log_record = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "name": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        if record.exc_info:
            log_record["exc_info"] = self.formatException(record.exc_info)

        if record.stack_info:
            log_record["stack_info"] = self.formatStack(record.stack_info)

        return json.dumps(log_record)


def configure_logging(
    log_level: str = "INFO",
    log_dir: str = "logs",
    json_logging: bool = False,
    max_bytes: int = 10 * 1024 * 1024,  # 10MB
    backup_count: int = 5,
) -> None:
    """
    Configure logging with best practices.

    Args:
        log_level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_dir: Directory to store log files
        json_logging: Whether to use JSON structured logging
        max_bytes: Maximum size of each log file before rotation
        backup_count: Number of backup log files to keep

    Environment variables:
        IBIS_LOG_LEVEL: Overrides log_level parameter
        IBIS_LOG_DIR: Overrides log_dir parameter
        IBIS_JSON_LOGGING: Overrides json_logging parameter (true/false)
    """
    # Read environment variables for configuration
    log_level = os.environ.get("IBIS_LOG_LEVEL", log_level).upper()
    log_dir = os.environ.get("IBIS_LOG_DIR", log_dir)
    json_logging = os.environ.get("IBIS_JSON_LOGGING", str(json_logging)).lower() == "true"

    # Create log directory if it doesn't exist
    os.makedirs(log_dir, exist_ok=True)

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    # Clear existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # File handler with rotation
    log_file = os.path.join(log_dir, "ibis.log")
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=max_bytes,
        backupCount=backup_count,
        encoding="utf-8",
    )

    # Console handler
    console_handler = logging.StreamHandler()

    # Choose formatter based on logging type
    if json_logging:
        file_formatter = JSONFormatter()
        console_formatter = JSONFormatter()
    else:
        file_formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s - %(module)s:%(funcName)s:%(lineno)d"
        )
        console_formatter = logging.Formatter("%(levelname)s - %(message)s")

    file_handler.setFormatter(file_formatter)
    console_handler.setFormatter(console_formatter)

    # Add handlers to root logger
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)

    # Configure log levels for external libraries
    external_loggers = {
        "aiohttp": "WARNING",
        "asyncio": "WARNING",
        "websockets": "WARNING",
        "urllib3": "WARNING",
    }

    for logger_name, level in external_loggers.items():
        logger = logging.getLogger(logger_name)
        logger.setLevel(level)
        # Prevent external loggers from propagating to root logger
        logger.propagate = False
        # Add handlers to external loggers
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

    # Log configuration details
    root_logger.info("Logging configured successfully")
    root_logger.debug(
        "Logging configuration: log_level=%s, log_dir=%s, json_logging=%s",
        log_level,
        log_dir,
        json_logging,
    )


# Convenience function to get a logger
def get_logger(name: Optional[str] = None) -> logging.Logger:
    """
    Get a logger with the specified name.

    Args:
        name: Logger name (defaults to __name__ if None)

    Returns:
        Configured logger instance
    """
    return logging.getLogger(name)
