"""Unit tests for SystemHealthService mock historical series."""

import pytest

from app.services.system_health_service import SystemHealthService, VALID_HISTORY_RANGES


@pytest.mark.parametrize("range_key", VALID_HISTORY_RANGES)
def test_get_historical_metrics_returns_mock_when_empty(app, session, range_key):
    """Verifies that empty history in testing yields non-empty mock Chart.js series."""
    with app.app_context():
        service = SystemHealthService(session)
        payload = service.get_historical_metrics(range_key)

    assert len(payload["labels"]) > 0
    assert len(payload["labels"]) == len(payload["cpu"]) == len(payload["ram"])
    assert all(isinstance(value, (int, float)) for value in payload["cpu"])
