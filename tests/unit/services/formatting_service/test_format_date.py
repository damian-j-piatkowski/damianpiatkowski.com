"""Unit tests for the format_date function of the FormattingService module.

This module contains unit tests for the format_date function, which converts
a datetime string from the database into a human-readable format.

Tests included:
    - test_format_date_empty_string: Verifies that empty string input returns an empty string.
    - test_format_date_leap_year: Verifies correct formatting for leap day dates.
    - test_format_date_limits: Verifies formatting for earliest and latest possible dates.
    - test_format_date_logs_properly: Verifies that format_date emits the expected debug/warning logs.
    - test_format_date_trimming: Verifies correct handling of leading/trailing whitespace.
    - test_format_date_valid_input: Verifies correct formatting for valid datetime strings.
    - test_format_date_various_invalid_inputs: Verifies fallback behavior and logging for invalid or partial inputs.
"""

import pytest

from app.services.formatting_service import format_date


def test_format_date_empty_string() -> None:
    """Tests that an empty string returns an empty string."""
    assert format_date("") == ""


def test_format_date_leap_year() -> None:
    """Tests correct formatting for leap day in a leap year."""
    date_str = "2024-02-29 00:00:00"
    expected = "February 29, 2024"
    assert format_date(date_str) == expected


def test_format_date_limits() -> None:
    """Tests formatting for earliest and latest possible dates."""
    earliest = "0001-01-01 00:00:00"
    latest = "9999-12-31 23:59:59"

    assert format_date(earliest) == "January 01, 0001"
    assert format_date(latest) == "December 31, 9999"


def test_format_date_logs_properly(caplog) -> None:
    """Tests that format_date emits the expected debug/warning logs."""
    caplog.set_level("DEBUG")

    # Case 1: Empty string
    _ = format_date("")
    assert any("format_date: Empty date string received." in msg for msg in caplog.messages), \
        "Missing log for empty string input"

    # Case 2: Valid date
    caplog.clear()
    _ = format_date("2025-07-22 07:39:58")
    assert any("format_date: Parsed '2025-07-22 07:39:58' -> 'July 22, 2025'" in msg for msg in caplog.messages), \
        "Missing log for successful parse"

    # Case 3: Invalid date (should trigger warning and fallback)
    caplog.clear()
    _ = format_date("invalid-date")
    assert any("format_date: Failed to parse" in msg for msg in caplog.messages), \
        "Missing warning log for invalid date"

    # Case 4: None input
    caplog.clear()
    _ = format_date(None)  # type: ignore[arg-type]
    assert any("format_date: Empty date string received." in msg for msg in caplog.messages), \
        "Missing log for None input"


def test_format_date_trimming() -> None:
    """Tests trimming of leading/trailing whitespace in valid datetime strings."""
    date_str = "   2025-07-22 07:39:58   "
    expected = "July 22, 2025"
    # We strip here since format_date itself does not strip whitespace
    assert format_date(date_str.strip()) == expected


def test_format_date_valid_input() -> None:
    """Tests correct formatting of a valid datetime string."""
    date_str = "2025-07-22 07:39:58"
    expected = "July 22, 2025"
    assert format_date(date_str) == expected


@pytest.mark.parametrize(
    "input_str,expected",
    [
        (None, ""),  # None input → empty string
        ("invalid-date-string", "invalid-da"),  # Completely invalid string → first 10 chars
        ("2025-07-22", "2025-07-22"),  # Partial date without time → first 10 chars
        ("short", "short"),  # Less than 10 chars → return as-is
    ],
)
def test_format_date_various_invalid_inputs(input_str, expected, caplog) -> None:
    """Tests fallback behavior and logging for invalid, None, or partial inputs."""
    caplog.set_level("WARNING")

    result = format_date(input_str)
    assert result == expected

    # Warnings should be logged for all non-empty invalid cases
    if input_str not in (None, ""):
        assert any(
            "format_date: Failed to parse" in message
            for message in caplog.messages
        )
    else:
        assert not caplog.messages
