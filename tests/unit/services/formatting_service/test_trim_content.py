"""Unit tests for the trim_content function in the FormattingService module.

Tests included:
    - test_trim_content_empty_string: Handles empty string input.
    - test_trim_content_none: Handles None input.
    - test_trim_content_short_or_exact_length: Returns content unchanged if within limit.
    - test_trim_content_truncation_variants: Truncates content correctly at various max_length values.
    - test_trim_content_very_long_input: Handles very long input with proper trimming.
"""

import pytest

from app.services.formatting_service import trim_content


@pytest.mark.admin_upload_blog_posts
def test_trim_content_empty_string() -> None:
    """Returns empty string if input is empty."""
    assert trim_content("") == ""


@pytest.mark.admin_upload_blog_posts
def test_trim_content_none() -> None:
    """Returns empty string if input is None."""
    assert trim_content(None) == ""  # type: ignore[arg-type]


@pytest.mark.admin_upload_blog_posts
def test_trim_content_short_or_exact_length() -> None:
    """Returns content unchanged if shorter than or exactly equal to max_length."""
    assert trim_content("Short string", max_length=50) == "Short string"
    exact = "a" * 100
    assert trim_content(exact, max_length=100) == exact


@pytest.mark.admin_upload_blog_posts
@pytest.mark.parametrize(
    "text,max_length,expected",
    [
        ("This is a very long sentence that needs to be trimmed appropriately.", 10, "This is a..."),
        ("Trim me down, please!", 5, "Trim..."),
        ("1234567890", 10, "1234567890"),
        ("Edge case trimming works fine.", 0, "..."),
    ],
)
def test_trim_content_truncation_variants(text: str, max_length: int, expected: str) -> None:
    """Ensures trimming works with various max_length settings."""
    assert trim_content(text, max_length) == expected


@pytest.mark.admin_upload_blog_posts
def test_trim_content_very_long_input() -> None:
    """Ensures very long input is trimmed to default 200 characters + ellipsis."""
    long_text = (
        "Lorem ipsum dolor sit amet, consectetur adipiscing elit. "
        "Phasellus vehicula, metus non interdum gravida, sapien justo ultricies orci, "
        "et blandit nisi nibh non tortor. Sed commodo lorem vitae orci egestas, "
        "et volutpat metus suscipit. Curabitur..."
    )
    expected = long_text[:200] + "..."
    assert trim_content(long_text) == expected
