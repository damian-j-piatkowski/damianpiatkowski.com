"""Fixtures for seeding dictionary and linguistic entities in tests.

This module provides reusable factories to build deep, relational schema structures
for testing database integrity, services, and API controllers.

Supported Scenarios:
    - Independent creation of words, sources, and Hán Việt semantic particles.
    - Composite association bindings (Word-to-Type and Word-to-Han-Viet-Roots).
    - Citation mappings (linking words to sources via specific example sentences).
    - Bulk bootstrap configurations for quick, end-to-end service testing.
"""

from typing import Callable, Optional

import pytest
from sqlalchemy.orm import Session

from app.domain.dictionary_example import DictionaryExample
from app.domain.dictionary_source import DictionarySource
from app.domain.dictionary_word import DictionaryWord
from app.domain.han_viet_root import HanVietRoot
from app.models.tables.dictionary_example import dictionary_examples
from app.models.tables.dictionary_source import dictionary_sources
# Core table schemas for direct database-level operations
from app.models.tables.dictionary_word import dictionary_words
from app.models.tables.han_viet_root import han_viet_roots
from app.models.tables.word_han_viet_association import word_han_viet_association
from app.models.tables.word_type_association import word_type_association

# ==============================================================================
# 1. CANONICAL DICTIONARY SEED CONSTANTS
# ==============================================================================

CANONICAL_WORDS = [
    {"viet_word": "học tập", "english_translation": "to study / to learn"},
    {"viet_word": "nghiên cứu", "english_translation": "to research / to analyze"},
    {"viet_word": "nhân viên", "english_translation": "employee / staff member"},
]

CANONICAL_ROOTS = [
    {"root": "học", "chinese_character": "學", "root_meaning": "to study / science"},
    {"root": "tập", "chinese_character": "習", "root_meaning": "to practice / habit"},
    {"root": "nhân", "chinese_character": "人", "root_meaning": "person / human"},
    {"root": "viên", "chinese_character": "員", "root_meaning": "member / official"},
]

CANONICAL_SOURCES = [
    {"source_type": "literary", "title": "Truyện Kiều (The Tale of Kieu)", "url": "https://example.com/kieu"},
    {"source_type": "dictionary", "title": "Từ Điển Tiếng Việt", "url": None},
]


# ==============================================================================
# 2. MODULAR FACTORY FIXTURES (WITH FLUSH AND ISOLATED TRANSACTIONS)
# ==============================================================================

@pytest.fixture(scope='function')
def make_word(session: Session) -> Callable[..., DictionaryWord]:
    """Factory to create and insert a standalone DictionaryWord."""

    def _make_word(
            viet_word: str = "tự do",
            english_translation: str = "freedom / liberty"
    ) -> DictionaryWord:
        stmt = dictionary_words.insert().values(
            viet_word=viet_word,
            english_translation=english_translation
        )
        result = session.execute(stmt)
        session.flush()

        inserted_id = result.inserted_primary_key[0]

        row = session.execute(
            dictionary_words.select().where(dictionary_words.c.id == inserted_id)
        ).fetchone()

        word = DictionaryWord(
            word_id=row.id,
            viet_word=row.viet_word,
            english_translation=row.english_translation,
            created_at=row.created_at,
            updated_at=row.updated_at
        )
        word.id = row.id
        return word

    return _make_word


@pytest.fixture(scope='function')
def make_source(session: Session) -> Callable[..., DictionarySource]:
    """Factory to create and insert an authoritative DictionarySource."""

    def _make_source(
            source_type: str = "textbook",
            title: str = "Chuyên đề Ngữ pháp Tiếng Việt",
            url: Optional[str] = "https://example.com/grammar"
    ) -> DictionarySource:
        stmt = dictionary_sources.insert().values(
            source_type=source_type,
            title=title,
            url=url
        )
        result = session.execute(stmt)
        session.flush()

        inserted_id = result.inserted_primary_key[0]

        row = session.execute(
            dictionary_sources.select().where(dictionary_sources.c.id == inserted_id)
        ).fetchone()

        source = DictionarySource(
            source_id=row.id,
            source_type=row.source_type,
            title=row.title,
            url=row.url,
            created_at=row.created_at
        )
        source.id = row.id
        return source

    return _make_source


@pytest.fixture(scope='function')
def make_root(session: Session) -> Callable[..., HanVietRoot]:
    """Factory to create and insert an etymological HanVietRoot."""

    def _make_root(
            root: str = "tự",
            chinese_character: str = "自",
            root_meaning: str = "self / oneself"
    ) -> HanVietRoot:
        stmt = han_viet_roots.insert().values(
            root=root,
            chinese_character=chinese_character,
            root_meaning=root_meaning
        )
        result = session.execute(stmt)
        session.flush()

        inserted_id = result.inserted_primary_key[0]

        row = session.execute(
            han_viet_roots.select().where(han_viet_roots.c.id == inserted_id)
        ).fetchone()

        entity = HanVietRoot(
            root_id=row.id,
            root=row.root,
            chinese_character=row.chinese_character,
            root_meaning=row.root_meaning
        )
        entity.id = row.id
        return entity

    return _make_root


