from typing import Callable
import pytest
from sqlalchemy.orm import Session
from datetime import datetime, timezone

from app.domain.log import Log
from app.models.repositories.log_repository import LogRepository


@pytest.fixture(scope="function")
def create_log(session: Session) -> Callable[..., Log]:
    """Fixture to create a Log instance using the LogRepository.

    The log is persisted in the database, and the repository ensures
    proper handling of the database operations.

    Args:
        session: The SQLAlchemy session used by the LogRepository.

    Returns:
        Callable: A callable to create and persist a Log entry.
    """

    def _create_log(level: str = "INFO", message: str = "Test log message") -> Log:
        log_entry = Log(
            log_id=None,  # todo investigate how to assign whatever was given from the db
            level=level,
            message=message,
            timestamp=datetime.now(timezone.utc),  # Assign the current UTC time
        )
        log_repo = LogRepository(session)
        return log_repo.create_log(log_entry)

    return _create_log
