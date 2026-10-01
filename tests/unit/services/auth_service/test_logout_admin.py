"""Unit tests for auth_service.logout_admin.

Tests included:
    - test_logout_admin_clears_session: Verifies admin session keys are removed.
"""

import pytest

from app.services.auth_service import logout_admin


@pytest.mark.dictionary
def test_logout_admin_clears_session(app):
    """Verifies that logout_admin removes is_admin and admin_username from the session."""
    with app.test_request_context("/admin/logout"):
        from flask import session as flask_session
        flask_session["is_admin"] = True
        flask_session["admin_username"] = "admin"
        logout_admin()
        assert "is_admin" not in flask_session
        assert "admin_username" not in flask_session
