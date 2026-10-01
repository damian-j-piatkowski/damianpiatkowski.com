"""Integration tests for DictionaryDashboardService.get_sources_catalog.

Tests included:
    - test_get_sources_catalog_empty: Verifies empty catalog payload shape.
    - test_get_sources_catalog_sorts: Verifies catalog ordering for supported sort keys.
    - test_get_sources_catalog_filters: Verifies type and title query filters.
    - test_get_sources_catalog_pagination: Verifies page/per_page/total_pages math.
    - test_get_sources_catalog_echoes_filters: Verifies filter fields are echoed back.
"""

import pytest

from app.services.dictionary_dashboard_service import DictionaryDashboardService


@pytest.mark.dictionary
def test_get_sources_catalog_empty(session):
    """Verifies that an empty catalog returns zero rows and total_pages of 1."""
    service = DictionaryDashboardService(session)
    payload = service.get_sources_catalog()

    assert payload["rows"] == []
    assert payload["total"] == 0
    assert payload["page"] == 1
    assert payload["total_pages"] == 1
    assert payload["source_type"] == ""
    assert payload["title_query"] == ""


@pytest.mark.dictionary
@pytest.mark.parametrize(
    "sort,expected_first_title",
    [
        ("citations_desc", "Zeta Heavy Book"),
        ("title_asc", "Alpha News Desk"),
        ("title_desc", "Zeta Heavy Book"),
    ],
)
def test_get_sources_catalog_sorts(session, seed_dashboard_sources, sort, expected_first_title):
    """Verifies that catalog rows are ordered according to the requested sort key."""
    seed_dashboard_sources()
    session.flush()

    service = DictionaryDashboardService(session)
    payload = service.get_sources_catalog(sort=sort)

    assert payload["rows"][0]["title"] == expected_first_title
    assert payload["sort"] == sort


@pytest.mark.dictionary
def test_get_sources_catalog_filters(session, seed_dashboard_sources):
    """Verifies that source_type and title_query filters narrow the catalog."""
    seed_dashboard_sources()
    session.flush()

    service = DictionaryDashboardService(session)
    payload = service.get_sources_catalog(
        source_type="article",
        title_query="News",
    )

    assert payload["total"] == 1
    assert len(payload["rows"]) == 1
    assert payload["rows"][0]["title"] == "Alpha News Desk"
    assert payload["source_type"] == "article"
    assert payload["title_query"] == "News"


@pytest.mark.dictionary
def test_get_sources_catalog_pagination(session, seed_dashboard_sources):
    """Verifies that pagination returns sliced rows and correct total_pages."""
    seed_dashboard_sources()
    session.flush()

    service = DictionaryDashboardService(session)
    page_one = service.get_sources_catalog(page=1, per_page=1, sort="title_asc")
    page_two = service.get_sources_catalog(page=2, per_page=1, sort="title_asc")

    assert page_one["total"] == 3
    assert page_one["total_pages"] == 3
    assert len(page_one["rows"]) == 1
    assert len(page_two["rows"]) == 1
    assert page_one["rows"][0]["title"] != page_two["rows"][0]["title"]


@pytest.mark.dictionary
def test_get_sources_catalog_echoes_filters(session, seed_dashboard_sources):
    """Verifies that sort and filter arguments are echoed in the response payload."""
    seed_dashboard_sources()
    session.flush()

    service = DictionaryDashboardService(session)
    payload = service.get_sources_catalog(
        page=1,
        per_page=10,
        sort="created_at_desc",
        source_type="book",
        title_query="Heavy",
    )

    assert payload["page"] == 1
    assert payload["per_page"] == 10
    assert payload["sort"] == "created_at_desc"
    assert payload["source_type"] == "book"
    assert payload["title_query"] == "Heavy"
