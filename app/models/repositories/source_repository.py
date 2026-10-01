"""Repository for dictionary sources."""

from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy import delete, func, insert, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.domain.dictionary_source import DictionarySource
from app.exceptions import DictionarySourceNotFoundError
from app.models.tables.dictionary_example import dictionary_examples
from app.models.tables.dictionary_source import dictionary_sources
from app.models.tables.word_han_viet_association import word_han_viet_association


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

    def count_sources(self) -> int:
        """Return the total number of dictionary sources."""
        try:
            return int(
                self.session.execute(
                    select(func.count()).select_from(dictionary_sources)
                ).scalar()
                or 0
            )
        except SQLAlchemyError as exc:
            raise RuntimeError(f"Failed to count sources: {exc}") from exc

    def list_sources_catalog(
            self,
            page: int = 1,
            per_page: int = 20,
            sort: str = "created_at_desc",
            source_type: Optional[str] = None,
            title_query: Optional[str] = None,
    ) -> Tuple[List[Dict[str, Any]], int]:
        """Return a paginated sources catalog with citation and Hán Việt metrics."""
        try:
            page = max(1, page)
            per_page = max(1, min(per_page, 100))

            example_stats = (
                select(
                    dictionary_examples.c.source_id.label("source_id"),
                    func.count().label("citation_count"),
                    func.count(func.distinct(dictionary_examples.c.word_id)).label(
                        "unique_words"
                    ),
                )
                .group_by(dictionary_examples.c.source_id)
            ).subquery()

            hv_stats = (
                select(
                    dictionary_examples.c.source_id.label("source_id"),
                    func.count(func.distinct(dictionary_examples.c.word_id)).label(
                        "hv_words"
                    ),
                )
                .select_from(dictionary_examples)
                .join(
                    word_han_viet_association,
                    word_han_viet_association.c.word_id == dictionary_examples.c.word_id,
                )
                .group_by(dictionary_examples.c.source_id)
            ).subquery()

            citation_count = func.coalesce(example_stats.c.citation_count, 0)
            unique_words = func.coalesce(example_stats.c.unique_words, 0)
            hv_words = func.coalesce(hv_stats.c.hv_words, 0)

            filters = []
            if source_type and source_type.strip():
                filters.append(
                    dictionary_sources.c.source_type == source_type.strip().lower()
                )
            if title_query and title_query.strip():
                filters.append(
                    dictionary_sources.c.title.like(f"%{title_query.strip()}%")
                )

            count_stmt = select(func.count()).select_from(dictionary_sources)
            if filters:
                count_stmt = count_stmt.where(*filters)
            total = int(self.session.execute(count_stmt).scalar() or 0)

            sort_map = {
                "title_asc": dictionary_sources.c.title.asc(),
                "title_desc": dictionary_sources.c.title.desc(),
                "citations_asc": citation_count.asc(),
                "citations_desc": citation_count.desc(),
                "created_at_asc": dictionary_sources.c.created_at.asc(),
                "created_at_desc": dictionary_sources.c.created_at.desc(),
            }
            order_by = sort_map.get(sort, dictionary_sources.c.created_at.desc())

            stmt = (
                select(
                    dictionary_sources.c.id,
                    dictionary_sources.c.source_type,
                    dictionary_sources.c.title,
                    dictionary_sources.c.url,
                    dictionary_sources.c.created_at,
                    citation_count.label("citation_count"),
                    unique_words.label("unique_words_covered"),
                    hv_words.label("hv_words_covered"),
                )
                .outerjoin(
                    example_stats,
                    example_stats.c.source_id == dictionary_sources.c.id,
                )
                .outerjoin(
                    hv_stats,
                    hv_stats.c.source_id == dictionary_sources.c.id,
                )
                .order_by(order_by)
                .offset((page - 1) * per_page)
                .limit(per_page)
            )
            if filters:
                stmt = stmt.where(*filters)

            rows = self.session.execute(stmt).fetchall()
            items: List[Dict[str, Any]] = []
            for row in rows:
                unique = int(row.unique_words_covered or 0)
                hv_covered = int(row.hv_words_covered or 0)
                ratio = (hv_covered / unique * 100.0) if unique else 0.0
                items.append(
                    {
                        "id": row.id,
                        "source_type": row.source_type,
                        "title": row.title,
                        "url": row.url,
                        "created_at": row.created_at,
                        "citation_count": int(row.citation_count or 0),
                        "unique_words_covered": unique,
                        "han_viet_ratio": round(ratio, 1),
                    }
                )
            return items, total
        except SQLAlchemyError as exc:
            raise RuntimeError(f"Failed to load sources catalog: {exc}") from exc
