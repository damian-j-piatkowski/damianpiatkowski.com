"""Integration tests for dictionary services."""

import pytest

from app.exceptions import (
    DictionaryValidationError,
    DictionaryWordDuplicateError,
    HanVietRootInUseError,
)
from app.models.repositories.han_viet_repository import HanVietRepository
from app.services.han_viet_service import HanVietService
from app.services.source_service import SourceService
from app.services.word_service import WordService
from app.models.tables.han_viet_root import han_viet_roots
from app.models.tables.word_han_viet_association import word_han_viet_association


@pytest.mark.dictionary
def test_word_service_rejects_blank_and_invalid_words(session):
    service = WordService(session)
    with pytest.raises(DictionaryValidationError):
        service.create_entry("   ", "meaning")
    with pytest.raises(DictionaryValidationError):
        service.create_entry("abc123", "meaning")


@pytest.mark.dictionary
def test_word_service_duplicate_check_and_create(session):
    service = WordService(session)
    created = service.create_entry("học tập", "to study", word_types=["verb"])
    assert created.viet_word == "học tập"
    assert service.check_duplicate("học tập") is not None
    with pytest.raises(DictionaryWordDuplicateError):
        service.create_entry("học tập", "again")


@pytest.mark.dictionary
def test_source_service_requires_title(session):
    service = SourceService(session)
    with pytest.raises(DictionaryValidationError):
        service.create(source_type="book", title="  ")


@pytest.mark.dictionary
def test_han_viet_service_found_and_missing(session, make_root):
    make_root(root="chính", chinese_character="政", root_meaning="politics")
    session.flush()

    service = HanVietService(session)
    result = service.check_existing_roots("chính trị")

    assert result["syllables"] == ["chính", "trị"]
    assert [item["root"] for item in result["found"]] == ["chính"]
    assert result["missing"] == ["trị"]


@pytest.mark.dictionary
def test_han_viet_root_deletion_safety(session, make_word, make_root, bind_word_han_viet):
    word = make_word(viet_word="nhân viên", english_translation="employee")
    root = make_root(root="nhân", chinese_character="人", root_meaning="person")
    bind_word_han_viet(word.id, root.id)
    session.flush()

    service = HanVietService(session)
    with pytest.raises(HanVietRootInUseError):
        service.delete_root(root.id)

    service.unlink_root(word.id, root.id)
    service.delete_root(root.id)

    remaining_roots = session.execute(han_viet_roots.select()).fetchall()
    assert all(row.id != root.id for row in remaining_roots)


@pytest.mark.dictionary
def test_han_viet_create_and_associate(session, make_word):
    word = make_word(viet_word="chính trị", english_translation="politics")
    session.flush()

    service = HanVietService(session)
    created = service.create_and_associate(
        word_id=word.id,
        root="chính",
        chinese_character="政",
        root_meaning="politics",
    )

    associations = session.execute(
        word_han_viet_association.select().where(
            word_han_viet_association.c.word_id == word.id,
            word_han_viet_association.c.root_id == created.id,
        )
    ).fetchall()
    assert len(associations) == 1


@pytest.mark.dictionary
def test_word_service_delete_cascades_associations(
        session, make_word, make_root, make_source, make_example, bind_word_type, bind_word_han_viet
):
    word = make_word(viet_word="nghiên cứu", english_translation="research")
    root = make_root(root="cứu", chinese_character="究", root_meaning="research")
    source = make_source(source_type="book", title="Academic Source", url=None)
    make_example(word.id, source.id, "Tôi nghiên cứu.", "I research.")
    bind_word_type(word.id, "verb")
    bind_word_han_viet(word.id, root.id)
    session.flush()

    service = WordService(session)
    service.delete_entry(word.id)

    repo = HanVietRepository(session)
    assert repo.get_by_id(root.id).root == "cứu"
    assert repo.count_associations(root.id) == 0
