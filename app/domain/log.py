"""Module for representing and managing log entries.

This module contains the definition of the `Log` class,
which models a log entry in the system.

The `Log` class includes attributes to store details of a log entry
such as its unique identifier, severity level, message, and timestamp.

The class-level type hints provide clear indications of the expected data
types for each attribute.

Classes:
- Log: Represents a log entry with attributes for id, level, message, and timestamp.

Example Usage:
    log_entry = Log(
        log_id=1,
        level='INFO',
        message='This is an informational log message.',
        timestamp=datetime(2024, 12, 20, 14, 30, tzinfo=timezone.utc)
    )
"""

from datetime import datetime, timezone
from typing import Optional


class Log:
    """Represents a log entry.

    Attributes:
        log_id: The unique identifier for the log entry.
        level: The severity level of the log (e.g., 'INFO', 'WARNING', 'ERROR').
        message: The log message.
        timestamp: The UTC timestamp when the log entry was created.
    """

    log_id: Optional[int]
    level: str
    message: str
    timestamp: Optional[datetime]

    def __init__(
            self,
            log_id: Optional[int],
            level: str,
            message: str,
            timestamp: Optional[datetime] = None,  # Default to None
    ) -> None:
        """
        Constructs all the necessary attributes for the Log object.

        Args:
            log_id: The unique identifier for the log entry.
            level: The severity level of the log.
            message: The log message.
            timestamp: The UTC timestamp of the log entry.
        """
        self.log_id = log_id
        self.level = level
        self.message = message
        # Use the provided timestamp or default to the current UTC time
        self.timestamp = timestamp or datetime.now(timezone.utc)
