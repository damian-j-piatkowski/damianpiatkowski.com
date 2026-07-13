"""Unit tests for the DictionaryExample domain model.

These tests verify the correct initialization, attribute mapping, and structural
hydration properties of DictionaryExample instances, ensuring that parallel text tokens,
localization constraints, and entity relationships function flawlessly at the domain boundary.

Scenarios included:
    - Ensure an unhydrated DictionaryExample instance initializes correctly with a valid database ID.
    - Ensure a new transient DictionaryExample instance handles a None value for its identifier.
    - Ensure a fully hydrated representation accurately maps the attached DictionarySource domain entity.
    - Ensure various boundary payloads, multi-accented strings, and timing configurations map via parametrization.
"""

import datetime
from typing import Optional

import pytest

from app.domain.dictionary_example import DictionaryExample
from app.domain.dictionary_source import DictionarySource
from app.domain.domain_enums import SourceType


@pytest.mark.dictionary
def test_dictionary_example_unhydrated_initialization_with_id() -> None:
    """Verifies that a DictionaryExample instance initializes accurately in its unhydrated state.

    This scenario ensures that persistence database locks, structural relation IDs,
    parallel text strings, and baseline timestamp mixins are cleanly bound to target elements.
    """
    # Arrange & Act
    fixed_timestamp = datetime.datetime(2026, 7, 6, 15, 2, 49, tzinfo=datetime.timezone.utc)
    example_entry = DictionaryExample(
        example_id=504,
        word_id=88,
        source_id=14,
        sentence="Doraemon và nhóm bạn càng lúc càng gay cấn, các em đừng bỏ lỡ nhé!",
        english_translation="The adventures of Doraemon and his friends are getting more thrilling by the minute; don't miss out, kids!",
        created_at=fixed_timestamp,
        source=None
    )

    # Assert
    assert example_entry.id == 504
    assert example_entry.word_id == 88
    assert example_entry.source_id == 14
    assert example_entry.sentence == "Doraemon và nhóm bạn càng lúc càng gay cấn, các em đừng bỏ lỡ nhé!"
    assert example_entry.english_translation == "The adventures of Doraemon and his friends are getting more thrilling by the minute; don't miss out, kids!"
    assert example_entry.created_at == fixed_timestamp
    assert example_entry.source is None


@pytest.mark.dictionary
def test_dictionary_example_transient_initialization_without_id() -> None:
    """Verifies that a transient DictionaryExample instance initializes correctly with a None identifier.

    This scenario guarantees that mining pipelines and dynamic submission inputs can safely construct
    domain models before committing rows to the physical storage layer.
    """
    # Arrange & Act
    current_time = datetime.datetime.now(datetime.timezone.utc)
    transient_example = DictionaryExample(
        example_id=None,
        word_id=42,
        source_id=7,
        sentence="Học, học nữa, học mãi.",
        english_translation="Study, study more, study forever.",
        created_at=current_time,
        source=None
    )

    # Assert
    assert transient_example.id is None
    assert transient_example.word_id == 42
    assert transient_example.source_id == 7
    assert transient_example.sentence == "Học, học nữa, học mãi."
    assert transient_example.english_translation == "Study, study more, study forever."
    assert transient_example.created_at == current_time
    assert transient_example.source is None


@pytest.mark.dictionary
def test_dictionary_example_fully_hydrated_initialization() -> None:
    """Verifies that a DictionaryExample instance maps an explicitly nested DictionarySource entity.

    This scenario ensures that joined query pipelines hydra-load contextual source parameters
    and keep domain model relationship rules perfectly intact.
    """
    # Arrange
    fixed_timestamp = datetime.datetime(2026, 7, 6, 15, 2, 49, tzinfo=datetime.timezone.utc)
    mock_source = DictionarySource(
        source_id=14,
        source_type=SourceType.MANGA,
        title="Doraemon Tập 1",
        created_at=fixed_timestamp
    )

    # Act
    hydrated_example = DictionaryExample(
        example_id=504,
        word_id=88,
        source_id=14,
        sentence="Doraemon và nhóm bạn càng lúc càng gay cấn, các em đừng bỏ lỡ nhé!",
        english_translation="The adventures of Doraemon and his friends are getting more thrilling by the minute; don't miss out, kids!",
        created_at=fixed_timestamp,
        source=mock_source
    )

    # Assert
    assert hydrated_example.source is not None
    assert hydrated_example.source.id == 14
    assert hydrated_example.source.source_type == "manga"
    assert hydrated_example.source.title == "Doraemon Tập 1"
    assert hydrated_example.source_id == hydrated_example.source.id


@pytest.mark.dictionary
@pytest.mark.parametrize(
    "example_id,word_id,source_id,sentence,english_translation",
    [
        # Case 1: Zero testing boundary values for IDs
        (0, 0, 0, "Từ này có nghĩa gì?", "What does this word mean?"),

        # Case 2: Negative ID boundaries
        (-1, -100, -5, "Tôi không hiểu.", "I do not understand."),

        # Case 3: Complex combining diacritics and tones (utf8mb4_unicode_ci target)
        (777, 888, 999, "Đường đi gập ghềnh hiểm trở vô cùng.", "The path is incredibly bumpy and dangerous."),

        # Case 4: Empty structures / raw whitespace constraints
        (12, 34, 56, "", "   "),

        # Case 5: Long descriptive sentence translation layout strings
        (
                1001, 2002, 3003,
                "Trải qua bao nhiêu thăng trầm lịch sử, tiếng nói của chúng ta vẫn giữ được bản sắc dân tộc độc đáo.",
                "Having passed through countless historical ups and downs, our spoken language still beautifully maintains its highly unique national identity."
        ),
    ],
    ids=[
        "zero_ids",
        "negative_ids",
        "complex_diacritics_and_tones",
        "empty_and_whitespace_blocks",
        "long_parallel_text_strings"
    ]
)
def test_dictionary_example_parameterized_edge_cases(
        example_id: Optional[int],
        word_id: int,
        source_id: int,
        sentence: str,
        english_translation: str
) -> None:
    """Verifies that parameterized boundary strings and numbers map correctly to runtime instances.

    This scenario validates localization character compliance, extreme text boundaries,
    and system numbers to prove constructors never mutate raw input criteria.
    """
    # Arrange
    static_time = datetime.datetime(2026, 1, 1, 0, 0, 0, tzinfo=datetime.timezone.utc)

    # Act
    example_entry = DictionaryExample(
        example_id=example_id,
        word_id=word_id,
        source_id=source_id,
        sentence=sentence,
        english_translation=english_translation,
        created_at=static_time,
        source=None
    )

    # Assert
    assert example_entry.id == example_id
    assert example_entry.word_id == word_id
    assert example_entry.source_id == source_id
    assert example_entry.sentence == sentence
    assert example_entry.english_translation == english_translation
    assert example_entry.created_at == static_time
