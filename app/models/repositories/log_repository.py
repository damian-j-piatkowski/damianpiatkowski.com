"""LogRepository for managing log entries in the database.

This module defines the LogRepository class, responsible for handling
CRUD operations on the logs table. It provides methods for creating,
retrieving, updating, and deleting log entries, and raises informative
errors in case of database issues.

Methods:
- create_log: Inserts a new log entry into the database.
- fetch_all_logs: Retrieves all log entries as Log domain objects.
"""

from typing import List

from sqlalchemy import insert, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.domain.log import Log
from app.models.tables.log import logs


class LogRepository:
    """Repository for managing log entries in the database."""

    def __init__(self, session: Session) -> None:
        """
        Initializes the repository with a SQLAlchemy session.

        Args:
            session: A SQLAlchemy session used to interact with the database.
        """
        self.session = session

    def create_log(self, log: Log) -> Log:
        """
        Inserts a new log entry into the database.

        Args:
            log: The Log object containing the level and message.

        Returns:
            The created Log object with the database-generated ID and timestamp.
        """
        try:
            stmt = insert(logs).values(
                level=log.level,
                message=log.message,
            ).returning(logs.c.id, logs.c.timestamp)  # Fetch generated ID and timestamp
            result = self.session.execute(stmt).one()
            self.session.commit()

            # Update the log object with generated ID and timestamp
            log.log_id = result.id
            log.timestamp = result.timestamp
            return log
        except SQLAlchemyError as e:
            self.session.rollback()
            raise RuntimeError("Failed to create log in the database.") from e

    def fetch_all_logs(self) -> List[Log]:
        """
        Retrieves all log entries as Log domain objects.

        Returns:
            A list of Log objects representing all log entries.
        """
        try:
            query = select(logs)  # SQLAlchemy select statement
            result = self.session.execute(query).mappings().all()  # Dict-like rows

            return [
                Log(
                    log_id=row['id'],
                    level=row['level'],
                    message=row['message'],
                    timestamp=row['timestamp'],  # Assume DB timestamps are UTC
                )
                for row in result
            ] if result else []
        except SQLAlchemyError as e:
            raise RuntimeError("Failed to fetch logs from the database.") from e
