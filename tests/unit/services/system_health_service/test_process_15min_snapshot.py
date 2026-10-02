"""Unit tests for SystemHealthService.process_15min_snapshot alert logic."""

from datetime import datetime, timedelta, timezone

from app.models.repositories.system_health_log_repository import SystemHealthLogRepository
from app.services.system_health_service import SystemHealthService


def test_process_snapshot_sends_alert_when_thresholds_exceeded(app, session, mocker):
    """Verifies that high metrics trigger an alert email and alert_sent=True."""
    mocker.patch.object(
        SystemHealthService,
        "get_node_metrics",
        return_value={
            "cpu_percent": 95.0,
            "ram_percent": 50.0,
            "ram_used_mb": 500.0,
            "swap_percent": 1.0,
            "disk_percent": 40.0,
            "uptime": "1d",
            "os_info": "test",
            "environment": "DEV MOCK",
        },
    )
    send = mocker.patch("app.services.email_service.send_system_health_alert")

    with app.app_context():
        service = SystemHealthService(session)
        result = service.process_15min_snapshot()

    assert result["persisted"] is True
    assert result["alert_sent"] is True
    send.assert_called_once()


def test_process_snapshot_respects_alert_cooldown(app, session, mocker):
    """Verifies that a recent alert_sent row suppresses another alert within one hour."""
    repo = SystemHealthLogRepository(session)
    repo.insert(
        cpu_percent=10.0,
        ram_percent=10.0,
        ram_used_mb=100.0,
        swap_percent=0.0,
        disk_percent=10.0,
        alert_sent=True,
        timestamp=datetime.now(timezone.utc) - timedelta(minutes=10),
    )
    session.flush()

    mocker.patch.object(
        SystemHealthService,
        "get_node_metrics",
        return_value={
            "cpu_percent": 99.0,
            "ram_percent": 90.0,
            "ram_used_mb": 900.0,
            "swap_percent": 10.0,
            "disk_percent": 95.0,
            "uptime": "1d",
            "os_info": "test",
            "environment": "DEV MOCK",
        },
    )
    send = mocker.patch("app.services.email_service.send_system_health_alert")

    with app.app_context():
        service = SystemHealthService(session)
        result = service.process_15min_snapshot()

    assert result["persisted"] is True
    assert result["alert_sent"] is False
    send.assert_not_called()


def test_process_snapshot_skips_persistence_in_development(app, session, mocker):
    """Verifies that development environment does not write snapshot rows."""
    mocker.patch.dict(app.config, {"FLASK_ENV": "development", "TESTING": False})
    mocker.patch.object(
        SystemHealthService,
        "get_node_metrics",
        return_value={
            "cpu_percent": 10.0,
            "ram_percent": 10.0,
            "ram_used_mb": 100.0,
            "swap_percent": 0.0,
            "disk_percent": 10.0,
            "uptime": "1d",
            "os_info": "test",
            "environment": "DEV MOCK",
        },
    )

    with app.app_context():
        service = SystemHealthService(session)
        result = service.process_15min_snapshot()

    assert result["persisted"] is False
    assert SystemHealthLogRepository(session).list_since(
        datetime.now(timezone.utc) - timedelta(days=1)
    ) == []
