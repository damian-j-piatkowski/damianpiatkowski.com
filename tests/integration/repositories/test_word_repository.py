"""Integration tests for dictionary repositories."""

import pytest

from app.models.repositories.han_viet_repository import HanVietRepository
from app.models.repositories.source_repository import SourceRepository
from app.models.repositories.word_repository import WordRepository
from app.models.tables.word_han_viet_association import word_han_viet_association


@pytest.mark.dictionary
def test_word_repository_prefix_search(session, make_word):
    make_word(viet_word="bàn học", english_translation="study desk")
    make_word(viet_word="bàn ăn", english_translation="dining table")
    make_word(viet_word="ghế", english_translation="chair")
    session.flush()

    repository = WordRepository(session)
    results = repository.search_by_prefix("bàn")

    assert {word.viet_word for word in results} == {"bàn học", "bàn ăn"}


@pytest.mark.dictionary
def test_word_repository_duplicate_lookup(session, make_word):
    make_word(viet_word="sách", english_translation="book")
    session.flush()

    repository = WordRepository(session)
    found = repository.find_by_viet_word("sách")
    missing = repository.find_by_viet_word("không có")

    assert found is not None
    assert found.viet_word == "sách"
    assert missing is None


@pytest.mark.dictionary
def test_word_repository_create_with_types(session):
    repository = WordRepository(session)
    word = repository.create(
        viet_word="báo cáo",
        english_translation="to report",
        word_types=["noun", "verb"],
    )

    assert word.id is not None
    assert set(word.word_types) == {"noun", "verb"}


@pytest.mark.dictionary
def test_han_viet_batch_lookup(session, make_root):
    make_root(root="chính", chinese_character="政", root_meaning="politics")
    make_root(root="trị", chinese_character="治", root_meaning="rule")
    session.flush()

    repository = HanVietRepository(session)
    found = repository.find_by_roots(["chính", "trị", "học"])

    assert set(found.keys()) == {"chính", "trị"}


@pytest.mark.dictionary
def test_han_viet_unlink_preserves_root(session, make_word, make_root, bind_word_han_viet):
    word = make_word(viet_word="pháp luật", english_translation="law")
    root = make_root(root="pháp", chinese_character="法", root_meaning="law")
    bind_word_han_viet(word.id, root.id)
    session.flush()

    repository = HanVietRepository(session)
    repository.unlink(word.id, root.id)

    remaining = session.execute(word_han_viet_association.select()).fetchall()
    assert remaining == []
    assert repository.get_by_id(root.id).root == "pháp"


@pytest.mark.dictionary
def test_source_repository_requires_title_at_db_when_empty_string_bypassed(session):
    repository = SourceRepository(session)
    source = repository.create(source_type="book", title="Truyện Kiều", url=None)
    assert source.title == "Truyện Kiều"
    recent = repository.list_recent(limit=5)
    assert any(item.id == source.id for item in recent)
