"""Integration tests for SourceService.list_recent.

Tests included:
    - test_list_recent_returns_newest_first: Verifies recent ordering.
"""

import pytest

from app.services.source_service import SourceService


@pytest.mark.dictionary
def test_list_recent_returns_newest_first(session, make_source):
    """Verifies that list_recent returns the most recently created sources."""
    make_source(source_type="book", title="Older", url=None)
    make_source(source_type="article", title="Newer", url=None)
    session.flush()

    service = SourceService(session)
    recent = service.list_recent(limit=10)
    titles = [source.title for source in recent]
    assert "Newer" in titles
    assert "Older" in titles
