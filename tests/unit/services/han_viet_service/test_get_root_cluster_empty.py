"""Unit/integration-style tests for HanVietService explorer helpers via session.

Tests included:
    - Covered in integration/services/han_viet_service; this module keeps a thin
      empty-root unit check using the service Value path without DB when possible.
"""

import pytest

from app.exceptions import HanVietRootNotFoundError
from app.services.han_viet_service import HanVietService


@pytest.mark.dictionary
def test_get_root_cluster_empty_syllable_raises(session):
    """Verifies that a blank root syllable is treated as not found."""
    service = HanVietService(session)
    with pytest.raises(HanVietRootNotFoundError):
        service.get_root_cluster("   ")
