"""Unit tests for word_service.order_etymology_components.

Tests included:
    - test_order_etymology_components_follows_syllables: Verifies syllable order.
    - test_order_etymology_components_skips_unlinked: Verifies unlinked syllables skip.
"""

from app.domain.dictionary_word import DictionaryWord
from app.domain.han_viet_root import HanVietRoot
from app.services.word_service import order_etymology_components


def test_order_etymology_components_follows_syllables():
    """Verifies that etymology components are ordered by viet_word syllables."""
    word = DictionaryWord(
        word_id=1,
        viet_word="chính trị",
        english_translation="politics",
        han_viet_roots=[
            HanVietRoot(2, "trị", "治", "govern"),
            HanVietRoot(1, "chính", "正", "main"),
        ],
    )
    ordered = order_etymology_components(word)
    assert [item["root"] for item in ordered] == ["chính", "trị"]


def test_order_etymology_components_skips_unlinked():
    """Verifies that syllables without a linked root are omitted from the list."""
    word = DictionaryWord(
        word_id=1,
        viet_word="chính trị",
        english_translation="politics",
        han_viet_roots=[
            HanVietRoot(1, "chính", "正", "main"),
        ],
    )
    ordered = order_etymology_components(word)
    assert [item["root"] for item in ordered] == ["chính"]
