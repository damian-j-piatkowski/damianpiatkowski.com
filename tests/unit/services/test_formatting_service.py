"""Unit tests for the convert_markdown_to_html function of the FormattingService module.

This module contains unit tests for the convert_markdown_to_html function, which
transforms markdown text into HTML.

Tests included:
    - test_convert_markdown_to_html_bullet_list: Verifies conversion of bullet lists.
    - test_convert_markdown_to_html_code_block: Verifies conversion of standalone code blocks.
    - test_convert_markdown_to_html_complex: Verifies conversion of complex content with headings,
        paragraphs, and code blocks.
    - test_convert_markdown_to_html_inline_code: Verifies conversion of inline code blocks.
    - test_convert_markdown_to_html_mixed_content: Verifies handling of mixed markdown content.
    - test_convert_markdown_to_html_multiline_paragraphs: Verifies conversion of multiline
        paragraphs.
    - test_convert_markdown_to_html_with_blockquotes: Verifies conversion of blockquotes.
    - test_convert_markdown_to_html_with_headings_and_paragraphs: Verifies conversion of headings
        and paragraphs.
"""

from app.services.formatting_service import convert_markdown_to_html


def test_convert_markdown_to_html_bullet_list() -> None:
    """Tests conversion of bullet lists in markdown to HTML."""
    text = "- First item\n- Second item\n\nA line after the list."
    expected_html = "<ul><li>First item</li><li>Second item</li></ul><p>A line after the list.</p>"
    assert ''.join(convert_markdown_to_html(text).split()) == ''.join(expected_html.split())


def test_convert_markdown_to_html_code_block() -> None:
    """Tests conversion of standalone code blocks in markdown to HTML."""
    text = "```\nprint('Hello, World!')\n```"
    expected_html = '<pre class="codehilite"><code>print(\'Hello, World!\')</code></pre>'
    assert ''.join(convert_markdown_to_html(text).split()) == ''.join(expected_html.split())


def test_convert_markdown_to_html_complex() -> None:
    text = """
# Six Essential Object-Oriented Design Principles from Matthias Noback's “Object Design Style Guide”

The concept of transferable skills is one that I hold dear, particularly in the realm of programming...

Let's illustrate composition, but instead of cars and engines that almost every tutorial has, I'll use games, because games are fun:

```
class Game:
    def __init__(self, title: str, play_time: int = 0) -> None:
        self.title: str = title
        self.play_time: int = play_time

    def add_play_time(self, hours: int) -> None:
        self.play_time += hours
        print(f"Added {hours} hours to {self.title}. Total play time is now {self.play_time} hours.")

    def __str__(self) -> str:
        return f"{self.title} ({self.play_time} hours played)"
```

In this example, the GamerAccount class uses composition to manage instances of the Game class...
    """  # noqa: E501
    expected_html = """
    <h1>Six Essential Object-Oriented Design Principles from Matthias Noback's “Object Design Style Guide”</h1>
    <p>The concept of transferable skills is one that I hold dear, particularly in the realm of programming...</p>
    <p>Let's illustrate composition, but instead of cars and engines that almost every tutorial has, I'll use games, because games are fun:</p>
    <pre class="codehilite"><code>class Game:
    def __init__(self, title: str, play_time: int = 0) -&gt; None:
        self.title: str = title
        self.play_time: int = play_time

    def add_play_time(self, hours: int) -&gt; None:
        self.play_time += hours
        print(f&quot;Added {hours} hours to {self.title}. Total play time is now {self.play_time} hours.&quot;)

    def __str__(self) -&gt; str:
        return f&quot;{self.title} ({self.play_time} hours played)&quot;
    </code></pre>
    <p>In this example, the GamerAccount class uses composition to manage instances of the Game class...</p>
    """  # noqa: E501
    assert ''.join(convert_markdown_to_html(text).split()) == ''.join(expected_html.split())


def test_convert_markdown_to_html_inline_code() -> None:
    """Tests conversion of inline code in markdown to HTML."""
    text = "Here is some `inline code` in the middle of a sentence."
    expected_html = "<p>Here is some <code>inline code</code> in the middle of a sentence.</p>"
    assert ''.join(convert_markdown_to_html(text).split()) == ''.join(expected_html.split())


def test_convert_markdown_to_html_mixed_content() -> None:
    """Tests conversion of mixed content including headings, lists, and paragraphs to HTML."""
    text = "# Title\nIntro text\n\n- Item one\n- Item two\n\n## Subtitle\nRegular text."
    expected_html = ("<h1>Title</h1><p>Intro text</p><ul><li>Item one</li>"
                     "<li>Item two</li></ul><h2>Subtitle</h2><p>Regular text.</p>")
    assert ''.join(convert_markdown_to_html(text).split()) == ''.join(expected_html.split())


def test_convert_markdown_to_html_multiline_paragraphs() -> None:
    """Tests conversion of multiple paragraphs in markdown to HTML."""
    text = "This is the first paragraph.\n\nThis is the second paragraph."
    expected_html = "<p>This is the first paragraph.</p><p>This is the second paragraph.</p>"
    assert ''.join(convert_markdown_to_html(text).split()) == ''.join(expected_html.split())


def test_convert_markdown_to_html_with_blockquotes() -> None:
    """Tests conversion of blockquotes in markdown to HTML."""
    text = "> This is a blockquote.\nThis is not a blockquote."
    expected_html = ("<blockquote><p>This is a blockquote. "
                     "This is not a blockquote.</p></blockquote>")
    assert ''.join(convert_markdown_to_html(text).split()) == ''.join(expected_html.split())


def test_convert_markdown_to_html_with_headings_and_paragraphs() -> None:
    """Tests conversion of markdown with headings and paragraphs to HTML."""
    text = "# Main Title\nSome introductory text.\n## Subtitle\nMore content here."
    expected_html = ("<h1>Main Title</h1>"
                     "<p>Some introductory text.</p><h2>Subtitle</h2><p>More content here.</p>")
    assert ''.join(convert_markdown_to_html(text).split()) == ''.join(expected_html.split())
