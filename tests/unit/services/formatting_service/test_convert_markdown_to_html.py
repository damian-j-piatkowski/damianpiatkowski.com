"""Unit tests for the convert_markdown_to_html function of the FormattingService module.

This module contains unit tests for the convert_markdown_to_html function, which
transforms markdown text into HTML.

Tests included:
    - test_convert_markdown_to_html_blockquotes: Verifies conversion of blockquotes.
    - test_convert_markdown_to_html_bullet_list: Verifies conversion of bullet lists.
    - test_convert_markdown_to_html_code_block: Verifies conversion of standalone code blocks.
    - test_convert_markdown_to_html_complex: Verifies conversion of complex content with headings,
        paragraphs, and code blocks.
    - test_convert_markdown_to_html_custom_extensions: Verifies support for custom extensions.
    - test_convert_markdown_to_html_footnotes: Verifies footnotes conversion.
    - test_convert_markdown_to_html_headings_and_paragraphs: Verifies conversion of headings
        and paragraphs.
    - test_convert_markdown_to_html_inline_code: Verifies conversion of inline code blocks.
    - test_convert_markdown_to_html_mixed_content: Verifies handling of mixed markdown content.
    - test_convert_markdown_to_html_multiline_paragraphs: Verifies conversion of multiline
        paragraphs.
    - test_convert_markdown_to_html_tables: Verifies table conversion.
    - test_convert_markdown_to_html_title: Verifies conversion of title content.
    - test_handle_empty_input: Verifies handling of empty input.
    - test_preserve_html_in_markdown: Verifies preservation of HTML within markdown.
"""

from app.services.formatting_service import convert_markdown_to_html


def test_convert_markdown_to_html_blockquotes() -> None:
    """Tests conversion of blockquotes in markdown to HTML."""
    text = (
        "> This is a blockquote.\n"
        "This continues in blockquote.\n"
        "\n"
        "This is regular text.\n"
        "> This is another blockquote."
    )
    expected_html = (
        "<blockquote><p>This is a blockquote.<br/>"
        "This continues in blockquote.</p></blockquote>\n"
        "<p>This is regular text.</p>\n"
        "<blockquote><p>This is another blockquote.</p></blockquote>"
    )
    result_html = convert_markdown_to_html(text)

    # Python-Markdown might use either <br> or <br/> tags depending on the version and configuration
    # Normalize both strings to use the same format before comparison
    normalized_expected = expected_html.replace('<br/>', '<br>')
    normalized_result = result_html.replace('<br/>', '<br>')

    assert ''.join(normalized_result.split()) == ''.join(normalized_expected.split())


def test_convert_markdown_to_html_bullet_list() -> None:
    """Tests conversion of bullet lists in markdown to HTML."""
    text = "- First item\n- Second item\n\nA line after the list."
    expected_html = "<ul><li>First item</li><li>Second item</li></ul><p>A line after the list.</p>"
    assert ''.join(convert_markdown_to_html(text).split()) == ''.join(expected_html.split())


def test_convert_markdown_to_html_code_block() -> None:
    """Tests conversion of standalone code blocks in markdown to HTML."""
    text = "```python\nprint('Hello, World!')\n```"
    html = convert_markdown_to_html(text)

    # Check structural elements are present
    assert 'highlight' in html  # Verify highlight class is present
    assert '<pre>' in html  # Verify preformatted block
    assert '<code>' in html  # Verify code block

    # Check code content is present, accounting for HTML entities
    assert "print" in html
    assert "Hello, World!" in html.replace("&#39;", "'")


def test_convert_markdown_to_html_complex() -> None:
    """Tests conversion of complex markdown content."""
    text = """# Title
Introduction paragraph
```

python
def example():
    return "test"
```
## Subtitle
- List item 1
- List item 2

> Quote here
"""
    html = convert_markdown_to_html(text)

    # Check headers are present with their basic content
    assert ">Title<" in html  # Check header content between tags
    assert ">Subtitle<" in html  # Check subheader content

    # Check structural elements
    assert "highlight" in html  # Code block styling
    assert "<blockquote>" in html  # Quote block
    assert "<ul>" in html  # Unordered list

    # Check content elements
    assert "Introduction paragraph" in html
    assert "List item 1" in html
    assert "List item 2" in html
    assert "Quote here" in html


def test_convert_markdown_to_html_custom_extensions() -> None:
    """Tests conversion with additional custom extensions."""
    markdown = "==highlighted text=="
    html = convert_markdown_to_html(markdown, extensions=['pymdownx.mark'])

    # Check that the marked text is wrapped in both <p> and <mark> tags
    # and verify the content is present
    assert "<p>" in html
    assert "<mark>" in html
    assert "highlighted text" in html
    assert "</mark>" in html
    assert "</p>" in html

    # Verify the overall structure (with spaces removed for comparison)
    assert '<p><mark>highlightedtext</mark></p>' in ''.join(html.split())


def test_convert_markdown_to_html_footnotes() -> None:
    """Tests footnote conversion."""
    text = "Text with footnote[^1]\n\n[^1]: Footnote content"
    html = convert_markdown_to_html(text)
    assert 'class="footnote"' in html
    assert "Footnote content" in html


def test_convert_markdown_to_html_headings_and_paragraphs() -> None:
    """Tests conversion of markdown with headings and paragraphs to HTML."""
    text = "# Main Title\nSome introductory text.\n## Subtitle\nMore content here."
    html = convert_markdown_to_html(text)

    # Check the basic structure and content
    assert ">Main Title<" in html  # Header content
    assert ">Some introductory text.<" in html  # First paragraph
    assert ">Subtitle<" in html  # Subheader content
    assert ">More content here.<" in html  # Second paragraph

    # Verify header hierarchy
    assert "<h1" in html and "</h1>" in html  # Main header tags
    assert "<h2" in html and "</h2>" in html  # Sub header tags

    # Verify paragraphs
    assert html.count("<p>") == 2  # Two paragraphs
    assert html.count("</p>") == 2


