"""
Structured logging configuration for Cultist Simulator AI Agent.
Uses structlog for JSON-formatted logging per constitutional requirement V.
"""

import logging
import sys
from pathlib import Path
from datetime import datetime
import structlog


# Log directory
LOG_DIR = Path(__file__).parent.parent.parent / "data" / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)


def configure_logging(log_level: str = "INFO", log_to_file: bool = True):
    """
    Configure structured logging with JSON output.

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_to_file: Whether to write logs to file

    Returns:
        Configured structlog logger
    """
    # Determine log file path with timestamp
    if log_to_file:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = LOG_DIR / f"agent_{timestamp}.jsonl"
    else:
        log_file = None

    # Configure standard library logging
    logging.basicConfig(
        format="%(message)s",
        level=getattr(logging, log_level.upper()),
        stream=sys.stdout,
    )

    # Processors for structlog
    processors = [
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer(),
    ]

    # Configure structlog
    structlog.configure(
        processors=processors,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

    # Get logger
    logger = structlog.get_logger()

    # Add file handler if requested
    if log_to_file and log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(getattr(logging, log_level.upper()))
        logging.root.addHandler(file_handler)
        logger.info("logging_initialized", log_file=str(log_file))

    return logger


def get_logger(name: str = None):
    """
    Get a logger instance.

    Args:
        name: Optional logger name (typically __name__)

    Returns:
        Structlog logger instance
    """
    if name:
        return structlog.get_logger(name)
    return structlog.get_logger()


if __name__ == "__main__":
    # Test logging configuration
    logger = configure_logging(log_level="DEBUG", log_to_file=True)
    logger.info("test_message", component="logging_config", status="success")
    logger.debug("debug_message", details={"key": "value"})
    logger.warning("warning_message", alert="test")
    print(f"\n✓ Logs written to: {LOG_DIR}")
