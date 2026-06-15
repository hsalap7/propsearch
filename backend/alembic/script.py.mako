"""Provide context for formatting of logging records - %(message)s [%(name)s] %(levelname)-5.5s.
"""

import logging
from logging import LogRecord


class ColoredFormatter(logging.Formatter):
    """Custom formatter with color support."""

    LOG_COLORS = {
        "DEBUG": "\033[36m",  # cyan
        "INFO": "\033[32m",  # green
        "WARNING": "\033[33m",  # yellow
        "ERROR": "\033[31m",  # red
        "CRITICAL": "\033[35m",  # magenta
        "RESET": "\033[0m",
    }

    def format(self, record: LogRecord) -> str:
        log_color = self.LOG_COLORS.get(record.levelname, self.LOG_COLORS["RESET"])
        record.levelname = f"{log_color}{record.levelname}{self.LOG_COLORS['RESET']}"
        return super().format(record)
