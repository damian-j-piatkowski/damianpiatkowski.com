"""Integration tests for HanVietService.get_root_cluster.

Tests included:
    - test_get_root_cluster_returns_compounds: Verifies root and compound payload.
    - test_get_root_cluster_missing_raises: Verifies unknown root raises NotFoundError.
"""

import pytest

from app.exceptions import HanVietRootNotFoundError
from app.services.han_viet_service import HanVietService


@pytest.mark.dictionary
def test_get_root_cluster_returns_compounds(session, seed_dashboard_han_viet):
    """Verifies that get_root_cluster returns the root and linked compounds."""
    seeded = seed_dashboard_han_viet()
    session.flush()

    service = HanVietService(session)
    cluster = service.get_root_cluster(seeded["reused_root"].root)
    assert cluster["root"]["root"] == "học"
    assert cluster["root"]["chinese_character"] == "學"
    assert len(cluster["compounds"]) == 2


@pytest.mark.dictionary
def test_get_root_cluster_missing_raises(session):
    """Verifies that an unknown root syllable raises HanVietRootNotFoundError."""
    service = HanVietService(session)
    with pytest.raises(HanVietRootNotFoundError):
        service.get_root_cluster("không-tồn-tại")
