"""Repository for dictionary sources."""

from typing import List, Optional

from sqlalchemy import delete, insert, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.domain.dictionary_source import DictionarySource
from app.exceptions import DictionarySourceNotFoundError
from app.models.tables.dictionary_source import dictionary_sources


class SourceRepository:
    """Persistence access for dictionary_sources."""

    def __init__(self, session: Session) -> None:
        self.session = session

    @staticmethod
    def _hydrate(row) -> DictionarySource:
        return DictionarySource(
            source_id=row.id,
            source_type=row.source_type,
            title=row.title,
            url=row.url,
            created_at=row.created_at,
        )

    def get_by_id(self, source_id: int) -> DictionarySource:
        """Load a source by primary key."""
        try:
            row = self.session.execute(
                select(dictionary_sources).where(dictionary_sources.c.id == source_id)
            ).fetchone()
            if row is None:
                raise DictionarySourceNotFoundError(
                    f"Dictionary source id={source_id} was not found.",
                    source_id=source_id,
                )
            return self._hydrate(row)
        except DictionarySourceNotFoundError:
            raise
        except SQLAlchemyError as exc:
            raise RuntimeError(f"Failed to load source id={source_id}: {exc}") from exc

    def search(self, query: str = "", limit: int = 20) -> List[DictionarySource]:
        """Search sources by title prefix/substring; empty query returns recent sources."""
        try:
            stmt = select(dictionary_sources).order_by(
                dictionary_sources.c.created_at.desc()
            ).limit(limit)
            if query.strip():
                pattern = f"%{query.strip()}%"
                stmt = (
                    select(dictionary_sources)
                    .where(dictionary_sources.c.title.like(pattern))
                    .order_by(dictionary_sources.c.created_at.desc())
                    .limit(limit)
                )
            rows = self.session.execute(stmt).fetchall()
            return [self._hydrate(row) for row in rows]
        except SQLAlchemyError as exc:
            raise RuntimeError(f"Failed to search sources: {exc}") from exc

    def list_recent(self, limit: int = 10) -> List[DictionarySource]:
        """Return the most recently created sources."""
        return self.search(query="", limit=limit)

    def create(
            self,
            source_type: str,
            title: str,
            url: Optional[str] = None,
    ) -> DictionarySource:
        """Insert a new dictionary source."""
        try:
            result = self.session.execute(
                insert(dictionary_sources).values(
                    source_type=source_type,
                    title=title,
                    url=url,
                )
            )
            self.session.flush()
            return self.get_by_id(result.inserted_primary_key[0])
        except SQLAlchemyError as exc:
            raise RuntimeError(f"Failed to create source '{title}': {exc}") from exc

    def delete(self, source_id: int) -> None:
        """Delete a source; associated examples cascade at the database layer."""
        try:
            result = self.session.execute(
                delete(dictionary_sources).where(dictionary_sources.c.id == source_id)
            )
            if result.rowcount == 0:
                raise DictionarySourceNotFoundError(
                    f"Dictionary source id={source_id} was not found.",
                    source_id=source_id,
                )
            self.session.flush()
        except DictionarySourceNotFoundError:
            raise
        except SQLAlchemyError as exc:
            raise RuntimeError(f"Failed to delete source id={source_id}: {exc}") from exc
