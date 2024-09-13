"""Tests for the LogSchema.

This module contains tests for the LogSchema, validating the serialization
and deserialization of log data. It ensures that required fields are present,
fields have valid values, and that timestamps are correctly formatted.

Test functions:
- test_log_schema_empty_level: Tests schema when the level is empty.
- test_log_schema_missing_level: Tests schema when the level is missing.
- test_log_schema_missing_message: Tests schema when the message is missing.
- test_log_schema_timestamp_dumps: Tests schema timestamp serialization.
- test_log_schema_valid: Tests schema with valid log data.
"""

from datetime import datetime

import pytest
from marshmallow import ValidationError

from app.api_schemas.log_schema import LogSchema


def test_log_schema_empty_level(valid_log_data):
    """Test schema when the level is empty.

    This test ensures that the schema raises a ValidationError when the level
    field is present but contains an empty string.
    """
    schema = LogSchema()
    valid_log_data["level"] = ""
    with pytest.raises(ValidationError) as excinfo:
        schema.load(valid_log_data)
    assert "level" in excinfo.value.messages
    assert "Shorter than minimum length 1." in excinfo.value.messages["level"]


def test_log_schema_missing_level(valid_log_data):
    """Test schema when the level is missing.

    This test checks that the schema raises a ValidationError when the level
    field is missing from the input data.
    """
    schema = LogSchema()
    valid_log_data.pop("level")
    with pytest.raises(ValidationError) as excinfo:
        schema.load(valid_log_data)
    assert "level" in excinfo.value.messages
    assert "Missing data for required field." in excinfo.value.messages["level"]


def test_log_schema_missing_message(valid_log_data):
    """Test schema when the message is missing.

    This test validates that the schema raises a ValidationError when the
    message field is missing from the input data.
    """
    schema = LogSchema()
    valid_log_data.pop("message")
    with pytest.raises(ValidationError) as excinfo:
        schema.load(valid_log_data)
    assert "message" in excinfo.value.messages
    assert "Missing data for required field." in excinfo.value.messages[
        "message"]


def test_log_schema_timestamp_dumps(valid_log_data):
    """Test schema timestamp serialization.

    This test verifies that the schema correctly serializes the timestamp
    field to the expected ISO 8601 format when dumping data.
    """
    schema = LogSchema()
    log_data_with_timestamp = valid_log_data.copy()

    # Correct usage of datetime without overwriting
    log_data_with_timestamp["timestamp"] = datetime(2023, 7, 2, 12, 0, 0)
    result = schema.dump(log_data_with_timestamp)

    # Validate the timestamp format in the dumped data
    assert "timestamp" in result
    assert result["timestamp"] == "2023-07-02T12:00:00"


def test_log_schema_valid(valid_log_data):
    """Test schema with valid log data.

    This test validates that the schema correctly loads valid data without
    raising any validation errors.
    """
    schema = LogSchema()
    result = schema.load(valid_log_data)
    assert result == valid_log_data
