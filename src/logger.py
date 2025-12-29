"""
Logging configuration for Equity Research Report Generator.
"""

import logging
import os
import sys
from pathlib import Path
from typing import Optional

from colorama import Fore, Style, init

# Initialize colorama for cross-platform colored output
init(autoreset=True)


class ColoredFormatter(logging.Formatter):
    """Custom formatter with colors for console output."""

    COLORS = {
        "DEBUG": Fore.CYAN,
        "INFO": Fore.GREEN,
        "WARNING": Fore.YELLOW,
        "ERROR": Fore.RED,
        "CRITICAL": Fore.RED + Style.BRIGHT,
    }

    def format(self, record):
        """Format log record with colors."""
        log_color = self.COLORS.get(record.levelname, "")
        record.levelname = f"{log_color}{record.levelname}{Style.RESET_ALL}"
        record.msg = f"{log_color}{record.msg}{Style.RESET_ALL}"
        return super().format(record)


def setup_logger(
    name: str = "geyser",
    level: str = "INFO",
    log_file: Optional[str] = None,
    log_to_console: bool = True,
) -> logging.Logger:
    """
    Set up logger with file and console handlers.

    Args:
        name: Logger name
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Path to log file (optional)
        log_to_console: Whether to log to console

    Returns:
        Configured logger
    """
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper()))

    # Remove existing handlers
    logger.handlers = []

    # Create formatters
    file_formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
    )
    console_formatter = ColoredFormatter(
        "%(levelname)s - %(message)s"
    )

    # Add file handler if log_file specified
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)

    # Add console handler if enabled
    if log_to_console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(getattr(logging, level.upper()))
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)

    return logger


def get_logger(name: str = "geyser") -> logging.Logger:
    """
    Get logger instance.

    Args:
        name: Logger name

    Returns:
        Logger instance
    """
    return logging.getLogger(name)


# Initialize default logger
_default_logger: Optional[logging.Logger] = None


def init_logging(level: str = "INFO", log_file: Optional[str] = None, log_to_console: bool = True):
    """
    Initialize application-wide logging.

    Args:
        level: Log level
        log_file: Path to log file
        log_to_console: Whether to log to console
    """
    global _default_logger
    _default_logger = setup_logger("geyser", level, log_file, log_to_console)
