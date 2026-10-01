"""Integration tests for DictionaryDashboardService.get_data_health.

Tests included:
    - test_get_data_health_seeded_queues: Verifies audit queues from mixed seed data.
    - test_get_data_health_limit_truncates: Verifies limit truncates each queue.
"""

import pytest

from app.services.dictionary_dashboard_service import DictionaryDashboardService


@pytest.mark.dictionary
def test_get_data_health_seeded_queues(session, seed_dashboard_general):
    """Verifies that data-health queues contain expected missing and compound words."""
    seeded = seed_dashboard_general()
    session.flush()

    service = DictionaryDashboardService(session)
    payload = service.get_data_health()

    missing_examples = {word.viet_word for word in payload["missing_examples"]}
    missing_types = {word.viet_word for word in payload["missing_types"]}
    compounds = {word.viet_word for word in payload["multi_syllable_without_han_viet"]}

    assert seeded["bare_word"].viet_word in missing_examples
    assert seeded["compound_word"].viet_word in missing_examples
    assert seeded["covered_word"].viet_word not in missing_examples

    assert seeded["bare_word"].viet_word in missing_types
    assert seeded["covered_word"].viet_word not in missing_types

    assert seeded["compound_word"].viet_word in compounds
    assert seeded["covered_word"].viet_word not in compounds


@pytest.mark.dictionary
def test_get_data_health_limit_truncates(session, make_word):
    """Verifies that the limit argument truncates each audit queue."""
    for index in range(3):
        make_word(viet_word=f"bare {index}", english_translation=f"bare {index}")
    session.flush()

    service = DictionaryDashboardService(session)
    payload = service.get_data_health(limit=1)

    assert len(payload["missing_examples"]) == 1
    assert len(payload["missing_types"]) == 1
    assert len(payload["multi_syllable_without_han_viet"]) == 1
