"""Integration tests for DictionaryDashboardService.get_word_velocity.

Tests included:
    - test_get_word_velocity_range_shapes: Verifies label/count shapes per range key.
    - test_get_word_velocity_counts_seeded_window: Verifies counts include recent words.
    - test_get_word_velocity_rejects_invalid_range: Verifies ValueError for bad ranges.
    - test_get_word_velocity_gap_fill_contains_zeros: Verifies gap fill leaves zero buckets.
"""

from datetime import datetime, timedelta, timezone

import pytest

from app.services.dictionary_dashboard_service import DictionaryDashboardService


@pytest.mark.dictionary
@pytest.mark.parametrize("range_key", ["30d", "6m", "12m"])
def test_get_word_velocity_range_shapes(session, range_key):
    """Verifies that each velocity range returns aligned non-empty labels and counts."""
    service = DictionaryDashboardService(session)
    payload = service.get_word_velocity(range_key)

    assert len(payload["labels"]) > 0
    assert len(payload["labels"]) == len(payload["counts"])
    assert all(isinstance(count, int) for count in payload["counts"])


@pytest.mark.dictionary
def test_get_word_velocity_counts_seeded_window(session, make_word, set_word_created_at):
    """Verifies that words created inside the 30d window contribute to velocity counts."""
    now = datetime.now(timezone.utc)
    recent = make_word(viet_word="mới", english_translation="new")
    older = make_word(viet_word="cũ", english_translation="old")
    set_word_created_at(recent.id, now - timedelta(days=2))
    set_word_created_at(older.id, now - timedelta(days=40))
    session.flush()

    service = DictionaryDashboardService(session)
    payload = service.get_word_velocity("30d")

    assert sum(payload["counts"]) >= 1
    assert len(payload["labels"]) == 30


@pytest.mark.dictionary
@pytest.mark.parametrize("bad_range", ["7d", "1y", "", "daily"])
def test_get_word_velocity_rejects_invalid_range(session, bad_range):
    """Verifies that unsupported velocity ranges raise ValueError."""
    service = DictionaryDashboardService(session)
    with pytest.raises(ValueError):
        service.get_word_velocity(bad_range)


@pytest.mark.dictionary
def test_get_word_velocity_gap_fill_contains_zeros(session):
    """Verifies that gap filling produces zero counts when no words exist in-range."""
    service = DictionaryDashboardService(session)
    payload = service.get_word_velocity("30d")

    assert payload["counts"].count(0) == len(payload["counts"])
    assert len(payload["labels"]) == 30
