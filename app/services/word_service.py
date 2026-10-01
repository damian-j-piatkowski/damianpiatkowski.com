"""Service layer for dictionary word workflows."""

from typing import List, Optional

from sqlalchemy.orm import Session

from app.domain.dictionary_word import DictionaryWord
from app.exceptions import DictionaryValidationError, DictionaryWordDuplicateError
from app.models.repositories.example_repository import ExampleRepository
from app.models.repositories.source_repository import SourceRepository
from app.models.repositories.word_repository import WordRepository
from app.services.dictionary_validation import (
    validate_english_translation,
    validate_viet_word,
    validate_word_types,
)


class WordService:
    """Business logic for dictionary entry create/update/delete and lookups."""

    def __init__(self, session: Session) -> None:
        self.session = session
        self.words = WordRepository(session)
        self.examples = ExampleRepository(session)
        self.sources = SourceRepository(session)

    def search_prefix(self, query: str, limit: int = 20) -> List[DictionaryWord]:
        """Return autocomplete matches for a Vietnamese prefix query."""
        prefix = (query or "").strip()
        if not prefix:
            return []
        return self.words.search_by_prefix(prefix, limit=limit)

    def check_duplicate(self, viet_word: str) -> Optional[DictionaryWord]:
        """Return an existing entry when the Vietnamese word already exists."""
        normalized = (viet_word or "").strip()
        if not normalized:
            return None
        return self.words.find_by_viet_word(normalized)

    def get_entry(self, word_id: int) -> DictionaryWord:
        """Load a full dictionary entry with relationships."""
        return self.words.get_by_id(word_id, with_relations=True)

    def create_entry(
            self,
            viet_word: str,
            english_translation: str,
            word_types: Optional[List[str]] = None,
    ) -> DictionaryWord:
        """Create a new dictionary entry after validation and duplicate checks."""
        normalized_word = validate_viet_word(viet_word)
        normalized_translation = validate_english_translation(english_translation)
        normalized_types = validate_word_types(word_types)

        existing = self.words.find_by_viet_word(normalized_word)
        if existing is not None:
            raise DictionaryWordDuplicateError(
                f"Dictionary word '{normalized_word}' already exists.",
                viet_word=normalized_word,
            )

        word = self.words.create(
            viet_word=normalized_word,
            english_translation=normalized_translation,
            word_types=normalized_types,
        )
        return word

    def update_entry(
            self,
            word_id: int,
            *,
            viet_word: Optional[str] = None,
            english_translation: Optional[str] = None,
            word_types: Optional[List[str]] = None,
    ) -> DictionaryWord:
        """Update dictionary entry fields and optional word types."""
        kwargs = {}
        if viet_word is not None:
            kwargs["viet_word"] = validate_viet_word(viet_word)
        if english_translation is not None:
            kwargs["english_translation"] = validate_english_translation(english_translation)

        word = self.words.update(word_id, **kwargs)
        if word_types is not None:
            self.words.replace_word_types(word_id, validate_word_types(word_types))
            word = self.words.get_by_id(word_id, with_relations=True)
        return word

    def delete_entry(self, word_id: int) -> None:
        """Permanently delete a dictionary entry and cascaded dependents."""
        self.words.delete(word_id)

    def add_example(
            self,
            word_id: int,
            source_id: int,
            sentence: str,
            english_translation: str,
    ):
        """Add a contextual example to an existing dictionary entry."""
        sentence_normalized = (sentence or "").strip()
        translation_normalized = (english_translation or "").strip()
        if not sentence_normalized:
            raise DictionaryValidationError("Example sentence is required.", field="sentence")
        if not translation_normalized:
            raise DictionaryValidationError(
                "Example English translation is required.",
                field="english_translation",
            )

        # Ensure parent word and source exist.
        self.words.get_by_id(word_id, with_relations=False)
        self.sources.get_by_id(source_id)

        return self.examples.create(
            word_id=word_id,
            source_id=source_id,
            sentence=sentence_normalized,
            english_translation=translation_normalized,
        )

    def remove_example(self, example_id: int) -> None:
        """Remove a single contextual example."""
        self.examples.delete(example_id)
