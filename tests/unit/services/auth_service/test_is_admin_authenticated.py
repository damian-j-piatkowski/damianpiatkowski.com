"""Unit tests for auth_service.is_admin_authenticated.

Tests included:
    - test_is_admin_authenticated_true_and_false: Verifies session flag detection.
"""

import pytest

from app.services.auth_service import is_admin_authenticated


@pytest.mark.dictionary
def test_is_admin_authenticated_true_and_false(app):
    """Verifies that is_admin_authenticated mirrors the session is_admin flag."""
    with app.test_request_context("/"):
        from flask import session as flask_session
        assert is_admin_authenticated() is False
        flask_session["is_admin"] = True
        assert is_admin_authenticated() is True
