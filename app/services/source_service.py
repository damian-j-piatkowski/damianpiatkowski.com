"""Service layer for dictionary sources."""

from typing import List, Optional

from sqlalchemy.orm import Session

from app.domain.dictionary_source import DictionarySource
from app.domain.domain_enums import SourceType
from app.exceptions import DictionaryValidationError
from app.models.repositories.source_repository import SourceRepository


class SourceService:
    """Business logic for source creation, search, and deletion."""

    def __init__(self, session: Session) -> None:
        self.session = session
        self.sources = SourceRepository(session)

    def list_recent(self, limit: int = 10) -> List[DictionarySource]:
        """Return recently created sources."""
        return self.sources.list_recent(limit=limit)

    def search(self, query: str = "", limit: int = 20) -> List[DictionarySource]:
        """Search sources by title."""
        return self.sources.search(query=query, limit=limit)

    def create(
            self,
            source_type: str,
            title: str,
            url: Optional[str] = None,
    ) -> DictionarySource:
        """Create a source after validating required fields."""
        normalized_title = (title or "").strip()
        if not normalized_title:
            raise DictionaryValidationError(
                "Source title is required.",
                field="title",
            )

        normalized_type = (source_type or "").strip().lower()
        allowed = {member.value for member in SourceType}
        if normalized_type not in allowed:
            raise DictionaryValidationError(
                f"Unsupported source type '{source_type}'.",
                field="source_type",
            )

        normalized_url = (url or "").strip() or None
        return self.sources.create(
            source_type=normalized_type,
            title=normalized_title,
            url=normalized_url,
        )

    def delete(self, source_id: int) -> None:
        """Delete a source; examples cascade at the database layer."""
        self.sources.delete(source_id)
