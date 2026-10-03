"""Integration tests for HanVietService.create_root."""

import pytest

from app.exceptions import DictionaryValidationError
from app.services.han_viet_service import HanVietService


@pytest.mark.dictionary
def test_create_root_persists_standalone_root(session):
    """Verifies that create_root stores a root without requiring a word association."""
    service = HanVietService(session)
    root = service.create_root(
        root="học",
        chinese_character="學",
        root_meaning="study",
    )
    session.flush()

    assert root.id is not None
    assert root.root == "học"
    assert root.chinese_character == "學"
    assert service.roots.count_associations(root.id) == 0


@pytest.mark.dictionary
def test_create_root_rejects_missing_fields(session):
    """Verifies that create_root validates required fields."""
    service = HanVietService(session)
    with pytest.raises(DictionaryValidationError):
        service.create_root(root="", chinese_character="學", root_meaning="study")
