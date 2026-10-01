"""Repository for dictionary word persistence and lookups."""

from typing import List, Optional

from sqlalchemy import delete, insert, select, update
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session, selectinload

from app.domain.dictionary_word import DictionaryWord
from app.exceptions import DictionaryWordDuplicateError, DictionaryWordNotFoundError
from app.models.tables.dictionary_word import dictionary_words
from app.models.tables.word_type_association import word_type_association


class WordRepository:
    """Persistence access for dictionary_words and word_type_association."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def _load_word_types(self, word_id: int) -> List[str]:
        rows = self.session.execute(
            select(word_type_association.c.word_type).where(
                word_type_association.c.word_id == word_id
            )
        ).fetchall()
        return [row.word_type for row in rows]

    def _hydrate_from_orm(self, entity: DictionaryWord) -> DictionaryWord:
        entity.word_types = self._load_word_types(entity.id) if entity.id is not None else []
        return entity

    def find_by_viet_word(self, viet_word: str) -> Optional[DictionaryWord]:
        """Exact duplicate lookup against the unique viet_word column."""
        try:
            row = self.session.execute(
                select(dictionary_words).where(dictionary_words.c.viet_word == viet_word)
            ).fetchone()
            if row is None:
                return None
            return DictionaryWord(
                word_id=row.id,
                viet_word=row.viet_word,
                english_translation=row.english_translation,
                word_types=self._load_word_types(row.id),
                created_at=row.created_at,
                updated_at=row.updated_at,
            )
        except SQLAlchemyError as exc:
            raise RuntimeError(f"Failed to look up word '{viet_word}': {exc}") from exc

    def search_by_prefix(self, prefix: str, limit: int = 20) -> List[DictionaryWord]:
        """Prefix search optimized for autocomplete via idx_viet_word_prefix."""
        try:
            pattern = f"{prefix}%"
            rows = self.session.execute(
                select(dictionary_words)
                .where(dictionary_words.c.viet_word.like(pattern))
                .order_by(dictionary_words.c.viet_word.asc())
                .limit(limit)
            ).fetchall()
            results: List[DictionaryWord] = []
            for row in rows:
                results.append(
                    DictionaryWord(
                        word_id=row.id,
                        viet_word=row.viet_word,
                        english_translation=row.english_translation,
                        word_types=self._load_word_types(row.id),
                        created_at=row.created_at,
                        updated_at=row.updated_at,
                    )
                )
            return results
        except SQLAlchemyError as exc:
            raise RuntimeError(f"Failed prefix search for '{prefix}': {exc}") from exc

    def get_by_id(self, word_id: int, *, with_relations: bool = True) -> DictionaryWord:
        """Load a dictionary word by id, optionally hydrating examples and roots."""
        try:
            if with_relations:
                entity = self.session.get(
                    DictionaryWord,
                    word_id,
                    options=(
                        selectinload(DictionaryWord.examples),
                        selectinload(DictionaryWord.han_viet_roots),
                    ),
                )
            else:
                entity = self.session.get(DictionaryWord, word_id)

            if entity is None:
                raise DictionaryWordNotFoundError(
                    f"Dictionary word id={word_id} was not found.",
                    word_id=word_id,
                )
            return self._hydrate_from_orm(entity)
        except DictionaryWordNotFoundError:
            raise
        except SQLAlchemyError as exc:
            raise RuntimeError(f"Failed to load word id={word_id}: {exc}") from exc

    def create(
            self,
            viet_word: str,
            english_translation: str,
            word_types: Optional[List[str]] = None,
    ) -> DictionaryWord:
        """Insert a new dictionary word and optional type associations."""
        try:
            result = self.session.execute(
                insert(dictionary_words).values(
                    viet_word=viet_word,
                    english_translation=english_translation,
                )
            )
            self.session.flush()
            word_id = result.inserted_primary_key[0]
            for word_type in word_types or []:
                self.add_word_type(word_id, word_type)
            return self.get_by_id(word_id, with_relations=True)
        except IntegrityError as exc:
            raise DictionaryWordDuplicateError(
                f"Dictionary word '{viet_word}' already exists.",
                viet_word=viet_word,
            ) from exc
        except SQLAlchemyError as exc:
            raise RuntimeError(f"Failed to create word '{viet_word}': {exc}") from exc

    def update(
            self,
            word_id: int,
            *,
            viet_word: Optional[str] = None,
            english_translation: Optional[str] = None,
    ) -> DictionaryWord:
        """Update mutable fields on an existing dictionary word."""
        values = {}
        if viet_word is not None:
            values["viet_word"] = viet_word
        if english_translation is not None:
            values["english_translation"] = english_translation
        if not values:
            return self.get_by_id(word_id)

        try:
            result = self.session.execute(
                update(dictionary_words)
                .where(dictionary_words.c.id == word_id)
                .values(**values)
            )
            if result.rowcount == 0:
                raise DictionaryWordNotFoundError(
                    f"Dictionary word id={word_id} was not found.",
                    word_id=word_id,
                )
            self.session.flush()
            return self.get_by_id(word_id)
        except DictionaryWordNotFoundError:
            raise
        except IntegrityError as exc:
            raise DictionaryWordDuplicateError(
                f"Dictionary word '{viet_word}' already exists.",
                viet_word=viet_word or "",
            ) from exc
        except SQLAlchemyError as exc:
            raise RuntimeError(f"Failed to update word id={word_id}: {exc}") from exc

    def delete(self, word_id: int) -> None:
        """Delete a dictionary word; dependent rows cascade at the database layer."""
        try:
            result = self.session.execute(
                delete(dictionary_words).where(dictionary_words.c.id == word_id)
            )
            if result.rowcount == 0:
                raise DictionaryWordNotFoundError(
                    f"Dictionary word id={word_id} was not found.",
                    word_id=word_id,
                )
            self.session.flush()
        except DictionaryWordNotFoundError:
            raise
        except SQLAlchemyError as exc:
            raise RuntimeError(f"Failed to delete word id={word_id}: {exc}") from exc

    def add_word_type(self, word_id: int, word_type: str) -> None:
        """Associate a grammatical type with a dictionary word."""
        try:
            existing = self.session.execute(
                select(word_type_association.c.word_id).where(
                    word_type_association.c.word_id == word_id,
                    word_type_association.c.word_type == word_type,
                )
            ).fetchone()
            if existing is not None:
                return
            self.session.execute(
                insert(word_type_association).values(word_id=word_id, word_type=word_type)
            )
            self.session.flush()
        except SQLAlchemyError as exc:
            raise RuntimeError(
                f"Failed to add word type '{word_type}' to word id={word_id}: {exc}"
            ) from exc

    def remove_word_type(self, word_id: int, word_type: str) -> None:
        """Remove a grammatical type association from a dictionary word."""
        try:
            self.session.execute(
                delete(word_type_association).where(
                    word_type_association.c.word_id == word_id,
                    word_type_association.c.word_type == word_type,
                )
            )
            self.session.flush()
        except SQLAlchemyError as exc:
            raise RuntimeError(
                f"Failed to remove word type '{word_type}' from word id={word_id}: {exc}"
            ) from exc

    def replace_word_types(self, word_id: int, word_types: List[str]) -> None:
        """Replace all grammatical types for a dictionary word."""
        try:
            self.session.execute(
                delete(word_type_association).where(
                    word_type_association.c.word_id == word_id
                )
            )
            for word_type in word_types:
                self.session.execute(
                    insert(word_type_association).values(
                        word_id=word_id, word_type=word_type
                    )
                )
            self.session.flush()
        except SQLAlchemyError as exc:
            raise RuntimeError(
                f"Failed to replace word types for word id={word_id}: {exc}"
            ) from exc
