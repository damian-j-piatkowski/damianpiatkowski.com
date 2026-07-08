"""Defines the DictionaryExample domain model representing a mined contextual sentence.

This module isolates the clean domain representation of vocabulary usage exposures,
pairing target language text directly with its translation metadata and parent source.

Domain Instantiation Examples:

    Scenario A: Unhydrated Representation (Source object not pulled from DB)
        example = DictionaryExample(
            example_id=504,
            word_id=88,
            source_id=14,
            sentence="Doraemon và nhóm bạn càng lúc càng gay cấn, các em đừng bỏ lỡ nhé!",
            english_translation="The adventures of Doraemon and his friends are getting more thrilling by the minute; don't miss out, kids!",
            created_at=datetime.datetime(2026, 7, 6, 15, 2, 49, tzinfo=datetime.timezone.utc),
            source=None
        )

    Scenario B: Fully Hydrated Representation (Source object loaded via DB JOIN)
        example = DictionaryExample(
            example_id=504,
            word_id=88,
            source_id=14,
            sentence="Doraemon và nhóm bạn càng lúc càng gay cấn, các em đừng bỏ lỡ nhé!",
            english_translation="The adventures of Doraemon and his friends are getting more thrilling by the minute; don't miss out, kids!",
            created_at=datetime.datetime(2026, 7, 6, 15, 2, 49, tzinfo=datetime.timezone.utc),
            source=DictionarySource(
                source_id=14,
                source_type="comic",
                title="Doraemon Tập 1"
            )
        )

Classes:
    DictionaryExample: Captures a single contextual sentence instance and its translation.
"""

from datetime import datetime
from typing import Optional

from app.domain.dictionary_source import DictionarySource


class DictionaryExample:
    """Represents a single real-life contextual example of a dictionary word.

    This class captures the base sentence context along with its parallel English
    translation mapping, completely isolated from raw database layer structures.
    Every example strictly enforces the inclusion of an underlying metadata source.
    """

    def __init__(
            self,
            example_id: Optional[int],
            word_id: int,
            source_id: int,
            sentence: str,
            english_translation: str,
            created_at: datetime,
            source: Optional[DictionarySource] = None
    ) -> None:
        """Initializes a new DictionaryExample instance with all required attributes.

        Args:
            example_id (Optional[int]): The unique database identifier.
            word_id (int): Foreign key tracing back to the aggregate parent word.
            source_id (int): Foreign key tracking back to the required origin source document.
            sentence (str): The raw target language contextual sentence.
            english_translation (str): The English translation companion meaning.
            created_at (datetime): Timestamp when this context was imported.
            source (Optional[DictionarySource]): Hydrated domain entity of the source. Defaults to None.
        """
        self.id = example_id
        self.word_id = word_id
        self.source_id = source_id
        self.sentence = sentence
        self.english_translation = english_translation
        self.created_at = created_at  # Sourced from the database
        self.source = source
