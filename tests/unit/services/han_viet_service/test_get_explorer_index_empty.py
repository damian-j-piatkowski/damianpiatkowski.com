"""Unit tests for HanVietService.get_explorer_index empty-state behaviour.

Tests included:
    - test_get_explorer_index_empty_database: Verifies empty list on no roots.
"""

import pytest

from app.services.han_viet_service import HanVietService


@pytest.mark.dictionary
def test_get_explorer_index_empty_database(session):
    """Verifies that explorer index returns an empty list when no roots exist."""
    service = HanVietService(session)
    assert service.get_explorer_index() == []
