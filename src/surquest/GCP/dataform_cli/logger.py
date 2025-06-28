import logging
from datetime import datetime


class FixedWidthFormatter(logging.Formatter):
    """
    Custom log formatter that outputs log records in a fixed-width format:
    [LEVEL] [TIMESTAMP]  [TITLE] [MESSAGE]

    Example:
        INFO    2025-06-28 20:00:00  Puller Starting pull operation...
    """
    def __init__(self):
        super().__init__()
        self.datefmt = "%Y-%m-%d %H:%M:%S"

    def format(self, record):
        """
        Format the log record with fixed-width fields.

        Args:
            record (logging.LogRecord): The log record to format.

        Returns:
            str: Formatted log string.
        """
        level = record.levelname.ljust(7)  # Pad level to align messages
        timestamp = datetime.fromtimestamp(record.created).strftime(self.datefmt)
        title = getattr(record, 'title', '-')  # Optional custom field
        message = record.getMessage()
        return f"{level} {timestamp}  {title} {message}"


def get_fixed_width_logger(name: str = "dataform-cli", level=logging.DEBUG) -> logging.Logger:
    """
    Creates a logger with a fixed-width formatter for consistent, readable output.

    Args:
        name (str): Logger name. Useful for identifying log sources.
        level (int): Logging level (e.g., logging.DEBUG, logging.INFO).

    Returns:
        logging.Logger: Configured logger instance.
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Only add a handler if the logger has none to prevent duplicate output
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = FixedWidthFormatter()
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger
