"""Unit tests for auth_service.authenticate_admin.

Tests included:
    - test_authenticate_admin_success: Verifies session flags after success.
    - test_authenticate_admin_rejects_bad_password: Verifies AuthenticationError.
"""

import pytest

from app.exceptions import AuthenticationError
from app.models.repositories.user_repository import UserRepository
from app.services.auth_service import authenticate_admin, hash_password


@pytest.mark.dictionary
def test_authenticate_admin_success(app, session):
    """Verifies that valid credentials establish an admin session."""
    repo = UserRepository(session)
    repo.create_user(username="admin", password_hash=hash_password("secret"))
    session.flush()

    with app.test_request_context("/admin/login"):
        authenticate_admin(repo, "admin", "secret")
        from flask import session as flask_session
        assert flask_session.get("is_admin") is True
        assert flask_session.get("admin_username") == "admin"


@pytest.mark.dictionary
def test_authenticate_admin_rejects_bad_password(app, session):
    """Verifies that invalid credentials raise AuthenticationError."""
    repo = UserRepository(session)
    repo.create_user(username="admin", password_hash=hash_password("secret"))
    session.flush()

    with app.test_request_context("/admin/login"):
        with pytest.raises(AuthenticationError):
            authenticate_admin(repo, "admin", "wrong")
