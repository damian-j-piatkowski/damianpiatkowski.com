from datetime import datetime, timezone


class Log:
    """Represents a log entry.

    Attributes:
        level: The severity level of the log (e.g., 'INFO', 'WARNING', 'ERROR').
        message: The log message.
        timestamp: The UTC timestamp when the log entry was created.
    """

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
