"""Route tests for the admin System Health module."""

import pytest


@pytest.mark.dictionary
def test_system_health_pages_require_auth(client):
    """Verifies that System Health pages redirect unauthenticated browsers."""
    for path in (
        "/admin/system-health",
        "/admin/system-health?tab=trends",
    ):
        response = client.get(path)
        assert response.status_code in {302, 401}


@pytest.mark.dictionary
def test_system_health_apis_require_auth(client):
    """Verifies that System Health JSON APIs return 401 without an admin session."""
    for path in (
        "/admin/api/system-health/stats",
        "/admin/api/system-health/history?range=24h",
    ):
        response = client.get(
            path,
            headers={"Accept": "application/json", "X-Requested-With": "XMLHttpRequest"},
        )
        assert response.status_code == 401


@pytest.mark.dictionary
def test_system_health_page_renders_for_admin(auth_client):
    """Verifies that authenticated admins receive the live System Health page."""
    response = auth_client.get("/admin/system-health?tab=live")
    assert response.status_code == 200
    assert b"System Health" in response.data
    assert b"data-system-health-live" in response.data
    assert b"kpi-cpu" in response.data
    assert b"Back to Admin Hub" in response.data


@pytest.mark.dictionary
def test_system_health_trends_page_renders_for_admin(auth_client):
    """Verifies that the trends tab includes Chart.js canvas markup."""
    response = auth_client.get("/admin/system-health?tab=trends")
    assert response.status_code == 200
    assert b"data-system-health-trends" in response.data
    assert b"system-health-chart" in response.data


@pytest.mark.dictionary
def test_system_health_stats_json_shape(auth_client):
    """Verifies that live stats JSON includes mock metric fields."""
    response = auth_client.get(
        "/admin/api/system-health/stats",
        headers={"Accept": "application/json"},
    )
    assert response.status_code == 200
    payload = response.get_json()
    assert payload["environment"] == "DEV MOCK"
    assert isinstance(payload["cpu_percent"], (int, float))
    assert isinstance(payload["ram_percent"], (int, float))
    assert isinstance(payload["disk_percent"], (int, float))


@pytest.mark.dictionary
def test_system_health_history_json_and_invalid_range(auth_client):
    """Verifies history JSON shape and 400 for unsupported ranges."""
    ok = auth_client.get(
        "/admin/api/system-health/history?range=24h",
        headers={"Accept": "application/json"},
    )
    assert ok.status_code == 200
    payload = ok.get_json()
    assert isinstance(payload["labels"], list)
    assert isinstance(payload["cpu"], list)
    assert isinstance(payload["ram"], list)

    bad = auth_client.get(
        "/admin/api/system-health/history?range=1h",
        headers={"Accept": "application/json"},
    )
    assert bad.status_code == 400


@pytest.mark.dictionary
def test_admin_home_includes_system_health_tile(auth_client):
    """Verifies that the admin landing page exposes the System Health tile."""
    home = auth_client.get("/admin")
    assert home.status_code == 200
    assert b"admin-tile-system-health" in home.data
    assert b"system health are available now" in home.data