@pytest.fixture(scope='function')
def make_example(session: Session) -> Callable[..., DictionaryExample]:
    """Factory to create a contextual citation linking a word to its origin source."""

    def _make_example(
            word_id: int,
            source_id: int,
            sentence: str = "Tôi yêu tự do.",
            english_translation: str = "I love freedom."
    ) -> DictionaryExample:
        stmt = dictionary_examples.insert().values(
            word_id=word_id,
            source_id=source_id,
            sentence=sentence,
            english_translation=english_translation
        )
        result = session.execute(stmt)
        session.flush()

        inserted_id = result.inserted_primary_key[0]

        row = session.execute(
            dictionary_examples.select().where(dictionary_examples.c.id == inserted_id)
        ).fetchone()

        example = DictionaryExample(
            example_id=row.id,
            word_id=row.word_id,
            source_id=row.source_id,
            sentence=row.sentence,
            english_translation=row.english_translation,
            created_at=row.created_at
        )
        example.id = row.id
        return example

    return _make_example


# ==============================================================================
# 3. ASSOCIATION BINDING FIXTURES (BRIDGE TABLES)
# ==============================================================================

@pytest.fixture(scope='function')
def bind_word_type(session: Session) -> Callable[[int, str], None]:
    """Associates a dictionary word with a specific grammatical type classification."""

    def _bind_word_type(word_id: int, word_type: str) -> None:
        stmt = word_type_association.insert().values(
            word_id=word_id,
            word_type=word_type
        )
        session.execute(stmt)
        session.flush()

    return _bind_word_type


@pytest.fixture(scope='function')
def bind_word_han_viet(session: Session) -> Callable[[int, int], None]:
    """Binds a dictionary word to an etymological Han-Viet semantic root."""

    def _bind_word_han_viet(word_id: int, root_id: int) -> None:
        stmt = word_han_viet_association.insert().values(
            word_id=word_id,
            root_id=root_id
        )
        session.execute(stmt)
        session.flush()

    return _bind_word_han_viet


# ==============================================================================
# 4. COMPREHENSIVE BOOTSTRAP / SEED FIXTURES (FOR RAPID SYSTEM INTEGRATION)
# ==============================================================================

@pytest.fixture(scope='function')
def seed_dictionary(
        make_word,
        make_source,
        make_root,
        make_example,
        bind_word_type,
        bind_word_han_viet
) -> Callable[[], dict]:
    """Seeds a rich relational network of words, types, roots, and cited examples.

    This bootstrap fixture builds highly complex, interconnected testing scenarios
    in a single invocation, returning references to all created domain entities.
    """

    def _seed():
        # 1. Create Sources
        src_kieu = make_source(source_type="literary", title="Truyện Kiều", url="https://example.com/kieu")
        src_dict = make_source(source_type="dictionary", title="Từ Điển Tiếng Việt", url=None)

        # 2. Create Roots
        rt_hoc = make_root(root="học", chinese_character="學", root_meaning="to study")
        rt_tap = make_root(root="tập", chinese_character="習", root_meaning="to practice")
        rt_nhan = make_root(root="nhân", chinese_character="人", root_meaning="person")
        rt_vien = make_root(root="viên", chinese_character="員", root_meaning="member")

        # 3. Create Words
        w_hoc_tap = make_word(viet_word="học tập", english_translation="to study / to learn")
        w_nhan_vien = make_word(viet_word="nhân viên", english_translation="employee")

        # 4. Bind Many-to-Many Han-Viet Associations
        bind_word_han_viet(w_hoc_tap.id, rt_hoc.id)
        bind_word_han_viet(w_hoc_tap.id, rt_tap.id)
        bind_word_han_viet(w_nhan_vien.id, rt_nhan.id)
        bind_word_han_viet(w_nhan_vien.id, rt_vien.id)

        # 5. Bind One-to-Many Word Type Classifications
        bind_word_type(w_hoc_tap.id, "verb")
        bind_word_type(w_nhan_vien.id, "noun")

        # 6. Bind Examples Linked to Specific Source Citations
        ex_1 = make_example(
            word_id=w_hoc_tap.id,
            source_id=src_dict.id,
            sentence="Chúng tôi học tập mỗi ngày.",
            english_translation="We study every day."
        )
        ex_2 = make_example(
            word_id=w_nhan_vien.id,
            source_id=src_kieu.id,
            sentence="Nhân viên ấy rất chăm chỉ.",
            english_translation="That employee is very hard-working."
        )

        return {
            "words": [w_hoc_tap, w_nhan_vien],
            "sources": [src_kieu, src_dict],
            "roots": [rt_hoc, rt_tap, rt_nhan, rt_vien],
            "examples": [ex_1, ex_2]
        }

    return _seed
