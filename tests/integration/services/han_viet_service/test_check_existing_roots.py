"""Integration tests for HanVietService.check_existing_roots.

Tests included:
    - test_check_existing_roots_found_and_missing: Verifies found vs missing syllables.
"""

import pytest

from app.services.han_viet_service import HanVietService


@pytest.mark.dictionary
def test_check_existing_roots_found_and_missing(session, make_root):
    """Verifies that check_existing_roots reports found and missing syllables."""
    make_root(root="chính", chinese_character="政", root_meaning="politics")
    session.flush()

    service = HanVietService(session)
    result = service.check_existing_roots("chính trị")

    assert result["syllables"] == ["chính", "trị"]
    assert [item["root"] for item in result["found"]] == ["chính"]
    assert result["missing"] == ["trị"]
