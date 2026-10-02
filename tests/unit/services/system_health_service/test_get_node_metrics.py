"""Unit tests for SystemHealthService.get_node_metrics."""

from app.services.system_health_service import SystemHealthService


def test_get_node_metrics_returns_dev_mock_in_testing(app, session):
    """Verifies that testing environment returns DEV MOCK metrics without psutil."""
    with app.app_context():
        service = SystemHealthService(session)
        metrics = service.get_node_metrics()

    assert metrics["environment"] == "DEV MOCK"
    assert "cpu_percent" in metrics
    assert "ram_percent" in metrics
    assert "disk_percent" in metrics
    assert "uptime" in metrics
    assert "os_info" in metrics
