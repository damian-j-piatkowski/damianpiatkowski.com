"""Tests for the Log model.

This module contains tests for the CRUD operations on the Log model,
ensuring that log entries can be inserted, updated, deleted, and
queried correctly in the database.

Test functions:
- test_log_delete: Tests deleting a log entry from the database.
- test_log_insert_multiple: Tests inserting multiple log entries
    with different levels and messages.
- test_log_update: Tests updating a log entry in the database.
"""

import pytest
from sqlalchemy.orm import Session

from app.domain.log import Log


def test_log_delete(session: Session, create_log):
    """Test deleting a log entry from the database."""
    create_log()  # Use default values from the fixture
    session.commit()

    # Fetch and delete the log entry
    fetched_log = session.query(Log).filter_by(level='INFO').first()
    assert fetched_log is not None
    session.delete(fetched_log)
    session.commit()

    # Verify the log entry has been deleted
    deleted_log = session.query(Log).filter_by(level='INFO').first()
    assert deleted_log is None


@pytest.mark.parametrize("level, message", [
    ('DEBUG', 'Debug log message'),
    ('WARNING', 'Warning log message'),
    ('CRITICAL', 'Critical log message'),
])
def test_log_insert_multiple(session: Session, create_log, level, message):
    """Test inserting multiple logs with different levels and messages."""
    create_log(level=level, message=message)
    session.commit()

    # Fetch and verify the log entry
    fetched_log = session.query(Log).filter_by(level=level).first()
    assert fetched_log is not None
    assert fetched_log.level == level
    assert fetched_log.message == message


def test_log_update(session: Session, create_log):
    """Test updating a log entry in the database."""
    create_log()  # Use default values from the fixture
    session.commit()

    # Fetch and update the log entry
    fetched_log = session.query(Log).filter_by(level='INFO').first()
    assert fetched_log is not None
    fetched_log.message = 'Updated log message'
    session.commit()

    # Verify the updated log entry
    updated_log = session.query(Log).filter_by(level='INFO').first()
    assert updated_log is not None
    assert updated_log.message == 'Updated log message'
