"""Integration tests for SourceService.create.

Tests included:
    - test_create_requires_title: Verifies blank titles are rejected.
    - test_create_success: Verifies a valid source is persisted.
"""

import pytest

from app.exceptions import DictionaryValidationError
from app.services.source_service import SourceService


@pytest.mark.dictionary
def test_create_requires_title(session):
    """Verifies that creating a source with a blank title raises ValidationError."""
    service = SourceService(session)
    with pytest.raises(DictionaryValidationError):
        service.create(source_type="book", title="  ")


@pytest.mark.dictionary
def test_create_success(session):
    """Verifies that a valid source is created and returned."""
    service = SourceService(session)
    source = service.create(source_type="book", title="Truyện Kiều", url=None)
    assert source.title == "Truyện Kiều"
    assert source.source_type == "book"
