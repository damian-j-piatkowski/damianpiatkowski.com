"""Route and controller tests for admin hubs and dictionary dashboard."""

import pytest

from app.services.auth_service import hash_password
from app.models.repositories.user_repository import UserRepository
from app.models.tables.word_han_viet_association import word_han_viet_association
from app.models.tables.word_type_association import word_type_association


@pytest.mark.dictionary
def test_login_defaults_to_admin_home(client, session):
    repository = UserRepository(session)
    repository.create_user(username="admin", password_hash=hash_password("secret"))
    session.flush()

    response = client.post(
        "/admin/login",
        data={"username": "admin", "password": "secret"},
        follow_redirects=False,
    )
    assert response.status_code == 302
    assert response.headers["Location"].endswith("/admin")


@pytest.mark.dictionary
def test_login_rejects_protocol_relative_next(client, session):
    repository = UserRepository(session)
    repository.create_user(username="admin", password_hash=hash_password("secret"))
    session.flush()

    response = client.post(
        "/admin/login",
        data={
            "username": "admin",
            "password": "secret",
            "next": "//evil.example/phish",
        },
        follow_redirects=False,
    )
    assert response.status_code == 302
    assert response.headers["Location"].endswith("/admin")
    assert "evil" not in response.headers["Location"]


@pytest.mark.dictionary
def test_admin_hub_pages_require_auth(client):
    for path in (
        "/admin",
        "/admin/blog",
        "/admin/dictionary",
        "/admin/dictionary/dashboard",
    ):
        response = client.get(path)
        assert response.status_code in {302, 401}


@pytest.mark.dictionary
def test_admin_hub_pages_render_for_admin(auth_client):
    home = auth_client.get("/admin")
    assert home.status_code == 200
    assert b"admin-tile-dictionary" in home.data
    assert b"admin-tile-blog" in home.data

    blog = auth_client.get("/admin/blog")
    assert blog.status_code == 200
    assert b"Work in progress" in blog.data

    hub = auth_client.get("/admin/dictionary")
    assert hub.status_code == 200
    assert b"admin-add-new-word" in hub.data
    assert b"admin-dictionary-dashboard" in hub.data
    assert b"admin-logout-link" in hub.data


@pytest.mark.dictionary
def test_dictionary_dashboard_tabs(
        auth_client,
        session,
        make_word,
        make_source,
        make_example,
        make_root,
):
    word = make_word(viet_word="học tập", english_translation="to study")
    session.execute(
        word_type_association.insert().values(word_id=word.id, word_type="verb")
    )
    root = make_root(root="học", chinese_character="學", root_meaning="study")
    session.execute(
        word_han_viet_association.insert().values(word_id=word.id, root_id=root.id)
    )
    source = make_source(source_type="book", title="Dashboard Source")
    make_example(
        word_id=word.id,
        source_id=source.id,
        sentence="Tôi học tập.",
        english_translation="I study.",
    )
    session.flush()

    general = auth_client.get("/admin/dictionary/dashboard?tab=general")
    assert general.status_code == 200
    assert b"kpi-total-words" in general.data
    assert b"word-velocity-chart" in general.data

    sources = auth_client.get(
        "/admin/dictionary/dashboard?tab=sources&q=Dashboard&type=book"
    )
    assert sources.status_code == 200
    assert b"Dashboard Source" in sources.data
    assert b"sources-catalog-table" in sources.data

    han_viet = auth_client.get("/admin/dictionary/dashboard?tab=han-viet")
    assert han_viet.status_code == 200
    assert b"kpi-total-roots" in han_viet.data

    health = auth_client.get("/admin/dictionary/dashboard?tab=data-health")
    assert health.status_code == 200
    assert b"Words Missing Examples" in health.data


@pytest.mark.dictionary
def test_word_velocity_api(auth_client, client, session, make_word):
    make_word(viet_word="chạy", english_translation="to run")
    session.flush()

    with client.session_transaction() as sess:
        sess.clear()

    unauth = client.get(
        "/admin/api/stats/word-velocity?range=30d",
        headers={"Accept": "application/json", "X-Requested-With": "XMLHttpRequest"},
    )
    assert unauth.status_code == 401

    # Re-authenticate for the remaining assertions.
    with client.session_transaction() as sess:
        sess["is_admin"] = True

    for range_key in ("30d", "6m", "12m"):
        response = client.get(
            f"/admin/api/stats/word-velocity?range={range_key}",
            headers={"Accept": "application/json"},
        )
        assert response.status_code == 200
        payload = response.get_json()
        assert isinstance(payload["labels"], list)
        assert isinstance(payload["counts"], list)
        assert len(payload["labels"]) == len(payload["counts"])

    bad = client.get(
        "/admin/api/stats/word-velocity?range=7d",
        headers={"Accept": "application/json"},
    )
    assert bad.status_code == 400


@pytest.mark.dictionary
def test_public_dictionary_copy(client):
    response = client.get("/dictionary")
    assert response.status_code == 200
    assert b"living Vietnamese" in response.data
    assert b"Type a Vietnamese word or phrase" in response.data
    assert b"Add new word" not in response.data
