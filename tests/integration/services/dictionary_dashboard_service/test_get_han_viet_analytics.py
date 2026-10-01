"""Integration tests for DictionaryDashboardService.get_han_viet_analytics.

Tests included:
    - test_get_han_viet_analytics_empty: Verifies empty analytics payload.
    - test_get_han_viet_analytics_seeded: Verifies totals, reuse ranking, and orphans.
"""

import pytest

from app.services.dictionary_dashboard_service import DictionaryDashboardService


@pytest.mark.dictionary
def test_get_han_viet_analytics_empty(session):
    """Verifies that analytics report zeros and empty lists on an empty database."""
    service = DictionaryDashboardService(session)
    payload = service.get_han_viet_analytics()

    assert payload["total_roots"] == 0
    assert payload["distinct_chinese_characters"] == 0
    assert payload["top_reused_roots"] == []
    assert payload["orphan_roots"] == []


@pytest.mark.dictionary
def test_get_han_viet_analytics_seeded(session, seed_dashboard_han_viet):
    """Verifies that reused roots rank first and orphan roots are unbound only."""
    seeded = seed_dashboard_han_viet()
    session.flush()

    service = DictionaryDashboardService(session)
    payload = service.get_han_viet_analytics()

    assert payload["total_roots"] == 2
    assert payload["distinct_chinese_characters"] == 2
    assert payload["top_reused_roots"][0]["root"] == seeded["reused_root"].root
    assert payload["top_reused_roots"][0]["usage_count"] == 2

    orphan_roots = {root.root for root in payload["orphan_roots"]}
    assert seeded["orphan_root"].root in orphan_roots
    assert seeded["reused_root"].root not in orphan_roots
