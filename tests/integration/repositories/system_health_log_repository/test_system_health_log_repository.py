"""Integration tests for SystemHealthLogRepository."""

from datetime import datetime, timedelta, timezone

import pytest

from app.models.repositories.system_health_log_repository import SystemHealthLogRepository


@pytest.mark.dictionary
def test_insert_and_list_since(session):
    """Verifies that inserted snapshots are returned by list_since."""
    repo = SystemHealthLogRepository(session)
    now = datetime.now(timezone.utc)
    repo.insert(
        cpu_percent=11.0,
        ram_percent=22.0,
        ram_used_mb=220.0,
        swap_percent=3.0,
        disk_percent=44.0,
        timestamp=now,
    )
    session.flush()

    rows = repo.list_since(now - timedelta(minutes=1))
    assert len(rows) == 1
    assert rows[0]["cpu_percent"] == 11.0
    assert rows[0]["ram_percent"] == 22.0
    assert rows[0]["alert_sent"] is False


@pytest.mark.dictionary
def test_prune_older_than(session):
    """Verifies that prune_older_than deletes only rows outside the retention window."""
    repo = SystemHealthLogRepository(session)
    now = datetime.now(timezone.utc)
    repo.insert(
        cpu_percent=1.0,
        ram_percent=1.0,
        ram_used_mb=10.0,
        swap_percent=0.0,
        disk_percent=1.0,
        timestamp=now - timedelta(days=200),
    )
    repo.insert(
        cpu_percent=2.0,
        ram_percent=2.0,
        ram_used_mb=20.0,
        swap_percent=0.0,
        disk_percent=2.0,
        timestamp=now,
    )
    session.flush()

    deleted = repo.prune_older_than(days=180)
    session.flush()
    remaining = repo.list_since(now - timedelta(days=365))

    assert deleted == 1
    assert len(remaining) == 1
    assert remaining[0]["cpu_percent"] == 2.0


@pytest.mark.dictionary
def test_last_alert_sent_at(session):
    """Verifies that last_alert_sent_at returns the latest alert_sent timestamp."""
    repo = SystemHealthLogRepository(session)
    older = datetime.now(timezone.utc) - timedelta(hours=3)
    newer = datetime.now(timezone.utc) - timedelta(hours=1)
    repo.insert(
        cpu_percent=1.0,
        ram_percent=1.0,
        ram_used_mb=10.0,
        swap_percent=0.0,
        disk_percent=1.0,
        alert_sent=True,
        timestamp=older,
    )
    repo.insert(
        cpu_percent=2.0,
        ram_percent=2.0,
        ram_used_mb=20.0,
        swap_percent=0.0,
        disk_percent=2.0,
        alert_sent=True,
        timestamp=newer,
    )
    session.flush()

    last = repo.last_alert_sent_at()
    assert last is not None
    assert abs((last - newer).total_seconds()) < 2
