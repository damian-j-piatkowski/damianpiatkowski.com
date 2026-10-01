"""Route tests for public Hán Việt explorer pages.

Tests included:
    - test_han_viet_index_public: Verifies explorer index is public.
    - test_han_viet_detail_public: Verifies root detail cluster is public.
    - test_han_viet_detail_unknown_404: Verifies missing roots return 404.
    - test_admin_create_source_tab: Verifies source tab on create workspace.
"""

import pytest


@pytest.mark.dictionary
def test_han_viet_index_public(client, session, seed_dashboard_han_viet):
    """Verifies that /han-viet is reachable without authentication."""
    seed_dashboard_han_viet()
    session.flush()

    response = client.get("/han-viet")
    assert response.status_code == 200
    assert b"H\xc3\xa1n Vi\xe1\xbb\x87t Explorer" in response.data or b"Explorer" in response.data
    assert "學".encode("utf-8") in response.data


@pytest.mark.dictionary
def test_han_viet_detail_public(client, session, seed_dashboard_han_viet):
    """Verifies that a root detail page renders compounds without auth."""
    seeded = seed_dashboard_han_viet()
    session.flush()

    response = client.get(f"/han-viet/{seeded['reused_root'].root}")
    assert response.status_code == 200
    assert "學".encode("utf-8") in response.data
    assert b"/dictionary/" in response.data


@pytest.mark.dictionary
def test_han_viet_detail_unknown_404(client):
    """Verifies that an unknown root syllable returns HTTP 404."""
    response = client.get("/han-viet/khong-ton-tai")
    assert response.status_code == 404


@pytest.mark.dictionary
def test_admin_create_source_tab(auth_client, client):
    """Verifies that create workspace tabs separate word and source forms."""
    with client.session_transaction() as sess:
        sess.clear()

    unauth = client.get("/admin/dictionary/new?tab=source")
    assert unauth.status_code in {302, 401}

    with client.session_transaction() as sess:
        sess["is_admin"] = True

    word_tab = client.get("/admin/dictionary/new?tab=word")
    assert word_tab.status_code == 200
    assert b"Create dictionary entry" in word_tab.data
    assert b"New source" not in word_tab.data
    assert b"create-source-panel" not in word_tab.data

    source_tab = client.get("/admin/dictionary/new?tab=source")
    assert source_tab.status_code == 200
    assert b"Create source entry" in source_tab.data
    assert b"create-source-panel" in source_tab.data
    assert b"id=\"create-source\"" in source_tab.data
