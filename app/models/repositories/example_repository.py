"""Repository for dictionary example sentences."""

from typing import Optional

from sqlalchemy import delete, insert, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.domain.dictionary_example import DictionaryExample
from app.domain.dictionary_source import DictionarySource
from app.models.tables.dictionary_example import dictionary_examples
from app.models.tables.dictionary_source import dictionary_sources


class ExampleRepository:
    """Persistence access for dictionary_examples."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def _hydrate(self, row, source: Optional[DictionarySource] = None) -> DictionaryExample:
        return DictionaryExample(
            example_id=row.id,
            word_id=row.word_id,
            source_id=row.source_id,
            sentence=row.sentence,
            english_translation=row.english_translation,
            created_at=row.created_at,
            source=source,
        )

    def create(
            self,
            word_id: int,
            source_id: int,
            sentence: str,
            english_translation: str,
    ) -> DictionaryExample:
        """Insert a contextual example for a dictionary word."""
        try:
            result = self.session.execute(
                insert(dictionary_examples).values(
                    word_id=word_id,
                    source_id=source_id,
                    sentence=sentence,
                    english_translation=english_translation,
                )
            )
            self.session.flush()
            example_id = result.inserted_primary_key[0]
            row = self.session.execute(
                select(dictionary_examples).where(dictionary_examples.c.id == example_id)
            ).fetchone()
            source_row = self.session.execute(
                select(dictionary_sources).where(dictionary_sources.c.id == source_id)
            ).fetchone()
            source = None
            if source_row is not None:
                source = DictionarySource(
                    source_id=source_row.id,
                    source_type=source_row.source_type,
                    title=source_row.title,
                    url=source_row.url,
                    created_at=source_row.created_at,
                )
            return self._hydrate(row, source=source)
        except SQLAlchemyError as exc:
            raise RuntimeError(
                f"Failed to create example for word id={word_id}: {exc}"
            ) from exc

    def delete(self, example_id: int) -> None:
        """Delete a single contextual example."""
        try:
            result = self.session.execute(
                delete(dictionary_examples).where(dictionary_examples.c.id == example_id)
            )
            if result.rowcount == 0:
                raise RuntimeError(f"Example id={example_id} was not found.")
            self.session.flush()
        except SQLAlchemyError as exc:
            raise RuntimeError(f"Failed to delete example id={example_id}: {exc}") from exc
