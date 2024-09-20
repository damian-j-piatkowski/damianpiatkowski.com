from unittest.mock import MagicMock

import pytest
from sqlalchemy.exc import SQLAlchemyError

from app.domain.log import Log
from app.models.repositories.log_repository import LogRepository


# Unit tests for LogRepository

def test_create_log_success():
    """Test successfully creating a log entry."""
    # Arrange
    mock_session = MagicMock()
    repository = LogRepository(mock_session)
    log = MagicMock()

    # Act
    repository.create_log(log)

    # Assert
    mock_session.execute.assert_called_once()
    mock_session.commit.assert_called_once()


def test_create_log_failure():
    """Test failure to create a log entry."""
    # Arrange
    mock_session = MagicMock()
    mock_session.execute.side_effect = SQLAlchemyError
    repository = LogRepository(mock_session)
    log = MagicMock()

    # Act & Assert
    with pytest.raises(RuntimeError):
        repository.create_log(log)


def test_fetch_all_logs_success():
    """Test successfully fetching all log entries."""
    # Arrange
    mock_session = MagicMock()

    # Create mock Log objects
    log1 = MagicMock(spec=Log, level='INFO', message='Log 1')
    log2 = MagicMock(spec=Log, level='ERROR', message='Log 2')

    mock_session.execute.return_value.fetchall.return_value = [log1, log2]
    repository = LogRepository(mock_session)

    # Act
    logs = repository.fetch_all_logs()

    # Assert
    assert len(logs) == 2
    assert logs[0].message == 'Log 1'
    assert logs[0].level == 'INFO'
    assert logs[1].message == 'Log 2'
    assert logs[1].level == 'ERROR'


def test_fetch_log_by_id_success():
    """Test successfully fetching a log entry by ID."""
    # Arrange
    mock_session = MagicMock()

    # Create a mock Log object
    log = MagicMock(spec=Log, level='INFO', message='Log 1')

    mock_session.execute.return_value.first.return_value = log
    repository = LogRepository(mock_session)

    # Act
    fetched_log = repository.fetch_log_by_id(1)

    # Assert
    assert fetched_log is not None
    assert fetched_log.message == 'Log 1'
    assert fetched_log.level == 'INFO'


def test_fetch_log_by_id_failure():
    """Test failure when fetching a log entry by a non-existent ID."""
    # Arrange
    mock_session = MagicMock()
    mock_session.execute.return_value.first.return_value = None
    repository = LogRepository(mock_session)

    # Act
    log = repository.fetch_log_by_id(999)

    # Assert
    assert log is None


def test_delete_log_success():
    """Test successfully deleting a log entry."""
    # Arrange
    mock_session = MagicMock()
    repository = LogRepository(mock_session)

    # Act
    repository.delete_log(1)

    # Assert
    mock_session.execute.assert_called_once()
    mock_session.commit.assert_called_once()


def test_delete_log_failure():
    """Test failure to delete a log entry."""
    # Arrange
    mock_session = MagicMock()
    mock_session.execute.side_effect = SQLAlchemyError
    repository = LogRepository(mock_session)

    # Act & Assert
    with pytest.raises(RuntimeError):
        repository.delete_log(1)


def test_update_log_success():
    """Test successfully updating a log entry."""
    # Arrange
    mock_session = MagicMock()
    repository = LogRepository(mock_session)

    # Act
    repository.update_log(1, level="ERROR", message="Updated message")

    # Assert
    mock_session.execute.assert_called_once()
    mock_session.commit.assert_called_once()


def test_update_log_failure():
    """Test failure to update a log entry."""
    # Arrange
    mock_session = MagicMock()
    mock_session.execute.side_effect = SQLAlchemyError
    repository = LogRepository(mock_session)

    # Act & Assert
    with pytest.raises(RuntimeError):
        repository.update_log(1, level="ERROR", message="Update failed")
