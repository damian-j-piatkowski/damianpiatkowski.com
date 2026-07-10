"""Defines the core Domain Model representation for a dictionary vocabulary entry.

This module encapsulates pure domain business logic, structural aggregate associations
(examples, Han-Viet semantic roots), and lifecycle tracking invariants independent
of any specific database access framework.

Domain Lifecycle Object Examples:

    1. New Domain Entity Instantiation:
       word = DictionaryWord(
           word_id=None,
           viet_word="báo cáo",
           english_translation="to report; a report"
       )

    2. Hydrated Entity with Aggregates and Timestamps:
       word = DictionaryWord(
           word_id=201,
           viet_word="báo cáo",
           english_translation="to report; a report",
           examples=[example_instance_1, example_instance_2],
           han_viet_roots=[root_instance_1],
           created_at=datetime.datetime(2026, 7, 10, 12, 0, tzinfo=datetime.timezone.utc),
           updated_at=datetime.datetime(2026, 7, 10, 12, 5, tzinfo=datetime.timezone.utc)
       )
"""

import datetime
from typing import List, Optional

# Forward references for type hinting complex aggregate relations
from app.domain.dictionary_example import DictionaryExample
from app.domain.han_viet_root import HanVietRoot


class DictionaryWord:
    """Represents a base vocabulary entry inside the core business domain layer.

    Attributes:
        id (Optional[int]): Database identity anchor; None if not yet persisted.
        viet_word (str): Canonical unique Vietnamese script lookup string.
        english_translation (str): Core summary definition string.
        examples (List[DictionaryExample]): Associated contextual sentence exposures.
        han_viet_roots (List[HanVietRoot]): Underlying Sino-Vietnamese components.
        created_at (Optional[datetime.datetime]): Timezone-aware initial record creation timestamp.
        updated_at (Optional[datetime.datetime]): Timezone-aware active record mutation timestamp.
    """

    def __init__(
            self,
            word_id: Optional[int],
            viet_word: str,
            english_translation: str,
            examples: Optional[List[DictionaryExample]] = None,
            han_viet_roots: Optional[List[HanVietRoot]] = None,
            created_at: Optional[datetime.datetime] = None,
            updated_at: Optional[datetime.datetime] = None
    ) -> None:
        """Initializes a new DictionaryWord domain entity instance."""
        self.id = word_id
        self.viet_word = viet_word
        self.english_translation = english_translation
        self.examples = examples or []
        self.han_viet_roots = han_viet_roots or []
        self.created_at = created_at
        self.updated_at = updated_at

    @property
    def level(self) -> int:
        """Computes the current Kaufmann-style exposure level based on example volume.

        Returns:
            int: Language acquisition level capped at a maximum value of 4.
        """
        count = len(self.examples)
        return min(count, 4)

    @property
    def has_han_viet(self) -> bool:
        """Determines if the word contains underlying Sino-Vietnamese components.

        Returns:
            bool: True if component metadata patterns are linked.
        """
        return len(self.han_viet_roots) > 0
