"""Integration tests for HanVietRepository public explorer queries.

Tests included:
    - test_get_root_with_compounds_join: Verifies root/compound join payload.
    - test_get_all_roots_summary_counts: Verifies summary compound counts.
"""

import pytest

from app.models.repositories.han_viet_repository import HanVietRepository


@pytest.mark.dictionary
def test_get_root_with_compounds_join(session, seed_dashboard_han_viet):
    """Verifies that get_root_with_compounds returns associated dictionary words."""
    seeded = seed_dashboard_han_viet()
    session.flush()

    repo = HanVietRepository(session)
    result = repo.get_root_with_compounds(seeded["reused_root"].root)
    assert result is not None
    root, compounds = result
    assert root.root == "học"
    assert len(compounds) == 2
    assert all("viet_word" in item and "id" in item for item in compounds)

    assert repo.get_root_with_compounds("missing-root") is None


@pytest.mark.dictionary
def test_get_all_roots_summary_counts(session, seed_dashboard_han_viet):
    """Verifies that get_all_roots_summary ranks reused roots above orphans."""
    seeded = seed_dashboard_han_viet()
    session.flush()

    repo = HanVietRepository(session)
    rows = repo.get_all_roots_summary()
    assert rows[0]["root"] == seeded["reused_root"].root
    assert rows[0]["compound_count"] == 2
