"""Unit tests for SystemHealthService history range validation."""

import pytest

from app.services.system_health_service import SystemHealthService


def test_get_historical_metrics_rejects_invalid_range(app, session):
    """Verifies that unsupported history ranges raise ValueError."""
    with app.app_context():
        service = SystemHealthService(session)
        with pytest.raises(ValueError, match="Unsupported health history range"):
            service.get_historical_metrics("1h")
