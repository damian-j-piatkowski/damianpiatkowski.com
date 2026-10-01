"""Integration tests for HanVietService.get_explorer_index.

Tests included:
    - test_get_explorer_index_returns_counts: Verifies summary rows and counts.
    - test_get_explorer_index_filters_query: Verifies q filter narrows results.
"""

import pytest

from app.services.han_viet_service import HanVietService


@pytest.mark.dictionary
def test_get_explorer_index_returns_counts(session, seed_dashboard_han_viet):
    """Verifies that explorer index includes compound counts for seeded roots."""
    seeded = seed_dashboard_han_viet()
    session.flush()

    service = HanVietService(session)
    rows = service.get_explorer_index()
    by_root = {row["root"]: row for row in rows}
    assert by_root[seeded["reused_root"].root]["compound_count"] == 2
    assert by_root[seeded["orphan_root"].root]["compound_count"] == 0


@pytest.mark.dictionary
def test_get_explorer_index_filters_query(session, seed_dashboard_han_viet):
    """Verifies that explorer index respects a root text query filter."""
    seed_dashboard_han_viet()
    session.flush()

    service = HanVietService(session)
    rows = service.get_explorer_index(q="học")
    assert len(rows) == 1
    assert rows[0]["root"] == "học"
