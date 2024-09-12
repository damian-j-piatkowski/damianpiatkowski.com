"""Module for representing and managing log entries.

This module contains the definition of the `Log` class,
which models a log entry in the system.

The `Log` class includes attributes to store details of a log entry
such as its severity level, message, and timestamp.

The class-level type hints provide clear indications of the expected data
types for each attribute.

Classes:
- Log: Represents a log entry with attributes for level, message, and timestamp.

Example Usage:
    log_entry = Log(
        level='INFO',
        message='This is an informational log message.'
    )
"""

from datetime import datetime, timezone


class Log:
    """Represents a log entry.

    Attributes:
        level: The severity level of the log (e.g., 'INFO', 'WARNING', 'ERROR').
        message: The log message.
        timestamp: The UTC timestamp when the log entry was created.
    """

    id: str
    level: str
    message: str
    timestamp: datetime

    def __init__(self, level: str, message: str) -> None:
        """
        Constructs all the necessary attributes for the Log object.

        Args:
            level: The severity level of the log.
            message: The log message.
        """
        self.level = level
        self.message = message
        self.timestamp = datetime.now(timezone.utc)
