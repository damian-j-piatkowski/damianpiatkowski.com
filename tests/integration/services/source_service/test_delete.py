"""Integration tests for SourceService.delete.

Tests included:
    - test_delete_source_success: Verifies a source can be removed.
"""

import pytest

from app.exceptions import DictionarySourceNotFoundError
from app.services.source_service import SourceService


@pytest.mark.dictionary
def test_delete_source_success(session, make_source):
    """Verifies that delete removes a source and subsequent get fails."""
    source = make_source(source_type="book", title="Temp", url=None)
    session.flush()

    service = SourceService(session)
    service.delete(source.id)
    with pytest.raises(DictionarySourceNotFoundError):
        service.sources.get_by_id(source.id)
