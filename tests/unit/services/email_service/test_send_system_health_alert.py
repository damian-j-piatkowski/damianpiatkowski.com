"""Unit tests for send_system_health_alert."""

import pytest
from pytest_mock import MockerFixture

from app.exceptions import EmailSendError
from app.services.email_service import send_system_health_alert


def test_send_system_health_alert_success(app, mocker: MockerFixture):
    """Verifies that a configured mail stack sends the health alert message."""
    with app.app_context():
        mock_send = mocker.patch("app.services.email_service.mail.send")
        app.config["MAIL_USERNAME"] = "sender@example.com"
        app.config["MAIL_RECIPIENT"] = "ops@example.com"

        send_system_health_alert("Subject", "Body")

        mock_send.assert_called_once()
        message = mock_send.call_args[0][0]
        assert message.subject == "Subject"
        assert message.body == "Body"
        assert message.recipients == ["ops@example.com"]


def test_send_system_health_alert_missing_config(app, mocker: MockerFixture):
    """Verifies that incomplete mail config raises EmailSendError."""
    with app.app_context():
        mocker.patch("app.services.email_service.mail.send")
        app.config["MAIL_USERNAME"] = ""
        app.config["MAIL_RECIPIENT"] = ""

        with pytest.raises(EmailSendError, match="Email configuration is incomplete"):
            send_system_health_alert("Subject", "Body")
