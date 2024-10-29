"""LogRepository for managing log entries in the database.

This module defines the LogRepository class, responsible for handling
CRUD operations on the logs table. It provides methods for creating,
retrieving, updating, and deleting log entries, and raises informative
errors in case of database issues.

Methods:
- create_log: Inserts a new log entry into the database.
- delete_log: Deletes a log entry from the database.
- fetch_all_logs: Retrieves all log entries from the database.
- fetch_log_by_id: Retrieves a log entry by its ID.
- update_log: Updates an existing log entry by its ID.
"""
from typing import List, Optional, Dict

from sqlalchemy import insert, select, update, delete
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

    def create_log(self, log: Log) -> None:
        """
        Inserts a new log entry into the database.

        Args:
            log: The Log object containing the level, message, and timestamp.
        """
        try:
            stmt = insert(logs).values(
                level=log.level,
                message=log.message,
                timestamp=log.timestamp
            )
            self.session.execute(stmt)
            self.session.commit()
        except SQLAlchemyError as e:
            print(f"Database error occurred while creating a log: {e}")
            raise RuntimeError("Failed to create log in the database.") from e

    def delete_log(self, log_id: int) -> None:
        """
        Deletes a log entry from the database by its ID.

        Args:
            log_id: The ID of the log entry to delete.
        """
        try:
            stmt = delete(logs).where(logs.c.id == log_id)
            self.session.execute(stmt)
            self.session.commit()
        except SQLAlchemyError as e:
            print(f"Database error occurred while deleting log: {e}")
            raise RuntimeError("Failed to delete log from the database.") from e

    def fetch_all_logs(self) -> List[Dict[str, str]]:
        """
        Fetches all log entries from the database in a dictionary format.

        Returns:
            A list of dictionaries representing the logs in the database.
        """
        try:
            stmt = select(logs)
            result = self.session.execute(stmt).mappings().all()
            return [dict(row) for row in result] if result else []
        except SQLAlchemyError as e:
            print(f"Database error occurred while fetching logs: {e}")
            raise RuntimeError("Failed to fetch logs from the database.") from e

    def fetch_log_by_id(self, log_id: int) -> Optional[Log]:
        """
        Fetches a single log entry by its ID.

        Args:
            log_id: The ID of the log entry to fetch.

        Returns:
            A Log object if found, otherwise None.
        """
        try:
            stmt = select(logs).where(logs.c.id == log_id)
            result = self.session.execute(stmt).first()

            if result:
                return Log(level=result.level, message=result.message)
            return None
        except SQLAlchemyError as e:
            print(f"Database error occurred while fetching log by ID: {e}")
            raise RuntimeError(
                "Failed to fetch log by ID from the database.") from e

    def update_log(self, log_id: int, level: str, message: str) -> None:
        """
        Updates an existing log entry by its ID.

        Args:
            log_id: The ID of the log entry to update.
            level: The updated severity level.
            message: The updated log message.
        """
        try:
            stmt = (
                update(logs)
                .where(logs.c.id == log_id)
                .values(level=level, message=message)
            )
            self.session.execute(stmt)
            self.session.commit()
        except SQLAlchemyError as e:
            print(f"Database error occurred while updating log: {e}")
            raise RuntimeError("Failed to update log in the database.") from e
