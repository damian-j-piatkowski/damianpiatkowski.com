"""Controller and route tests for dictionary and admin authentication."""

import pytest

from app.controllers import dictionary_controller
from app.services.auth_service import hash_password
from app.models.repositories.user_repository import UserRepository


@pytest.mark.dictionary
def test_search_dictionary_controller(session, make_word, app):
    make_word(viet_word="bàn học", english_translation="study desk")
    session.flush()

    with app.test_request_context("/dictionary/search"):
        response, status = dictionary_controller.search_dictionary("bàn")
    assert status == 200
    payload = response.get_json()
    assert any(item["viet_word"] == "bàn học" for item in payload["results"])


@pytest.mark.dictionary
def test_check_duplicate_controller(session, make_word, app):
    make_word(viet_word="sách", english_translation="book")
    session.flush()

    with app.test_request_context("/admin/dictionary/check-duplicate"):
        response, status = dictionary_controller.check_duplicate("sách")
    assert status == 200
    payload = response.get_json()
    assert payload["exists"] is True
    assert payload["entry"]["viet_word"] == "sách"


@pytest.mark.dictionary
def test_create_word_controller_validation(app, session):
    with app.test_request_context("/admin/dictionary/words"):
        response, status = dictionary_controller.create_word("", "meaning")
    assert status == 400
    assert response.get_json()["field"] == "viet_word"


@pytest.mark.dictionary
def test_dictionary_search_route(client, session, make_word):
    make_word(viet_word="ghế", english_translation="chair")
    session.flush()

    response = client.get("/dictionary/search?q=ghế")
    assert response.status_code == 200
    assert response.get_json()["results"][0]["viet_word"] == "ghế"


@pytest.mark.dictionary
def test_admin_dictionary_routes_require_auth(client):
    response = client.get("/admin/dictionary/new")
    assert response.status_code in {302, 401}

    response = client.post("/admin/dictionary/words", json={
        "viet_word": "học",
        "english_translation": "to study",
    })
    assert response.status_code == 401


@pytest.mark.dictionary
def test_admin_login_and_protected_access(client, session):
    repository = UserRepository(session)
    repository.create_user(username="admin", password_hash=hash_password("secret"))
    session.flush()

    response = client.post(
        "/admin/login",
        data={"username": "admin", "password": "secret"},
        follow_redirects=False,
    )
    assert response.status_code == 302

    with client.session_transaction() as sess:
        assert sess.get("is_admin") is True

    page = client.get("/admin/dictionary/new")
    assert page.status_code == 200


@pytest.mark.dictionary
def test_blog_admin_requires_auth(client):
    response = client.delete("/admin/delete-blog-posts", json={"slugs": ["x"]})
    assert response.status_code == 401
