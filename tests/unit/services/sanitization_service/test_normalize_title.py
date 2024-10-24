"""Unit tests for the `normalize_title` function of the `sanitization_service` module.

This module contains unit tests for the `normalize_title` function, which is responsible
for normalizing titles by stripping certain prefixes and ensuring correct format.

Tests included:
    - test_normalize_title_with_prefix: Verifies that title prefixes are correctly stripped.
    - test_normalize_title_with_invalid_format: Verifies that an exception is raised for titles
        without a valid prefix.
"""

import pytest

from app.services.sanitization_service import normalize_title


def test_normalize_title_with_prefix() -> None:
    """Tests that the title prefix is correctly stripped."""
    # Arrange
    title = "01_Hello_World"

    # Act
    normalized_title = normalize_title(title)

    # Assert
    assert normalized_title == "Hello_World"


def test_normalize_title_with_invalid_format() -> None:
    """Tests that an exception is raised for titles without a prefix."""
    # Arrange
    title = "HelloWorld"  # No '_' in the title

    # Act & Assert
    with pytest.raises(ValueError, match="Invalid title format: 'HelloWorld'"):
        normalize_title(title)
