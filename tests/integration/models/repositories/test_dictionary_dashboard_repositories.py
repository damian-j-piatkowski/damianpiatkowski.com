"""Integration tests for dictionary dashboard repository aggregates."""

from datetime import datetime, timedelta, timezone

import pytest
from sqlalchemy import update

from app.models.repositories.han_viet_repository import HanVietRepository
from app.models.repositories.source_repository import SourceRepository
from app.models.repositories.word_repository import WordRepository
from app.models.tables.dictionary_word import dictionary_words
from app.models.tables.word_han_viet_association import word_han_viet_association
from app.models.tables.word_type_association import word_type_association


@pytest.mark.dictionary
def test_word_repository_dashboard_counts(session, make_word, make_source, make_example, make_root):
    with_hv = make_word(viet_word="học tập", english_translation="to study")
    without_hv = make_word(viet_word="bàn", english_translation="table")
    compound = make_word(viet_word="nhà cửa", english_translation="housing")
    root = make_root(root="học", chinese_character="學", root_meaning="study")
    session.execute(
        word_han_viet_association.insert().values(word_id=with_hv.id, root_id=root.id)
    )
    session.execute(
        word_type_association.insert().values(word_id=with_hv.id, word_type="verb")
    )
    source = make_source(source_type="book", title="Coverage Book")
    make_example(
        word_id=with_hv.id,
        source_id=source.id,
        sentence="Tôi học tập mỗi ngày.",
        english_translation="I study every day.",
    )
    session.flush()

    words = WordRepository(session)
    assert words.count_words() == 3
    assert words.count_words_with_han_viet() == 1
    assert words.count_words_with_examples() == 1
    assert words.word_type_counts()["verb"] == 1

    missing_examples = {w.viet_word for w in words.list_words_missing_examples()}
    assert "bàn" in missing_examples
    assert "nhà cửa" in missing_examples

    missing_types = {w.viet_word for w in words.list_words_missing_types()}
    assert "bàn" in missing_types

    compounds = {w.viet_word for w in words.list_multi_syllable_without_han_viet()}
    assert "nhà cửa" in compounds
    assert "học tập" not in compounds


@pytest.mark.dictionary
def test_word_velocity_buckets(session, make_word):
    now = datetime.now(timezone.utc)
    recent = make_word(viet_word="mới", english_translation="new")
    older = make_word(viet_word="cũ", english_translation="old")
    session.execute(
        update(dictionary_words)
        .where(dictionary_words.c.id == recent.id)
        .values(created_at=now - timedelta(days=1))
    )
    session.execute(
        update(dictionary_words)
        .where(dictionary_words.c.id == older.id)
        .values(created_at=now - timedelta(days=40))
    )
    session.flush()

    words = WordRepository(session)
    buckets = dict(words.count_words_created_by_bucket("30d"))
    assert sum(buckets.values()) >= 1
    assert all(count >= 0 for count in buckets.values())

    with pytest.raises(ValueError):
        words.count_words_created_by_bucket("1y")


@pytest.mark.dictionary
def test_sources_catalog_metrics(session, make_word, make_source, make_example, make_root):
    word_hv = make_word(viet_word="nhân viên", english_translation="employee")
    word_native = make_word(viet_word="ghế", english_translation="chair")
    root = make_root(root="nhân", chinese_character="人", root_meaning="person")
    session.execute(
        word_han_viet_association.insert().values(word_id=word_hv.id, root_id=root.id)
    )
    source = make_source(source_type="article", title="News Desk")
    unused = make_source(source_type="book", title="Unused Book")
    make_example(
        word_id=word_hv.id,
        source_id=source.id,
        sentence="Nhân viên đến sớm.",
        english_translation="The employee arrived early.",
    )
    make_example(
        word_id=word_native.id,
        source_id=source.id,
        sentence="Ghế này đẹp.",
        english_translation="This chair is beautiful.",
    )
    session.flush()

    repo = SourceRepository(session)
    assert repo.count_sources() == 2
    items, total = repo.list_sources_catalog(page=1, per_page=10, sort="citations_desc")
    assert total == 2
    top = next(item for item in items if item["title"] == "News Desk")
    assert top["citation_count"] == 2
    assert top["unique_words_covered"] == 2
    assert top["han_viet_ratio"] == 50.0
    unused_row = next(item for item in items if item["title"] == "Unused Book")
    assert unused_row["citation_count"] == 0

    filtered, filtered_total = repo.list_sources_catalog(
        page=1,
        per_page=10,
        source_type="article",
        title_query="News",
    )
    assert filtered_total == 1
    assert filtered[0]["title"] == "News Desk"


@pytest.mark.dictionary
def test_han_viet_analytics_aggregates(session, make_word, make_root):
    used = make_root(root="học", chinese_character="學", root_meaning="study")
    orphan = make_root(root="tập", chinese_character="習", root_meaning="practice")
    word = make_word(viet_word="học", english_translation="to learn")
    session.execute(
        word_han_viet_association.insert().values(word_id=word.id, root_id=used.id)
    )
    session.flush()

    repo = HanVietRepository(session)
    assert repo.count_roots() == 2
    assert repo.count_distinct_chinese_characters() == 2
    top = repo.list_top_reused_roots(limit=5)
    assert top[0]["root"] == "học"
    assert top[0]["usage_count"] == 1
    orphans = {root.root for root in repo.list_orphan_roots()}
    assert "tập" in orphans
    assert "học" not in orphans
