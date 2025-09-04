"""Unit tests for the `extract_slug_and_title` function in the `sanitization_service` module.

This module contains unit tests for `extract_slug_and_title`, which processes Google Drive
file names into a slug and a formatted title. It ensures correct transformations while
handling various edge cases.

### **Test Cases:**
    - `test_extract_slug_and_title_double_extension`: Ensures only the last extension is removed.
    - `test_extract_slug_and_title_exemplary_case`: Ensures a well-formatted name remains unchanged.
    - `test_extract_slug_and_title_extra_spaces`: Normalizes extra spaces before and after words.
    - `test_extract_slug_and_title_mixed_case`: Ensures slug is lowercase, title is in title case.
    - `test_extract_slug_and_title_multiple_underscores`: Handles multiple underscores correctly.
    - `test_extract_slug_and_title_no_extension`: Processes file names without an extension.
    - `test_extract_slug_and_title_no_prefix_number`: Raises an exception if the prefix is missing.
    - `test_extract_slug_and_title_numbers_in_title`: Ensures numbers are preserved in the title.
"""

import re

import pytest

from app.services.sanitization_service import extract_slug_and_title


@pytest.mark.admin_unpublished_posts
def test_extract_slug_and_title_double_extension() -> None:
    """Tests a file name with multiple extensions to ensure only the last one is removed."""
    # Arrange
    file_name = "11_my_post.tar.gz"

    # Act
    slug, title = extract_slug_and_title(file_name)

    # Assert
    assert slug == "my-post.tar"
    assert title == "My Post.Tar"


@pytest.mark.admin_unpublished_posts
def test_extract_slug_and_title_exemplary_case() -> None:
    """Tests a file name that is already correctly formatted."""
    # Arrange
    file_name = "05-exemplary-post.md"

    # Act
    slug, title = extract_slug_and_title(file_name)

    # Assert
    assert slug == "exemplary-post"
    assert title == "Exemplary Post"


@pytest.mark.admin_unpublished_posts
def test_extract_slug_and_title_extra_spaces() -> None:
    """Tests extraction from a file name with extra spaces before and after words."""
    # Arrange
    file_name = "08_  messy   file  name .md"

    # Act
    slug, title = extract_slug_and_title(file_name)

    # Assert
    assert slug == "messy-file-name"
    assert title == "Messy File Name"


@pytest.mark.admin_unpublished_posts
def test_extract_slug_and_title_mixed_case() -> None:
    """Tests a file name with mixed case to ensure slug is lowercased."""
    # Arrange
    file_name = "09_MiXeD_CaSe.md"

    # Act
    slug, title = extract_slug_and_title(file_name)

    # Assert
    assert slug == "mixed-case"
    assert title == "Mixed Case"


@pytest.mark.admin_unpublished_posts
def test_extract_slug_and_title_multiple_underscores() -> None:
    """Tests extraction from a file name with multiple underscores after the prefix."""
    # Arrange
    file_name = "05_this_is_a_test.md"

    # Act
    slug, title = extract_slug_and_title(file_name)

    # Assert
    assert slug == "this-is-a-test"
    assert title == "This Is A Test"


@pytest.mark.admin_unpublished_posts
def test_extract_slug_and_title_no_extension() -> None:
    """Tests extraction from a file name that has no extension."""
    # Arrange
    file_name = "10_a_title_without_extension"

    # Act
    slug, title = extract_slug_and_title(file_name)

    # Assert
    assert slug == "a-title-without-extension"
    assert title == "A Title Without Extension"


@pytest.mark.admin_unpublished_posts
def test_extract_slug_and_title_no_prefix_number() -> None:
    """Tests that an exception is raised when there is no numeric prefix before `_`."""
    # Arrange
    file_name = "hello_world.md"

    # Act & Assert
    with pytest.raises(ValueError, match=re.escape(
            "Invalid file name format: 'hello_world.md'. Expected a prefix separated by '-'.")):
        extract_slug_and_title(file_name)


@pytest.mark.admin_unpublished_posts
def test_extract_slug_and_title_numbers_in_title() -> None:
    """Tests a title that contains numbers after the prefix."""
    # Arrange
    file_name = "06_2024_review.md"

    # Act
    slug, title = extract_slug_and_title(file_name)

    # Assert
    assert slug == "2024-review"
    assert title == "2024 Review"
