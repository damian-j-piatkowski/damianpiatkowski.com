from datetime import datetime
import pytest
from marshmallow import ValidationError
from app.api_schemas.log_schema import LogSchema


@pytest.fixture
def valid_log_data():
    return {
        "level": "INFO",
        "message": "This is a log message."
    }


def test_log_schema_valid(valid_log_data):
    schema = LogSchema()
    result = schema.load(valid_log_data)
    assert result == valid_log_data


def test_log_schema_missing_level(valid_log_data):
    schema = LogSchema()
    valid_log_data.pop("level")
    with pytest.raises(ValidationError) as excinfo:
        schema.load(valid_log_data)
    assert "level" in excinfo.value.messages
    assert "Missing data for required field." in excinfo.value.messages["level"]


def test_log_schema_empty_level(valid_log_data):
    schema = LogSchema()
    valid_log_data["level"] = ""
    with pytest.raises(ValidationError) as excinfo:
        schema.load(valid_log_data)
    assert "level" in excinfo.value.messages
    assert "Shorter than minimum length 1." in excinfo.value.messages["level"]


def test_log_schema_missing_message(valid_log_data):
    schema = LogSchema()
    valid_log_data.pop("message")
    with pytest.raises(ValidationError) as excinfo:
        schema.load(valid_log_data)
    assert "message" in excinfo.value.messages
    assert "Missing data for required field." in excinfo.value.messages["message"]


def test_log_schema_timestamp_dumps(valid_log_data):
    schema = LogSchema()
    log_data_with_timestamp = valid_log_data.copy()
    log_data_with_timestamp["timestamp"] = datetime(2023, 7, 2, 12, 0, 0)
    result = schema.dump(log_data_with_timestamp)
    assert "timestamp" in result
    assert result["timestamp"] == "2023-07-02T12:00:00"
