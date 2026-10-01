"""Route tests for public dictionary word detail pages.

Tests included:
    - test_word_detail_requires_no_auth: Verifies 200 for public visitors.
    - test_word_detail_shows_etymology: Verifies etymology badges render.
    - test_word_detail_unknown_id_404: Verifies missing words return 404.
"""

import pytest


@pytest.mark.dictionary
def test_word_detail_requires_no_auth(client, session, make_word):
    """Verifies that the public word detail page is available without admin auth."""
    word = make_word(viet_word="học", english_translation="to learn")
    session.flush()

    response = client.get(f"/dictionary/{word.id}")
    assert response.status_code == 200
    assert b"h\xe1\xbb\x8dc" in response.data or "học".encode("utf-8") in response.data


@pytest.mark.dictionary
def test_word_detail_shows_etymology(client, session, make_word, make_root, bind_word_han_viet):
    """Verifies that etymology badges appear when Hán Việt roots are linked."""
    word = make_word(viet_word="chính trị", english_translation="politics")
    root = make_root(root="chính", chinese_character="正", root_meaning="main")
    bind_word_han_viet(word.id, root.id)
    session.flush()

    response = client.get(f"/dictionary/{word.id}")
    assert response.status_code == 200
    assert b"Etymology" in response.data
    assert "正".encode("utf-8") in response.data
    assert b"/han-viet/" in response.data


@pytest.mark.dictionary
def test_word_detail_unknown_id_404(client):
    """Verifies that an unknown word id returns HTTP 404."""
    response = client.get("/dictionary/999999")
    assert response.status_code == 404
