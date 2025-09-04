"""Unit tests for the `sanitize_contact_form_input` function of the `sanitization_service` module.

This module contains unit tests for the `sanitize_contact_form_input` function, which is responsible
for sanitizing contact form input to prevent XSS attacks and remove dangerous content.

Tests included:
    - test_sanitize_contact_form_input: Verifies that form fields are properly sanitized.
    - test_sanitize_contact_form_input_with_empty_fields: Verifies handling of empty fields.
    - test_sanitize_contact_form_input_with_inline_event_handlers: Verifies that inline event
        handlers are removed.
    - test_sanitize_contact_form_input_with_nested_tags_and_scripts: Verifies proper sanitization
        of nested tags and scripts.
    - test_sanitize_contact_form_input_with_non_string_values: Verifies handling of non-string form
        field values.
    - test_sanitize_contact_form_input_with_mixed_content: Verifies that mixed safe and unsafe
        content is sanitized correctly.
    - test_sanitize_contact_form_input_with_malicious_urls: Verifies that malicious URLs are
        sanitized.
    - test_sanitize_contact_form_input_with_valid_html: Verifies that valid HTML content is
        stripped but retains plain text.

Fixtures:
    - sample_form_data: Provides sample form data with potentially harmful content for testing
        sanitization.
"""

import pytest

from app.services.sanitization_service import sanitize_contact_form_input


@pytest.fixture
def sample_form_data() -> dict[str, str]:
    """Fixture providing a sample contact form data."""
    return {
        "name": "<script>alert('XSS');</script>John Doe",
        "email": "<b>john.doe@example.com</b>",
        "message": "<p>Hello, <script>alert('XSS');</script>world!</p>"
    }


def test_sanitize_contact_form_input(sample_form_data: dict[str, str]) -> None:
    """Tests that contact form fields are properly sanitized."""
    # Act
    sanitized_data = sanitize_contact_form_input(sample_form_data)

    # Assert
    assert sanitized_data["name"] == "John Doe"  # Script tags and JS should be stripped
    assert sanitized_data["email"] == "john.doe@example.com"  # Tags should be stripped
    assert sanitized_data["message"] == "Hello, world!"  # Only allowed tags remain


def test_sanitize_contact_form_input_with_empty_fields() -> None:
    """Tests that empty fields in the contact form are handled gracefully."""
    # Arrange
    form_data = {
        "name": "",
        "email": "",
        "message": ""
    }

    # Act
    sanitized_data = sanitize_contact_form_input(form_data)

    # Assert
    assert sanitized_data["name"] == ""
    assert sanitized_data["email"] == ""
    assert sanitized_data["message"] == ""


def test_sanitize_contact_form_input_with_inline_event_handlers() -> None:
    """Tests that inline event handlers are removed."""
    # Arrange
    form_data = {
        "name": "<div onclick='alert(1)'>Click me</div>",
        "email": "<span onmouseover='alert(1)'>Hover me</span>",
        "message": "No event handlers here"
    }

    # Act
    sanitized_data = sanitize_contact_form_input(form_data)

    # Assert
    assert sanitized_data["name"] == "Click me"  # Event handler should be removed
    assert sanitized_data["email"] == "Hover me"  # Event handler should be removed
    assert sanitized_data["message"] == "No event handlers here"


def test_sanitize_contact_form_input_with_nested_tags_and_scripts() -> None:
    """Tests that nested tags and scripts are sanitized properly."""
    # Arrange
    form_data = {
        "name": "<div><script>alert('XSS');</script><p>John</p></div>",
        "email": "<b><i>john.doe@example.com</i></b>",
        "message": "<p>Hello, <script>alert('XSS');</script>world!</p>"
    }

    # Act
    sanitized_data = sanitize_contact_form_input(form_data)

    # Assert
    assert sanitized_data["name"] == "John"  # <script> removed and nested tags sanitized
    assert sanitized_data["email"] == "john.doe@example.com"  # HTML tags removed
    assert sanitized_data["message"] == "Hello, world!"  # Script tag removed, text remains


def test_sanitize_contact_form_input_with_non_string_values() -> None:
    """Tests that non-string values are properly handled."""
    # Arrange
    form_data = {
        "name": None,
        "email": 12345,  # Number input instead of string
        "message": "<p>Valid HTML content</p>"
    }

    # Act
    sanitized_data = sanitize_contact_form_input(form_data)

    # Assert
    assert sanitized_data["name"] == ""  # None should be converted to an empty string
    assert sanitized_data["email"] == "12345"  # Number should be converted to a string
    assert sanitized_data["message"] == "Valid HTML content"  # HTML should be stripped as usual


def test_sanitize_contact_form_input_with_mixed_content() -> None:
    """Tests that mixed safe and unsafe content is sanitized correctly."""
    # Arrange
    form_data = {
        "name": "John <b>Doe</b> <script>alert('XSS');</script>",
        "email": "<b>john.doe@example.com</b> <img src='invalid'/>",
        "message": "<p>Hello, world!</p><script>alert('XSS');</script>"
    }

    # Act
    sanitized_data = sanitize_contact_form_input(form_data)

    # Assert
    assert sanitized_data["name"] == "John Doe"  # Script should be removed, bold stripped
    assert sanitized_data["email"] == "john.doe@example.com"  # Image tag removed, text remains
    assert sanitized_data["message"] == "Hello, world!"  # Script tag stripped, valid HTML removed


def test_sanitize_contact_form_input_with_malicious_urls() -> None:
    """Tests that malicious URLs are sanitized."""
    # Arrange
    form_data = {
        "name": "<a href='javascript:alert(1)'>Click me</a>",
        "email": "<img src='javascript:alert(1)'/>",
        "message": "<a href='https://example.com'>Safe Link</a>"
    }

    # Act
    sanitized_data = sanitize_contact_form_input(form_data)

    # Assert
    assert sanitized_data["name"] == "Click me"  # Dangerous href should be stripped
    assert sanitized_data["email"] == ""  # Malicious img tag should be fully stripped
    assert sanitized_data["message"] == "Safe Link"  # Valid link should be stripped, text remains


def test_sanitize_contact_form_input_with_valid_html() -> None:
    """Tests that valid HTML content is stripped but retains the plain text."""
    # Arrange
    form_data = {
        "name": "<b>John Doe</b>",
        "email": "<i>john.doe@example.com</i>",
        "message": "<p>Hello, <b>world</b>!</p>"
    }

    # Act
    sanitized_data = sanitize_contact_form_input(form_data)

    # Assert
    assert sanitized_data["name"] == "John Doe"  # Bold tag stripped, text remains
    assert sanitized_data["email"] == "john.doe@example.com"  # Italics tag stripped, text remains
    assert sanitized_data["message"] == "Hello, world!"  # Paragraph and bold tags stripped
