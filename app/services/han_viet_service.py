"""Service layer for Hán Việt root detection, association, and deletion safety."""

from typing import Dict, List

from sqlalchemy.orm import Session

from app.domain.han_viet_root import HanVietRoot
from app.exceptions import (
    DictionaryValidationError,
    HanVietRootInUseError,
)
from app.models.repositories.han_viet_repository import HanVietRepository
from app.models.repositories.word_repository import WordRepository


def split_syllables(compound: str) -> List[str]:
    """Split a compound Vietnamese word into lowercase syllables.

    Preserves Vietnamese diacritics while isolating whitespace-separated tokens.
    """
    return [token.lower() for token in (compound or "").split() if token.strip()]


class HanVietService:
    """Business logic for Hán Việt prediction and association workflows."""

    def __init__(self, session: Session) -> None:
        self.session = session
        self.roots = HanVietRepository(session)
        self.words = WordRepository(session)

    def check_existing_roots(self, compound_word: str) -> Dict[str, List]:
        """Split a compound word and report found vs missing roots.

        Returns:
            dict with keys:
                syllables: list[str]
                found: list[dict] with id/root/chinese_character/root_meaning
                missing: list[str]
        """
        syllables = split_syllables(compound_word)
        found_map = self.roots.find_by_roots(syllables)
        found = [
            {
                "id": found_map[syllable].id,
                "root": found_map[syllable].root,
                "chinese_character": found_map[syllable].chinese_character,
                "root_meaning": found_map[syllable].root_meaning,
            }
            for syllable in syllables
            if syllable in found_map
        ]
        missing = [syllable for syllable in syllables if syllable not in found_map]
        return {"syllables": syllables, "found": found, "missing": missing}

    def associate_root(self, word_id: int, root_id: int) -> None:
        """Associate an existing root with a dictionary word."""
        self.words.get_by_id(word_id, with_relations=False)
        self.roots.get_by_id(root_id)
        self.roots.associate(word_id, root_id)

    def create_and_associate(
            self,
            word_id: int,
            root: str,
            chinese_character: str,
            root_meaning: str,
    ) -> HanVietRoot:
        """Create a missing root and associate it with the originating word."""
        self.words.get_by_id(word_id, with_relations=False)

        normalized_root = (root or "").strip().lower()
        normalized_character = (chinese_character or "").strip()
        normalized_meaning = (root_meaning or "").strip()
        if not normalized_root:
            raise DictionaryValidationError("Hán Việt root text is required.", field="root")
        if not normalized_character:
            raise DictionaryValidationError(
                "Chinese character is required.",
                field="chinese_character",
            )
        if not normalized_meaning:
            raise DictionaryValidationError(
                "Root meaning is required.",
                field="root_meaning",
            )

        existing = self.roots.find_by_root(normalized_root)
        if existing is not None:
            created = existing
        else:
            created = self.roots.create(
                root=normalized_root,
                chinese_character=normalized_character,
                root_meaning=normalized_meaning,
            )

        self.roots.associate(word_id, created.id)
        return created

    def unlink_root(self, word_id: int, root_id: int) -> None:
        """Remove only the association between a word and a root."""
        self.words.get_by_id(word_id, with_relations=False)
        self.roots.get_by_id(root_id)
        self.roots.unlink(word_id, root_id)

    def delete_root(self, root_id: int) -> None:
        """Delete a root only when no dictionary associations remain."""
        self.roots.get_by_id(root_id)
        association_count = self.roots.count_associations(root_id)
        if association_count > 0:
            raise HanVietRootInUseError(
                "Hán Việt root cannot be deleted while dictionary associations remain. "
                "Unlink associations first.",
                root_id=root_id,
                association_count=association_count,
            )
        self.roots.delete(root_id)
