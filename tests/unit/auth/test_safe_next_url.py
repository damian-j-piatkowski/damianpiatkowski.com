"""Unit tests for safe internal redirect validation."""

import pytest

from app.auth.redirects import safe_internal_next_url


@pytest.mark.parametrize(
    "value",
    [
        "/admin",
        "/admin/dictionary/new",
        "/dictionary",
        "/admin/dictionary?tab=sources",
    ],
)
def test_safe_internal_next_url_accepts_internal_paths(value):
    assert safe_internal_next_url(value) == value


@pytest.mark.parametrize(
    "value",
    [
        None,
        "",
        "   ",
        "https://attacker-phishing-site.com",
        "http://evil.example",
        "//evil.com",
        "///evil.com",
        "//attacker-phishing-site.com/phish",
        "javascript:alert(1)",
        "https://example.com/admin",
        "admin",
        "\\evil",
    ],
)
def test_safe_internal_next_url_rejects_external_or_invalid(value):
    assert safe_internal_next_url(value) is None
