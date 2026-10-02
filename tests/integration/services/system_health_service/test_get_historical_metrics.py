"""Integration tests for SystemHealthService historical bucketing."""

from datetime import datetime, timedelta, timezone

import pytest

from app.models.repositories.system_health_log_repository import SystemHealthLogRepository
from app.services.system_health_service import SystemHealthService


@pytest.mark.dictionary
@pytest.mark.parametrize("range_key", ["24h", "7d", "30d", "90d", "180d"])
def test_get_historical_metrics_shape(session, range_key):
    """Verifies that each history range returns aligned Chart.js series keys."""
    service = SystemHealthService(session)
    payload = service.get_historical_metrics(range_key)

    assert set(payload.keys()) >= {"labels", "cpu", "ram", "swap", "disk"}
    assert len(payload["labels"]) == len(payload["cpu"]) == len(payload["ram"])


@pytest.mark.dictionary
def test_get_historical_metrics_24h_includes_seeded_points(session):
    """Verifies that raw 24h history includes recently inserted snapshots."""
    repo = SystemHealthLogRepository(session)
    now = datetime.now(timezone.utc)
    repo.insert(
        cpu_percent=33.0,
        ram_percent=44.0,
        ram_used_mb=440.0,
        swap_percent=5.0,
        disk_percent=55.0,
        timestamp=now - timedelta(hours=2),
    )
    session.flush()

    service = SystemHealthService(session)
    payload = service.get_historical_metrics("24h")

    assert 33.0 in payload["cpu"]
    assert 44.0 in payload["ram"]
    assert len(payload["labels"]) >= 1
