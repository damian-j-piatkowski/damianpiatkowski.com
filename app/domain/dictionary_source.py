"""Defines the DictionarySource domain model tracking example citation origins.

This module isolates the clean domain representation of origin tracking documentation,
maintaining the descriptive context of where target text strings were harvested.

Domain Instantiation Examples:

    Scenario A: Physical Media (No URL footprint available)

        1. Initialization Arguments:
           source = DictionarySource(
               source_id=12,
               source_type=SourceType.BOOK,
               title="21 bài học cho thế kỷ 21",
               created_at=datetime.datetime(2026, 7, 8, 5, 20, 0, tzinfo=datetime.timezone.utc),
               url=None
           )

        2. Resulting Domain Instance State:
           source.id -> 12
           source.source_type -> SourceType.BOOK
           source.title -> "21 bài học cho thế kỷ 21"
           source.url -> None
           source.created_at -> datetime.datetime(2026, 7, 8, 5, 20, 0, ...)

    Scenario B: Digital Media (Full tracking link details provided)

        1. Initialization Arguments:
           source = DictionarySource(
               source_id=14,
               source_type=SourceType.ARTICLE,
               title="VnExpress - Messi điều chỉnh thế nào để giúp Argentina thắng ngược Ai Cập?",
               url="https://vnexpress.net/messi-dieu-chinh-the-nao-de-giup-argentina-thang-nguoc-ai-cap-5094933.html",
               created_at=datetime.datetime(2026, 7, 8, 5, 25, 0, tzinfo=datetime.timezone.utc)
           )

        2. Resulting Domain Instance State:
           source.id -> 14
           source.source_type -> SourceType.ARTICLE
           source.title -> "VnExpress - Messi điều chỉnh thế nào để giúp Argentina thắng ngược Ai Cập?"
           source.url -> "https://vnexpress.net/messi-dieu-chinh-the-nao-de-giup-argentina-thang-nguoc-ai-cap-5094933.html"
           source.created_at -> datetime.datetime(2026, 7, 8, 5, 25, 0, ...)

Classes:
    DictionarySource: Models the origin of a contextual exposure sentence.
"""

from datetime import datetime
from typing import Optional

from app.domain.domain_enums import SourceType


class DictionarySource:
    """Represents the origin documentation tracking where example context was mined.

    This class captures descriptive information about primary source materials, isolating
    the business layer representation cleanly from backend relational database engines.
    """

    def __init__(
            self,
            source_id: Optional[int],
            source_type: SourceType,  # Strictly enforces the domain Enum type
            title: str,
            created_at: datetime,
            url: Optional[str] = None
    ) -> None:
        """Initializes a new DictionarySource instance with all relevant attributes.

        Args:
            source_id (Optional[int]): The unique database identifier.
            source_type (SourceType): Centralized domain enum classification type.
            title (str): The descriptive name, title, or headline of the source.
            created_at (datetime): Timestamp when this source trace was compiled.
            url (Optional[str]): Optional web address locating the citation. Defaults to None.
        """
        self.id = source_id
        self.source_type = source_type
        self.title = title
        self.created_at = created_at
        self.url = url
