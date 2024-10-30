from sqlalchemy import text

from app.domain.log import Log
from app.models.repositories.log_repository import LogRepository

def test_fetch_all_logs(session, create_log):
    """Test fetching all log entries from the database."""
    # Arrange: Create and commit log entries
    log1 = create_log(level="INFO", message="Test log 1")
    log2 = create_log(level="ERROR", message="Test log 2")
    session.commit()

    # Act: Fetch logs using the repository
    repo = LogRepository(session)
    result = repo.fetch_all_logs()

    # Assert: Ensure the fetched data is correct
    assert len(result) == 2
    assert result[0]["message"] == log1.message
    assert result[1]["message"] == log2.message



def test_create_log(session):
    """Test creating a log entry in the database."""
    # Act: Use the repository to create a log entry
    repo = LogRepository(session)
    log_entry = Log(level="WARNING", message="Integration test log")
    repo.create_log(log_entry)

    # Assert: Ensure the log entry was created
    result = session.execute(
        text("SELECT * FROM logs WHERE message='Integration test log'")
    ).fetchone()  # Use text() to wrap raw SQL
    assert result is not None


def test_fetch_log_by_id(session, create_log):
    """Test fetching a log by its ID from the database."""
    # Arrange: Create and commit a log entry
    log_entry = create_log(level="INFO", message="Fetch log by ID")
    session.commit()

    # Act: Fetch the log by its ID
    repo = LogRepository(session)
    fetched_log = repo.fetch_log_by_id(int(log_entry.id))

    # Assert: Ensure the log entry matches the fetched data
    assert fetched_log is not None
    assert fetched_log.message == log_entry.message


def test_delete_log(session, create_log):
    """Test deleting a log entry by its ID."""
    # Arrange
    log_entry = Log(level="INFO", message="Test log entry")
    session.add(log_entry)
    session.commit()

    log_id = log_entry.id  # Store the log ID before clearing the session

    # Act: Delete the log by its ID
    repo = LogRepository(session)
    repo.delete_log(int(log_id))

    # Clear the session to avoid accessing the deleted object
    session.expunge_all()

    # Assert: Ensure the log entry was deleted by directly querying the database
    result = session.execute(
        text(f"SELECT * FROM logs WHERE id={log_id}")
    ).fetchone()  # Check via raw SQL to confirm deletion

    assert result is None


def test_update_log(session, create_log):
    """Test updating a log entry in the database."""
    # Arrange: Create and commit a log entry
    log_entry = create_log(level="INFO", message="Log to be updated")
    session.commit()

    # Act: Update the log entry
    repo = LogRepository(session)
    repo.update_log(int(log_entry.id), level="ERROR",
                    message="Updated log message")

    # Assert: Ensure the log entry was updated
    updated_log = session.execute(
        text(f"SELECT * FROM logs WHERE id={log_entry.id}")
    ).fetchone()  # Use text() to wrap raw SQL
    assert updated_log.level == "ERROR"
    assert updated_log.message == "Updated log message"
