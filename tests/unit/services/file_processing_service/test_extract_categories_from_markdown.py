"""Unit tests for the extract_categories_from_markdown function of the FileProcessingService module.

This module contains unit tests for the extract_categories_from_markdown function, which
extracts categories from the first line of markdown content and returns the remaining content.

Tests included:
    - test_extract_categories_basic_single_category: Verifies extraction of a single category.
    - test_extract_categories_empty_categories: Verifies handling of empty category list.
    - test_extract_categories_multiple_categories: Verifies extraction of multiple categories.
    - test_extract_categories_multiple_newlines_after_header: Verifies handling of multiple newlines after category header.
    - test_extract_categories_removes_bom: Verifies removal of BOM character from content.
    - test_extract_categories_single_line_no_newline: Verifies error handling for content without newlines.
    - test_extract_categories_trailing_commas: Verifies handling of trailing commas in category list.
    - test_extract_categories_whitespace_handling: Verifies proper whitespace trimming in categories and content.
    - test_extract_categories_wrong_first_line: Verifies error handling for incorrect first line format.
"""

import pytest

from app.services.file_processing_service import extract_categories_from_markdown


def test_extract_categories_basic_single_category() -> None:
    """Verifies extraction of a single category."""
    markdown = "Categories: python\n\n# Blog Post Title\nContent here."
    categories, content = extract_categories_from_markdown(markdown)

    assert categories == ["python"]
    assert content == "# Blog Post Title\nContent here."


def test_extract_categories_empty_categories() -> None:
    """Verifies handling of empty category list."""
    markdown = "Categories:\n\n# Title\nContent"
    categories, content = extract_categories_from_markdown(markdown)

    assert categories == []
    assert content == "# Title\nContent"


def test_extract_categories_multiple_categories() -> None:
    """Verifies extraction of multiple categories."""
    markdown = "Categories: python, web development, flask\n\n# Blog Post\nContent here."
    categories, content = extract_categories_from_markdown(markdown)

    assert categories == ["python", "web development", "flask"]
    assert content == "# Blog Post\nContent here."


def test_extract_categories_multiple_newlines_after_header() -> None:
    """Verifies handling of multiple newlines after category header."""
    markdown = "Categories: python\n\n\n\n# Title\nContent"
    categories, content = extract_categories_from_markdown(markdown)

    assert categories == ["python"]
    assert content == "# Title\nContent"


def test_extract_categories_removes_bom() -> None:
    """Verifies removal of BOM character from content."""
    markdown_with_bom = "\ufeffCategories: python\n\n# Title\nContent"
    categories, content = extract_categories_from_markdown(markdown_with_bom)

    assert categories == ["python"]
    assert content == "# Title\nContent"


def test_extract_categories_single_line_no_newline() -> None:
    """Verifies error handling for content without newlines."""
    markdown = "Categories: python"

    with pytest.raises(ValueError, match="Markdown must start with 'Categories:' followed by a newline"):
        extract_categories_from_markdown(markdown)


def test_extract_categories_trailing_commas() -> None:
    """Verifies handling of trailing commas in category list."""
    markdown = "Categories: python, web development,\n\nContent"
    categories, content = extract_categories_from_markdown(markdown)

    assert categories == ["python", "web development"]
    assert content == "Content"


def test_extract_categories_whitespace_handling() -> None:
    """Verifies proper whitespace trimming in categories and content."""
    markdown = "Categories:  python  ,   web development   ,  flask  \n\n   # Title\n   Content"
    categories, content = extract_categories_from_markdown(markdown)

    assert categories == ["python", "web development", "flask"]
    assert content == "# Title\n   Content"


def test_extract_categories_wrong_first_line() -> None:
    """Verifies error handling for incorrect first line format."""
    markdown_no_categories = "# Title\n\nContent here"
    markdown_wrong_prefix = "Tags: python\n\nContent here"

    with pytest.raises(ValueError, match="First line must start with 'Categories:'"):
        extract_categories_from_markdown(markdown_no_categories)

    with pytest.raises(ValueError, match="First line must start with 'Categories:'"):
        extract_categories_from_markdown(markdown_wrong_prefix)