def test_convert_markdown_to_html_inline_code() -> None:
    """Tests conversion of inline code in markdown to HTML."""
    text = "Here is some `inline code` in the middle of a sentence."
    expected_html = "<p>Here is some <code>inline code</code> in the middle of a sentence.</p>"
    assert ''.join(convert_markdown_to_html(text).split()) == ''.join(expected_html.split())


def test_convert_markdown_to_html_mixed_content() -> None:
    """Tests conversion of mixed content including headings, lists, and paragraphs to HTML."""
    text = "# Title\nIntro text\n\n- Item one\n- Item two\n\n## Subtitle\nRegular text."
    html = convert_markdown_to_html(text)

    # Check content presence
    assert "Title" in html
    assert "Intro text" in html
    assert "Item one" in html
    assert "Item two" in html
    assert "Subtitle" in html
    assert "Regular text" in html

    # Check structure
    assert html.count("<h1") == 1  # One main heading
    assert html.count("</h1>") == 1
    assert html.count("<h2") == 1  # One subheading
    assert html.count("</h2>") == 1
    assert html.count("<p>") == 2  # Two paragraphs
    assert html.count("</p>") == 2
    assert html.count("<ul>") == 1  # One unordered list
    assert html.count("</ul>") == 1
    assert html.count("<li>") == 2  # Two list items
    assert html.count("</li>") == 2

    # Check order of main elements (using index comparisons)
    h1_pos = html.find("<h1")
    p1_pos = html.find("<p>")
    ul_pos = html.find("<ul>")
    h2_pos = html.find("<h2")
    assert h1_pos < p1_pos < ul_pos < h2_pos  # Verify correct order


def test_convert_markdown_to_html_multiline_paragraphs() -> None:
    """Tests conversion of multiple paragraphs in markdown to HTML."""
    text = "This is the first paragraph.\n\nThis is the second paragraph."
    expected_html = "<p>This is the first paragraph.</p><p>This is the second paragraph.</p>"
    assert ''.join(convert_markdown_to_html(text).split()) == ''.join(expected_html.split())


def test_convert_markdown_to_html_tables() -> None:
    """Tests table conversion."""
    text = """
| Header 1 | Header 2 |
|----------|----------|
| Cell 1   | Cell 2   |
"""
    html = convert_markdown_to_html(text)

    # Check basic table structure
    assert "<table>" in html
    assert "</table>" in html
    assert "<thead>" in html
    assert "</thead>" in html
    assert "<tbody>" in html
    assert "</tbody>" in html

    # Check headers (accounting for whitespace trimming)
    assert ">Header 1<" in html
    assert ">Header 2<" in html

    # Check cells (accounting for whitespace trimming)
    assert ">Cell 1<" in html
    assert ">Cell 2<" in html

    # Verify table structure order
    thead_pos = html.find("<thead>")
    tbody_pos = html.find("<tbody>")
    assert thead_pos < tbody_pos  # Headers should come before body

    # Verify row structure
    assert html.count("<tr>") == 2  # One row for headers, one for cells
    assert html.count("</tr>") == 2
    assert html.count("<th>") == 2  # Two header cells
    assert html.count("</th>") == 2
    assert html.count("<td>") == 2  # Two data cells
    assert html.count("</td>") == 2


def test_convert_markdown_to_html_title() -> None:
    """Tests conversion of blog post title with quotes and special characters."""
    markdown = """# Six Essential Object-Oriented Design Principles from Matthias Noback's "Object Design Style Guide"\n\nThe concept of transferable skills..."""
    html = convert_markdown_to_html(markdown)

    # Check title structure
    assert html.count("<h1") == 1
    assert html.count("</h1>") == 1

    # Check title content is preserved
    assert "Six Essential Object-Oriented Design Principles" in html
    assert "Noback" in html
    assert "Object Design Style Guide" in html

    # Check smart quotes conversion
    assert "&rsquo;s" in html  # Proper apostrophe
    assert "&ldquo;" in html or "&quot;" in html  # Opening quote
    assert "&rdquo;" in html or "&quot;" in html  # Closing quote


def test_handle_empty_input() -> None:
    """Tests handling of empty input."""
    assert convert_markdown_to_html("") == ""
    assert convert_markdown_to_html("\n") == ""


def test_preserve_html_in_markdown() -> None:
    """Tests preservation of HTML within markdown."""
    text = "# Title\n\n<div class='custom'>Content</div>"
    html = convert_markdown_to_html(text)

    # Check title content and structure
    assert ">Title<" in html
    assert html.count("<h1") == 1
    assert html.count("</h1>") == 1

    # Check preserved HTML div content and structure
    assert "class=" in html  # Check attribute presence
    assert "custom" in html  # Check attribute value
    assert ">Content<" in html  # Check div content
    assert html.count("<div") == 1  # Check div tag presence
    assert html.count("</div>") == 1

    # Verify order
    h1_pos = html.find("<h1")
    div_pos = html.find("<div")
    assert h1_pos < div_pos  # Title should come before the custom div

    # Verify preserved HTML structure (handling both quote types)
    normalized_html = (html.replace("'", '"')  # Normalize quotes
                       .replace(" ", "")  # Remove spaces
                       .replace("\n", ""))  # Remove newlines

    assert any(div in normalized_html for div in [
        '<divclass="custom">Content</div>',
        '<divclass=\'custom\'>Content</div>'
    ])
