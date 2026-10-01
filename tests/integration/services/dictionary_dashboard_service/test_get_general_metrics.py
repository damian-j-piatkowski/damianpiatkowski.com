"""Integration tests for DictionaryDashboardService.get_general_metrics.

Tests included:
    - test_get_general_metrics_empty_database: Verifies zero KPIs on an empty DB.
    - test_get_general_metrics_seeded_coverage: Verifies KPI math, etymology, types,
      top sources, and recent activity from seed_dashboard_general.
"""

import pytest

from app.services.dictionary_dashboard_service import DictionaryDashboardService


@pytest.mark.dictionary
def test_get_general_metrics_empty_database(session):
    """Verifies that empty database metrics report zero coverage and empty summaries."""
    service = DictionaryDashboardService(session)
    payload = service.get_general_metrics()

    assert payload["kpis"]["total_words"] == 0
    assert payload["kpis"]["total_sources"] == 0
    assert payload["kpis"]["han_viet_coverage"] == 0.0
    assert payload["kpis"]["citation_coverage"] == 0.0
    assert payload["etymology"] == [
        {"label": "Hán Việt", "count": 0},
        {"label": "Native/Other", "count": 0},
    ]
    assert payload["word_types"] == []
    assert payload["top_sources"] == []
    assert payload["recent_activity"] == []


@pytest.mark.dictionary
def test_get_general_metrics_seeded_coverage(session, seed_dashboard_general):
    """Verifies that seeded coverage produces expected KPIs and categorical summaries."""
    seeded = seed_dashboard_general()
    session.flush()

    service = DictionaryDashboardService(session)
    payload = service.get_general_metrics()

    assert payload["kpis"]["total_words"] == 3
    assert payload["kpis"]["total_sources"] == 2
    assert payload["kpis"]["han_viet_coverage"] == round(1 / 3 * 100.0, 1)
    assert payload["kpis"]["citation_coverage"] == round(1 / 3 * 100.0, 1)

    etymology = {item["label"]: item["count"] for item in payload["etymology"]}
    assert etymology["Hán Việt"] == 1
    assert etymology["Native/Other"] == 2

    type_counts = {item["label"]: item["count"] for item in payload["word_types"]}
    assert type_counts.get("verb") == 1

    assert payload["top_sources"][0]["title"] == seeded["source"].title
    assert payload["top_sources"][0]["citation_count"] >= 1

    recent_words = {word.viet_word for word in payload["recent_activity"]}
    assert seeded["covered_word"].viet_word in recent_words
