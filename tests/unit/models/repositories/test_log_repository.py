from app.domain.log import Log
from app.models.repositories.log_repository import LogRepository


def test_create_log(session):
    """Test creating a log entry in the database."""
    repo = LogRepository(session)

    # Create a log entry
    log_entry = Log(
        log_id=None,  # Let the database assign this
        level="WARNING",
        message="Integration test log",
        timestamp=None,  # Database will assign this
    )
    created_log = repo.create_log(log_entry)

    # Verify the created log
    result = repo.fetch_all_logs()
    assert len(result) == 1
    assert result[0].message == created_log.message
    assert result[0].level == created_log.level
    assert result[0].log_id is not None
    assert result[0].timestamp is not None  # Ensure timestamp is set


def test_fetch_all_logs(session, create_log):
    """Test fetching all log entries from the database."""
    # Create multiple logs
    log1 = create_log(level="INFO", message="Test log 1")
    log2 = create_log(level="ERROR", message="Test log 2")
    session.commit()

    repo = LogRepository(session)
    result = repo.fetch_all_logs()

    # Verify fetched logs
    assert len(result) == 2
    assert result[0].message == log1.message
    assert result[0].level == log1.level
    assert result[0].log_id is not None
    assert result[0].timestamp is not None

    assert result[1].message == log2.message
    assert result[1].level == log2.level
    assert result[1].log_id is not None
    assert result[1].timestamp is not None


def test_fetch_all_logs_empty_db(session):
    """Test fetching all logs when the database is empty."""
    repo = LogRepository(session)
    result = repo.fetch_all_logs()

    # Verify the result is an empty list
    assert result == []
