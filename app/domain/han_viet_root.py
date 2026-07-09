"""Defines the HanVietRoot domain model tracking semantic sub-word components.

This module isolates the clean business representation of Sino-Vietnamese components,
allowing for complex linguistic breakdown analysis without hitting storage layers.

Domain Instantiation Examples:

    1. Initialization Arguments:
       root_entry = HanVietRoot(
           root_id=42,
           root="bản",
           chinese_character="本",
           root_meaning="root, basis, foundation"
       )

    2. Resulting Domain Instance State:
       root_entry.id -> 42
       root_entry.root -> "bản"
       root_entry.chinese_character -> "本"
       root_entry.root_meaning -> "root, basis, foundation"

Classes:
    HanVietRoot: Models a distinct Chinese structural semantic root component.
"""

from typing import Optional


class HanVietRoot:
    """Represents a single Hán Việt semantic root character component pattern.

    This class encapsulates foundational structural particles to reveal underlying
    etymological patterns, keeping storage logic decoupled from business definitions.
    """

    def __init__(
            self,
            root_id: Optional[int],
            root: str,
            chinese_character: str,  # Strictly required at the domain boundary
            root_meaning: str
    ) -> None:
        """Initializes a new HanVietRoot component snapshot instance.

        Args:
            root_id (Optional[int]): The unique database identifier. Evaluates to None for
                new transient instances before they are written to the storage engine.
            root (str): The lowercase standard Vietnamese script root spelling.
            chinese_character (str): Corresponding logogram character.
            root_meaning (str): Core target definitions linked with this element.
        """
        self.id = root_id
        self.root = root
        self.chinese_character = chinese_character
        self.root_meaning = root_meaning
