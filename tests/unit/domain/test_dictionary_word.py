"""Unit tests for the DictionaryWord domain model.

These tests verify the correct initialization, aggregate property calculations,
and attribute mapping of DictionaryWord instances. They ensure that exposure level
computations, aggregate list fallbacks, and multi-accented properties remain structurally sound.

Scenarios included:
    - Ensure a transient DictionaryWord instance initializes cleanly with default empty aggregates.
    - Ensure a fully hydrated DictionaryWord correctly maps arrays of examples and semantic roots.
    - Ensure the 'level' property accurately calculates and caps the volume level up to 4.
    - Ensure the 'has_han_viet' property evaluates flags correctly based on aggregate presence.
    - Ensure edge case payload states are processed through parametrization without modification.
"""

import datetime
from typing import Optional

import pytest

from app.domain.dictionary_example import DictionaryExample
from app.domain.dictionary_word import DictionaryWord
from app.domain.han_viet_root import HanVietRoot


@pytest.mark.dictionary
def test_dictionary_word_transient_initialization_defaults() -> None:
    """Verifies that a new transient DictionaryWord handles default fallback parameters correctly.

    This scenario guarantees that empty arrays are established for dependent aggregates,
    and that identity keys or timestamp limits default gracefully to None.
    """
    # Arrange & Act
    word_entry = DictionaryWord(
        word_id=None,
        viet_word="báo cáo",
        english_translation="to report; a report"
    )

    # Assert
    assert word_entry.id is None
    assert word_entry.viet_word == "báo cáo"
    assert word_entry.english_translation == "to report; a report"
    assert word_entry.examples == []
    assert word_entry.han_viet_roots == []
    assert word_entry.created_at is None
    assert word_entry.updated_at is None


@pytest.mark.dictionary
def test_dictionary_word_hydrated_initialization_with_aggregates() -> None:
    """Verifies that a fully hydrated DictionaryWord entity maps nested aggregate collections.

    This scenario validates that complex structural domain relations, timezone-aware stamps,
    and lookup values link flawlessly to runtime instance properties.
    """
    # Arrange
    static_time_created = datetime.datetime(2026, 7, 10, 12, 0, tzinfo=datetime.timezone.utc)
    static_time_updated = datetime.datetime(2026, 7, 10, 12, 5, tzinfo=datetime.timezone.utc)

    mock_example = DictionaryExample(
        example_id=504,
        word_id=201,
        source_id=14,
        sentence="Doraemon và nhóm bạn càng lúc càng gay cấn.",
        english_translation="Doraemon and his friends are getting more thrilling.",
        created_at=static_time_created
    )

    mock_root = HanVietRoot(
        root_id=42,
        root="bản",
        chinese_character="本",
        root_meaning="root, basis"
    )

    # Act
    word_entry = DictionaryWord(
        word_id=201,
        viet_word="báo cáo",
        english_translation="to report; a report",
        examples=[mock_example],
        han_viet_roots=[mock_root],
        created_at=static_time_created,
        updated_at=static_time_updated
    )

    # Assert
    assert word_entry.id == 201
    assert word_entry.viet_word == "báo cáo"
    assert len(word_entry.examples) == 1
    assert word_entry.examples[0].id == 504
    assert len(word_entry.han_viet_roots) == 1
    assert word_entry.han_viet_roots[0].root == "bản"
    assert word_entry.created_at == static_time_created
    assert word_entry.updated_at == static_time_updated


@pytest.mark.dictionary
@pytest.mark.parametrize(
    "example_count,expected_level",
    [
        (0, 0),
        (1, 1),
        (3, 3),
        (4, 4),
        (5, 4),  # Cap validation limit
        (12, 4),  # Upper boundary check
    ],
    ids=["zero_examples", "one_example", "three_examples", "exact_cap", "exceed_cap_by_one", "extreme_count"]
)
def test_dictionary_word_level_computation(example_count: int, expected_level: int) -> None:
    """Verifies that the Kaufmann-style exposure level property scales logically and caps at 4.

    This scenario confirms that user progression scoring remains locked to system constraints
    regardless of extreme exposure sample accumulation.
    """
    # Arrange
    mock_time = datetime.datetime(2026, 1, 1, 0, 0, tzinfo=datetime.timezone.utc)
    mock_examples = [
        DictionaryExample(
            example_id=i, word_id=1, source_id=1, sentence="...", english_translation="...", created_at=mock_time
        )
        for i in range(example_count)
    ]

    word_entry = DictionaryWord(
        word_id=1,
        viet_word="test",
        english_translation="test",
        examples=mock_examples
    )

    # Act & Assert
    assert word_entry.level == expected_level


@pytest.mark.dictionary
def test_dictionary_word_has_han_viet_evaluation() -> None:
    """Verifies that the has_han_viet evaluation switch switches accurately based on aggregate presence."""
    # Arrange
    word_without_roots = DictionaryWord(word_id=1, viet_word="abc", english_translation="xyz", han_viet_roots=[])

    mock_root = HanVietRoot(root_id=1, root="học", chinese_character="學", root_meaning="study")
    word_with_roots = DictionaryWord(word_id=2, viet_word="học", english_translation="to study",
                                     han_viet_roots=[mock_root])

    # Act & Assert
    assert word_without_roots.has_han_viet is False
    assert word_with_roots.has_han_viet is True


@pytest.mark.dictionary
@pytest.mark.parametrize(
    "word_id,viet_word,english_translation",
    [
        (0, "đường", "sugar; street, road"),
        (-5, "nghiệm", "to test, examine, verify"),
        (99999, " ", "   "),
    ],
    ids=["zero_id_multi_meaning", "negative_id_complex_diacritics", "large_id_whitespace_bounds"]
)
def test_dictionary_word_parameterized_edge_cases(
        word_id: Optional[int],
        viet_word: str,
        english_translation: str
) -> None:
    """Verifies that parameterized boundary text payloads match instance specifications without errors."""
    # Act
    word_entry = DictionaryWord(
        word_id=word_id,
        viet_word=viet_word,
        english_translation=english_translation
    )

    # Assert
    assert word_entry.id == word_id
    assert word_entry.viet_word == viet_word
    assert word_entry.english_translation == english_translation
