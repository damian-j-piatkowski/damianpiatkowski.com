"""Unit tests for dictionary word validation rules."""

import pytest

from app.exceptions import DictionaryValidationError
from app.services.dictionary_validation import validate_viet_word, validate_word_types
from app.services.han_viet_service import split_syllables


@pytest.mark.dictionary
@pytest.mark.parametrize(
    "raw,expected",
    [
        ("  báo cáo  ", "báo cáo"),
        ("nghiệm", "nghiệm"),
        ("học-tập", "học-tập"),
    ],
)
def test_validate_viet_word_accepts_valid_input(raw, expected):
    assert validate_viet_word(raw) == expected


@pytest.mark.dictionary
@pytest.mark.parametrize(
    "raw",
    ["", "   ", "hello123", "báo!", "word_with_underscore"],
)
def test_validate_viet_word_rejects_invalid_input(raw):
    with pytest.raises(DictionaryValidationError):
        validate_viet_word(raw)


@pytest.mark.dictionary
def test_validate_word_types_accepts_enum_values():
    assert validate_word_types(["noun", "verb"]) == ["noun", "verb"]


@pytest.mark.dictionary
def test_validate_word_types_rejects_unknown_values():
    with pytest.raises(DictionaryValidationError):
        validate_word_types(["noun", "not-a-type"])


@pytest.mark.dictionary
def test_split_syllables_preserves_diacritics():
    assert split_syllables("chính trị") == ["chính", "trị"]
    assert split_syllables("nghiệm") == ["nghiệm"]
    assert split_syllables("  học   tập ") == ["học", "tập"]
