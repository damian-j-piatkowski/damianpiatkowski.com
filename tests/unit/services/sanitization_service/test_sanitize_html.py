"""Unit tests for the `sanitize_html` function of the `sanitization_service` module.

This module contains unit tests for the `sanitize_html` function, which is responsible
for sanitizing HTML content by removing dangerous tags and ensuring safe content.

Tests included:
    - test_sanitize_html: Verifies that dangerous tags are removed from HTML content.
    - test_sanitize_html_with_empty_string: Verifies that empty strings are handled correctly.
    - test_sanitize_html_with_plain_text: Verifies that plain text is not altered.
    - test_sanitize_html_with_allowed_tags: Verifies that allowed HTML tags are preserved.
    - test_sanitize_html_with_unsafe_tags: Verifies that unsafe HTML tags are removed.
    - test_sanitize_html_with_nested_unsafe_tags: Verifies that nested unsafe HTML tags are
        sanitized.
    - test_sanitize_html_with_invalid_html: Verifies that invalid HTML structures are sanitized
        properly.
    - test_sanitize_html_with_extra_spaces: Verifies that extra spaces are handled correctly.
    - test_sanitize_html_with_unclosed_tags: Verifies that unclosed tags are handled properly.
"""

from app.services.sanitization_service import sanitize_html
import pytest

@pytest.mark.admin_upload_blog_posts
def test_sanitize_html() -> None:
    """Tests that HTML content is sanitized by removing dangerous tags."""
    # Arrange
    content = "<p><b>Hello</b>, <i>world</i>! <script>alert('XSS');</script></p>"

    # Act
    sanitized_content = sanitize_html(content)

    # Assert
    assert sanitized_content == "<p><b>Hello</b>, <i>world</i>!</p>"  # Script tag should be removed


@pytest.mark.admin_upload_blog_posts
def test_sanitize_html_with_empty_string() -> None:
    """Tests that an empty string is handled correctly."""
    # Arrange
    content = ""

    # Act
    sanitized_content = sanitize_html(content)

    # Assert
    assert sanitized_content == ""  # Should return an empty string


@pytest.mark.admin_upload_blog_posts
def test_sanitize_html_with_plain_text() -> None:
    """Tests that plain text is not altered."""
    # Arrange
    content = "Hello, world!"

    # Act
    sanitized_content = sanitize_html(content)

    # Assert
    assert sanitized_content == "Hello, world!"  # Plain text should remain unchanged


@pytest.mark.admin_upload_blog_posts
def test_sanitize_html_with_allowed_tags() -> None:
    """Tests that allowed HTML tags are preserved."""
    # Arrange
    content = "<p><b>Hello</b>, <i>world</i>!</p>"

    # Act
    sanitized_content = sanitize_html(content)

    # Assert
    assert sanitized_content == "<p><b>Hello</b>, <i>world</i>!</p>"  # Tags should be preserved


@pytest.mark.admin_upload_blog_posts
def test_sanitize_html_with_unsafe_tags() -> None:
    """Tests that unsafe HTML tags are removed."""
    # Arrange
    content = "<p>Hello, <iframe src='malicious.com'></iframe>world!</p>"

    # Act
    sanitized_content = sanitize_html(content)

    # Assert
    assert sanitized_content == "<p>Hello, world!</p>"  # <iframe> should be removed


@pytest.mark.admin_upload_blog_posts
def test_sanitize_html_with_nested_unsafe_tags() -> None:
    """Tests that nested unsafe HTML tags are sanitized."""
    # Arrange
    content = "<p><b>Hello</b> <script>alert('XSS');</script>, <i>world</i>!</p>"

    # Act
    sanitized_content = sanitize_html(content)

    # Assert
    assert sanitized_content == "<p><b>Hello</b>, <i>world</i>!</p>"  # Script should be removed


@pytest.mark.admin_upload_blog_posts
def test_sanitize_html_with_invalid_html() -> None:
    """Tests that invalid HTML structures are sanitized properly."""
    # Arrange
    content = "<p><b>Hello <i>world!</b></p>"

    # Act
    sanitized_content = sanitize_html(content)

    # Assert
    # Invalid nesting should be fixed by bleach
    assert sanitized_content == "<p><b>Hello <i>world!</i></b></p>"


@pytest.mark.admin_upload_blog_posts
def test_sanitize_html_with_extra_spaces() -> None:
    """Tests that extra spaces are handled correctly."""
    # Arrange
    content = "<p>  <b>Hello</b>, <i>world</i>!  </p>"

    # Act
    sanitized_content = sanitize_html(content)

    # Assert
    # Extra spaces inside tags should be handled
    assert sanitized_content == "<p><b>Hello</b>, <i>world</i>!</p>"


@pytest.mark.admin_upload_blog_posts
def test_sanitize_html_with_unclosed_tags() -> None:
    """Tests that unclosed tags are handled properly."""
    # Arrange
    content = "<p><b>Hello, <i>world!</p>"

    # Act
    sanitized_content = sanitize_html(content)

    # Assert
    # Bleach should close unclosed tags
    assert sanitized_content == "<p><b>Hello, <i>world!</i></b></p>"
