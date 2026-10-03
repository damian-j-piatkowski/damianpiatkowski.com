"""Route tests for standalone Hán Việt root creation and create workspace tab."""

import pytest


@pytest.mark.dictionary
def test_create_han_viet_tab_renders(auth_client):
    """Verifies that the Create Hán Việt root workspace tab renders for admins."""
    response = auth_client.get("/admin/dictionary/new?tab=han-viet")
    assert response.status_code == 200
    assert b"create-han-viet-panel" in response.data
    assert "Create Hán Việt root".encode("utf-8") in response.data


@pytest.mark.dictionary
def test_create_standalone_han_viet_root_api(auth_client, client):
    """Verifies that POST /admin/dictionary/han-viet creates a root without a word."""
    with client.session_transaction() as sess:
        sess.clear()

    unauth = client.post(
        "/admin/dictionary/han-viet",
        json={"root": "học", "chinese_character": "學", "root_meaning": "study"},
        headers={"Accept": "application/json", "X-Requested-With": "XMLHttpRequest"},
    )
    assert unauth.status_code == 401

    with client.session_transaction() as sess:
        sess["is_admin"] = True

    response = client.post(
        "/admin/dictionary/han-viet",
        json={"root": "học", "chinese_character": "學", "root_meaning": "study"},
        headers={"Accept": "application/json"},
    )
    assert response.status_code == 201
    payload = response.get_json()
    assert payload["success"] is True
    assert payload["root"]["root"] == "học"
