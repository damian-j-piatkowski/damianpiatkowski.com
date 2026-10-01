"""Unit tests for dictionary_validation.validate_word_types.

Tests included:
    - test_validate_word_types_empty_inputs: Verifies empty/None return [].
    - test_validate_word_types_accepts_and_normalizes: Verifies enum values, case, dedupe.
    - test_validate_word_types_rejects_unknown_values: Verifies rejection and field name.
"""

import pytest

from app.exceptions import DictionaryValidationError
from app.services.dictionary_validation import validate_word_types


@pytest.mark.dictionary
@pytest.mark.parametrize("raw", [None, [], ()])
def test_validate_word_types_empty_inputs(raw):
    """Verifies that missing or empty word type collections return an empty list."""
    assert validate_word_types(raw) == []


@pytest.mark.dictionary
def test_validate_word_types_accepts_and_normalizes():
    """Verifies that enum values are lowercased and de-duplicated in order."""
    assert validate_word_types(["Noun", "verb", "noun"]) == ["noun", "verb"]


@pytest.mark.dictionary
def test_validate_word_types_rejects_unknown_values():
    """Verifies that unsupported word types raise DictionaryValidationError on word_types."""
    with pytest.raises(DictionaryValidationError) as exc_info:
        validate_word_types(["noun", "not-a-type"])
    assert exc_info.value.field == "word_types"
