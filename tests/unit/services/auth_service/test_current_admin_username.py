"""Unit tests for auth_service.current_admin_username.

Tests included:
    - test_current_admin_username_reads_session: Verifies username retrieval.
"""

import pytest

from app.services.auth_service import current_admin_username


@pytest.mark.dictionary
def test_current_admin_username_reads_session(app):
    """Verifies that current_admin_username returns the session username when set."""
    with app.test_request_context("/"):
        from flask import session as flask_session
        assert current_admin_username() is None
        flask_session["admin_username"] = "admin"
        assert current_admin_username() == "admin"
