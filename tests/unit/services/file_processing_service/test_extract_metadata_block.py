"""Unit tests for the extract_metadata_block function of the File Processing Service module.

This module contains unit tests for the extract_metadata_block function, which
parses metadata (title, categories, meta description, keywords) from the top of
a markdown blog post and returns the remaining content.

Tests included:
    - test_extract_metadata_all_fields_present: Verifies parsing of all expected metadata.
    - test_extract_metadata_duplicate_field_definitions: Verifies the duplicate metadata fields behavior.
    - test_extract_metadata_empty_keywords: Verifies handling of an empty keywords list.
    - test_extract_metadata_extra_fields_accepted: Verifies that unsupported metadata fields are accepted without error.
    - test_extract_metadata_extra_whitespace: Verifies trimming of whitespace around fields.
    - test_extract_metadata_ignores_case: Verifies that field names are case-insensitive.
    - test_extract_metadata_invalid_field_format: Verifies error handling when metadata lines don't follow
        the "Key: Value" format.
    - test_extract_metadata_missing_block_entirely: Verifies that content without any metadata block raises
        error for missing fields.
    - test_extract_metadata_missing_required_field: Verifies that missing required fields raise errors.
    - test_extract_metadata_non_string_field_values: Verifies behavior when field values are not plain strings.
    - test_extract_metadata_removes_bom: Verifies removal of BOM character from content.
    - test_extract_metadata_trailing_commas_in_keywords: Verifies keywords field handles trailing commas.
"""

import pytest

from app.services.file_processing_service import extract_metadata_block


def test_extract_metadata_all_fields_present() -> None:
    """Verifies parsing of all expected metadata."""
    markdown = """Title: Blog Post
Categories: Python, Web Development
Meta Description: A short summary.
Keywords: python, flask, web

Main content here.
"""
    metadata, content = extract_metadata_block(markdown)

    assert metadata == {
        "title": "Blog Post",
        "categories": ["Python", "Web Development"],
        "meta description": "A short summary.",
        "keywords": ["python", "flask", "web"]
    }
    assert content.startswith("Main content here.")


def test_extract_metadata_duplicate_field_definitions() -> None:
    """Verifies the behavior when duplicate metadata fields are defined.

    The last occurrence of any duplicate metadata field should be silently accepted by overwriting the earlier one
    """
    markdown = """Title: First Title
Title: Second Title
Categories: Python
Meta Description: Summary.
Keywords: design, code

Content goes here.
"""
    metadata, content = extract_metadata_block(markdown)

    assert metadata["title"] == "Second Title"
    assert metadata["categories"] == ["Python"]
    assert metadata["meta description"] == "Summary."
    assert metadata["keywords"] == ["design", "code"]
    assert content.startswith("Content goes here.")


def test_extract_metadata_empty_keywords() -> None:
    """Verifies handling of an empty keywords list."""
    markdown = """Title: Blog
Categories: One, Two
Meta Description: Description here.
Keywords:

Content starts here.
"""
    metadata, content = extract_metadata_block(markdown)

    assert metadata["keywords"] == []
    assert "Content starts here." in content


def test_extract_metadata_extra_fields_ignored() -> None:
    """Verifies that unsupported metadata fields are ignored without error."""
    markdown = """Title: My Post
Categories: Python
Meta Description: Description.
Keywords: one, two
Author: Jane Doe
Reading Time: 5 minutes

Text content here.
"""
    metadata, content = extract_metadata_block(markdown)

    assert "author" in metadata
    assert "reading time" in metadata
    assert metadata["title"] == "My Post"
    assert metadata["categories"] == ["Python"]
    assert metadata["keywords"] == ["one", "two"]
    assert content.startswith("Text content here.")


def test_extract_metadata_extra_whitespace() -> None:
    """Verifies trimming of whitespace around fields."""
    markdown = """Title:   My Post   
Categories:   Python ,  Flask ,   APIs   
Meta Description:   Something about this post.  
Keywords:   design ,   code , clean   

Body content.
"""
    metadata, content = extract_metadata_block(markdown)

    assert metadata["title"] == "My Post"
    assert metadata["categories"] == ["Python", "Flask", "APIs"]
    assert metadata["meta description"] == "Something about this post."
    assert metadata["keywords"] == ["design", "code", "clean"]
    assert content.startswith("Body content.")


def test_extract_metadata_ignores_case() -> None:
    """Verifies that field names are case-insensitive."""
    markdown = """tItLe: Hello World
cAtEgOrIeS: Dev, Testing
MeTa DeScRiPtIoN: Sample
kEyWoRdS: foo, bar

Paragraph text.
"""
    metadata, content = extract_metadata_block(markdown)

    assert metadata["title"] == "Hello World"
    assert metadata["categories"] == ["Dev", "Testing"]
    assert metadata["meta description"] == "Sample"
    assert metadata["keywords"] == ["foo", "bar"]
    assert content.startswith("Paragraph text.")


def test_extract_metadata_invalid_field_format() -> None:
    """Verifies that malformed metadata lines are ignored and result in missing required fields error."""
    markdown = """Title=Invalid Format
Categories: Python
Meta Description: Fine.
Keywords: stuff

Hello world.
"""
    with pytest.raises(ValueError, match="Missing required metadata fields: title"):
        extract_metadata_block(markdown)


def test_extract_metadata_missing_block_entirely() -> None:
    """Verifies that content without any metadata block raises error for missing fields."""
    markdown = """Hello.
This is a post without metadata block.

But it still has good content!
"""
    with pytest.raises(ValueError,
                       match="Missing required metadata fields: title, categories, meta description, keywords"):
        extract_metadata_block(markdown)


def test_extract_metadata_missing_required_field() -> None:
    """Verifies that missing required fields raise errors."""
    incomplete = """Title: Missing Meta
Categories: Python
Keywords: keyword1, keyword2

Rest of the content.
"""
    with pytest.raises(ValueError, match="Missing required metadata fields: meta description"):
        extract_metadata_block(incomplete)


def test_extract_metadata_non_string_field_values() -> None:
    """Verifies behavior when field values are not plain strings (e.g., numeric)."""
    markdown = """Title: 12345
Categories: Data, AI
Meta Description: 9876
Keywords: 1, 2, 3

Content body here.
"""
    metadata, content = extract_metadata_block(markdown)

    assert metadata["title"] == "12345"
    assert metadata["meta description"] == "9876"
    assert metadata["keywords"] == ["1", "2", "3"]
    assert content.startswith("Content body here.")


def test_extract_metadata_removes_bom() -> None:
    """Verifies removal of BOM character from content."""
    markdown = """\ufeffTitle: BOM Title
Categories: Python
Meta Description: Clean start.
Keywords: one, two

## Subtitle
Something here.
"""
    metadata, content = extract_metadata_block(markdown)

    assert metadata["title"] == "BOM Title"
    assert content.startswith("## Subtitle")


def test_extract_metadata_trailing_commas_in_keywords() -> None:
    """Verifies keywords field handles trailing commas."""
    markdown = """Title: Test
Categories: Python
Meta Description: Example post
Keywords: one , two , three,

Main paragraph.
"""
    metadata, content = extract_metadata_block(markdown)

    assert metadata["keywords"] == ["one", "two", "three"]
    assert content.startswith("Main paragraph.")
