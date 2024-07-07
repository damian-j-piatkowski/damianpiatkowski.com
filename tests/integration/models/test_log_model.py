from app.domain.log import Log

def test_insert_log(session):
    log_entry = Log(
        level='INFO',
        message='Test log message'
    )
    session.add(log_entry)
    session.commit()

    # Fetch the log entry from the database
    fetched_log = session.query(Log).filter_by(level='INFO').first()
    assert fetched_log is not None
    assert fetched_log.level == 'INFO'
    assert fetched_log.message == 'Test log message'

def test_update_log(session):
    # Insert a new log entry
    log_entry = Log(
        level='INFO',
        message='Test log message'
    )
    session.add(log_entry)
    session.commit()

    # Fetch the log entry from the database
    fetched_log = session.query(Log).filter_by(level='INFO').first()
    assert fetched_log is not None

    # Update the log entry
    fetched_log.message = 'Updated log message'
    session.commit()

    # Fetch the updated log entry
    updated_log = session.query(Log).filter_by(level='INFO').first()
    assert updated_log is not None
    assert updated_log.message == 'Updated log message'


def test_insert_delete_log(session):
    # Insert a new log entry
    log_entry = Log(
        level='INFO',
        message='Test log message'
    )
    session.add(log_entry)
    session.commit()

    # Fetch the log entry from the database
    fetched_log = session.query(Log).filter_by(level='INFO').first()
    assert fetched_log is not None

    # Delete the log entry
    session.delete(fetched_log)
    session.commit()

    # Ensure the log entry has been deleted
    deleted_log = session.query(Log).filter_by(level='INFO').first()
    assert deleted_log is None


def test_insert_multiple_logs(session):
    # Insert multiple log entries
    log_entries = [
        Log(level='DEBUG', message='Debug log message'),
        Log(level='WARNING', message='Warning log message'),
        Log(level='CRITICAL', message='Critical log message')
    ]
    session.add_all(log_entries)
    session.commit()

    # Fetch and verify multiple log entries
    fetched_debug_log = session.query(Log).filter_by(level='DEBUG').first()
    assert fetched_debug_log is not None
    assert fetched_debug_log.level == 'DEBUG'
    assert fetched_debug_log.message == 'Debug log message'

    fetched_warning_log = session.query(Log).filter_by(level='WARNING').first()
    assert fetched_warning_log is not None
    assert fetched_warning_log.level == 'WARNING'
    assert fetched_warning_log.message == 'Warning log message'

    fetched_critical_log = session.query(Log).filter_by(level='CRITICAL').first()
    assert fetched_critical_log is not None
    assert fetched_critical_log.level == 'CRITICAL'
    assert fetched_critical_log.message == 'Critical log message'

