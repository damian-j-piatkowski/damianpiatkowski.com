"""Unit tests for the `sanitize_html` function of the `sanitization_service` module.

This module contains unit tests for the `sanitize_html` function, which is responsible
for sanitizing HTML content by removing dangerous tags and ensuring safe content.

Tests included (in alphabetical order):
    - test_sanitize_html: Verifies basic HTML content sanitization.
    - test_sanitize_html_with_allowed_tags: Verifies preservation of allowed HTML tags.
    - test_sanitize_html_with_code_blocks: Verifies handling of code blocks and inline code.
    - test_sanitize_html_with_empty_string: Verifies empty string handling.
    - test_sanitize_html_with_extra_spaces: Verifies whitespace normalization.
    - test_sanitize_html_with_invalid_html: Verifies invalid HTML structure handling.
    - test_sanitize_html_with_nested_lists: Verifies nested list structure preservation.
    - test_sanitize_html_with_nested_unsafe_tags: Verifies nested unsafe tag removal.
    - test_sanitize_html_with_plain_text: Verifies plain text preservation.
    - test_sanitize_html_with_safe_attributes: Verifies allowed attribute preservation.
    - test_sanitize_html_with_table_structure: Verifies table structure preservation.
    - test_sanitize_html_with_text_formatting: Verifies text formatting tag handling.
    - test_sanitize_html_with_unclosed_tags: Verifies unclosed tag handling.
    - test_sanitize_html_with_unsafe_attributes: Verifies unsafe attribute removal.
    - test_sanitize_html_with_unsafe_tags: Verifies unsafe tag removal.
"""

import pytest

from app.services.sanitization_service import sanitize_html


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
def test_sanitize_html_with_allowed_tags() -> None:
    """Tests that allowed HTML tags are preserved."""
    # Arrange
    content = "<p><b>Hello</b>, <i>world</i>!</p>"

    # Act
    sanitized_content = sanitize_html(content)

    # Assert
    assert sanitized_content == "<p><b>Hello</b>, <i>world</i>!</p>"  # Tags should be preserved


@pytest.mark.admin_upload_blog_posts
def test_sanitize_html_with_code_blocks() -> None:
    """Tests that code blocks and inline code are preserved correctly."""
    # Arrange
    content = """
    <pre><code>def example():
        return True</code></pre>
    <p>Inline <code>code</code> test</p>
    """

    # Act
    sanitized_content = sanitize_html(content)

    # Assert
    assert "<pre><code>" in sanitized_content
    assert "def example():" in sanitized_content
    assert "return True" in sanitized_content
    assert "Inline <code>code</code> test" in sanitized_content


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
def test_sanitize_html_with_nested_lists() -> None:
    """Tests that nested list structures are preserved correctly."""
    # Arrange
    content = """
    <ul>
        <li>Item 1
            <ol>
                <li>Sub-item 1</li>
                <li>Sub-item 2</li>
            </ol>
        </li>
        <li>Item 2</li>
    </ul>
    """

    # Act
    sanitized_content = sanitize_html(content)

    # Assert
    assert "<ul>" in sanitized_content
    assert "<ol>" in sanitized_content
    assert "Sub-item" in sanitized_content
    assert sanitized_content.count("<li>") == 4


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
def test_sanitize_html_with_plain_text() -> None:
    """Tests that plain text is not altered."""
    # Arrange
    content = "Hello, world!"

    # Act
    sanitized_content = sanitize_html(content)

    # Assert
    assert sanitized_content == "Hello, world!"  # Plain text should remain unchanged


@pytest.mark.admin_upload_blog_posts
def test_sanitize_html_with_safe_attributes() -> None:
    """Tests that safe attributes on allowed tags are preserved."""
    # Arrange
    content = '<a href="https://example.com" title="Example">Link</a>'
    content += '<img src="image.jpg" alt="Image" title="Image Title">'

    # Act
    sanitized_content = sanitize_html(content)

    # Assert
    assert 'href="https://example.com"' in sanitized_content
    assert 'title="Example"' in sanitized_content
    assert 'src="image.jpg"' in sanitized_content
    assert 'alt="Image"' in sanitized_content
    assert 'title="Image Title"' in sanitized_content


@pytest.mark.admin_upload_blog_posts
def test_sanitize_html_with_table_structure() -> None:
    """Tests that table structures are preserved correctly."""
    # Arrange
    content = """
    <table>
        <thead>
            <tr><th>Header 1</th><th>Header 2</th></tr>
        </thead>
        <tbody>
            <tr><td>Cell 1</td><td>Cell 2</td></tr>
        </tbody>
    </table>
    """

    # Act
    sanitized_content = sanitize_html(content)

    # Assert
    assert "<table>" in sanitized_content
    assert "<thead>" in sanitized_content
    assert "<tbody>" in sanitized_content
    assert "<tr>" in sanitized_content
    assert "<th>Header" in sanitized_content
    assert "<td>Cell" in sanitized_content


@pytest.mark.admin_upload_blog_posts
def test_sanitize_html_with_text_formatting() -> None:
    """Tests that text formatting tags are preserved correctly."""
    # Arrange
    content = """
    <p><strong>Bold</strong> and <em>italic</em> text</p>
    <p>With <sub>subscript</sub> and <sup>superscript</sup></p>
    """

    # Act
    sanitized_content = sanitize_html(content)

    # Assert
    assert "<strong>Bold</strong>" in sanitized_content
    assert "<em>italic</em>" in sanitized_content
    assert "<sub>subscript</sub>" in sanitized_content
    assert "<sup>superscript</sup>" in sanitized_content


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


@pytest.mark.admin_upload_blog_posts
def test_sanitize_html_with_unsafe_attributes() -> None:
    """Tests that unsafe attributes are removed while preserving the tag."""
    # Arrange
    content = '<a href="javascript:alert(1)" onclick="alert(2)">Link</a>'
    content += '<img src="image.jpg" onerror="alert(3)">'

    # Act
    sanitized_content = sanitize_html(content)

    # Assert
    assert '<a>Link</a>' in sanitized_content  # href is completely removed for javascript: URLs
    assert '<img src="image.jpg">' in sanitized_content
    assert 'javascript:' not in sanitized_content
    assert 'onclick' not in sanitized_content
    assert 'onerror' not in sanitized_content


@pytest.mark.admin_upload_blog_posts
def test_sanitize_html_with_unsafe_tags() -> None:
    """Tests that unsafe HTML tags are removed."""
    # Arrange
    content = "<p>Hello, <iframe src='malicious.com'></iframe>world!</p>"

    # Act
    sanitized_content = sanitize_html(content)

    # Assert
    assert sanitized_content == "<p>Hello, world!</p>"  # <iframe> should be removed
