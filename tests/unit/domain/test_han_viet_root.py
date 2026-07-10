"""Unit tests for the HanVietRoot domain model.

These tests verify the correct initialization and attribute handling of
HanVietRoot instances, ensuring that semantic sub-word attributes and optional database
identifiers are properly assigned at the domain boundary.

Scenarios included:
    - Ensure a HanVietRoot instance is initialized correctly with a valid database ID.
    - Ensure a new transient HanVietRoot instance handles a None value for its identifier.
    - Ensure various edge case configurations and string boundaries map cleanly via parametrization.
"""

from typing import Optional
import pytest
from app.domain.han_viet_root import HanVietRoot


@pytest.mark.dictionary
def test_han_viet_root_initialization_with_id() -> None:
    """Verifies that a HanVietRoot instance is initialized with all expected properties.

    This scenario ensures that database identity anchors, Vietnamese strings, Chinese characters,
    and translation strings are properly assigned and exposed via standard attributes.
    """
    # Arrange & Act
    root_entry = HanVietRoot(
        root_id=42,
        root="bản",
        chinese_character="本",
        root_meaning="root, basis, foundation"
    )

    # Assert
    assert root_entry.id == 42
    assert root_entry.root == "bản"
    assert root_entry.chinese_character == "本"
    assert root_entry.root_meaning == "root, basis, foundation"


@pytest.mark.dictionary
def test_han_viet_root_transient_initialization_without_id() -> None:
    """Verifies that a new transient HanVietRoot instance initializes with a None identifier.

    This scenario ensures that business logic domains can instantiate new objects safely before
    they are written to the database engine or storage layer.
    """
    # Arrange & Act
    transient_root = HanVietRoot(
        root_id=None,
        root="học",
        chinese_character="學",
        root_meaning="to learn, study"
    )

    # Assert
    assert transient_root.id is None
    assert transient_root.root == "học"
    assert transient_root.chinese_character == "學"
    assert transient_root.root_meaning == "to learn, study"


@pytest.mark.dictionary
@pytest.mark.parametrize(
    "root_id,root,chinese_character,root_meaning",
    [
        # Case 1: Zero testing boundary
        (0, "sinh", "生", "to be born, life"),

        # Case 2: Negative ID testing boundary
        (-1, "tử", "死", "to die, death"),

        # Case 3: Complex combining diacritics in Vietnamese script
        (105, "nghiệm", "驗", "to test, examine, verify"),

        # Case 4: Empty string values / trailing whitespaces
        (202, "", " ", "  "),

        # Case 5: Long descriptive text values for meaning blocks
        (303, "quốc", "國", "country, nation, state; relating to a national entity or territory"),
    ],
    ids=[
        "zero_id",
        "negative_id",
        "complex_diacritics",
        "empty_and_whitespace_strings",
        "long_meaning_text"
    ]
)
def test_han_viet_root_parameterized_edge_cases(
    root_id: Optional[int],
    root: str,
    chinese_character: str,
    root_meaning: str
) -> None:
    """Verifies that parameterized edge case payloads map accurately to internal instance variables.
    
    This scenario tests boundary numbers, multi-accented character maps, whitespace tokens, 
    and long strings to guarantee the initializer handles structural variance without modification.
    """
    # Act
    root_entry = HanVietRoot(
        root_id=root_id,
        root=root,
        chinese_character=chinese_character,
        root_meaning=root_meaning
    )

    # Assert
    assert root_entry.id == root_id
    assert root_entry.root == root
    assert root_entry.chinese_character == chinese_character
    assert root_entry.root_meaning == root_meaning