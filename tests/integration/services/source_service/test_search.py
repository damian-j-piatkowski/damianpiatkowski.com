"""Integration tests for SourceService.search.

Tests included:
    - test_search_by_title: Verifies title substring search.
"""

import pytest

from app.services.source_service import SourceService


@pytest.mark.dictionary
def test_search_by_title(session, make_source):
    """Verifies that search returns sources matching a title query."""
    make_source(source_type="book", title="Truyện Kiều", url=None)
    make_source(source_type="article", title="News Desk", url=None)
    session.flush()

    service = SourceService(session)
    results = service.search(query="Kiều")
    assert len(results) == 1
    assert results[0].title == "Truyện Kiều"
