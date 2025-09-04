"""Unit tests for the `calculate_read_time_minutes` utility.

Verifies accurate and robust estimation of read time from markdown content.
Tests account for edge cases like empty input, heavy formatting, multilingual
content, and custom reading speeds.

Tests included:
    - test_calculate_read_time_for_empty_content: Returns a minimum of 1 minute even for empty input.
    - test_calculate_read_time_for_high_volume_text: Accurately estimates time for long content (e.g., 1500 words).
    - test_calculate_read_time_for_markdown_formatting_noise: Ignores markdown formatting like #, *, links, and code.
    - test_calculate_read_time_for_minimum_threshold: Always returns at least 1 minute for very short input.
    - test_calculate_read_time_with_custom_speed: Supports custom words-per-minute values.
    - test_calculate_read_time_with_non_english_words: Handles multilingual and non-ASCII characters gracefully.
"""

from app.services.file_processing_service import calculate_read_time_minutes


def test_calculate_read_time_for_empty_content() -> None:
    """Returns a minimum of 1 minute even for empty input."""
    assert calculate_read_time_minutes("") == 1


def test_calculate_read_time_for_high_volume_text() -> None:
    """Accurately estimates time for long content (e.g., 1500 words)."""
    text = "word " * 1500
    assert calculate_read_time_minutes(text) == 8  # 1500 ÷ 200 = 7.5 → 8


def test_calculate_read_time_formatting_noise_affects_result() -> None:
    """Verifies that markdown formatting noise does not inflate word count beyond true content."""

    markdown = """
    # Big Heading

    Welcome to the **Markdown Test**. This paragraph is full of _formatting_,
    including [links](https://example.com), `inline code`, and more.

    - Bullet point one
    - Bullet point two
    - Bullet point three

    > A blockquote with **bold** and *italic* text.
    > Another blockquote line.

    ```python
    def example_function():
        # This is a comment
        pass
    ```

    Continuing the post with just enough **text** to hover around the 200-word threshold.
    Let's keep adding valid words to simulate a post that is very close to requiring
    2 full minutes to read based on real, readable content.

    Here we go: word1 word2 word3 word4 word5 word6 word7 word8 word9 word10
    word11 word12 word13 word14 word15 word16 word17 word18 word19 word20
    word21 word22 word23 word24 word25 word26 word27 word28 word29 word30
    word31 word32 word33 word34 word35 word36 word37 word38 word39 word40
    word41 word42 word43 word44 word45 word46 word47 word48 word49 word50
    word51 word52 word53 word54 word55 word56 word57 word58 word59 word60
    word61 word62 word63 word64 word65 word66 word67 word68 word69 word70
    word71 word72 word73 word74 word75 word76 word77 word78 word79 word80
    word81 word82 word83 word84 word85 word86 word87 word88 word89 word90
    word91 word92 word93 word94 word95 word96 word97 word98 word99 word100
    word101 word102 word103 word104 word105 word106 word107 word108 word109
    word110 word111 word112 word113 word114 word115
    """
    # Actual word count now < 200 → expect 1 minute
    assert calculate_read_time_minutes(markdown) == 1


def test_calculate_read_time_for_minimum_threshold() -> None:
    """Always returns at least 1 minute, even for very short content."""
    assert calculate_read_time_minutes("Quick post.") == 1


def test_calculate_read_time_with_custom_speed() -> None:
    """Supports custom words-per-minute rate."""
    text = "word " * 600
    assert calculate_read_time_minutes(text, words_per_minute=300) == 2  # 600 ÷ 300


def test_calculate_read_time_with_non_english_words() -> None:
    """Handles multilingual or non-ASCII words correctly."""
    text = "こんにちは 世界 " * 100  # Japanese for "Hello, World"
    assert calculate_read_time_minutes(text) == 1  # 200 words threshold not met
