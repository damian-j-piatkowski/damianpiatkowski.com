"""Shared authentication helpers for admin integration tests."""

import pytest
from werkzeug.security import generate_password_hash

from app.models.repositories.user_repository import UserRepository


@pytest.fixture
def admin_user(session):
    """Insert a test administrator account."""
    repository = UserRepository(session)
    user = repository.create_user(
        username="admin",
        password_hash=generate_password_hash("secret"),
    )
    session.flush()
    return user


@pytest.fixture
def auth_client(client, admin_user):
    """Flask test client with an authenticated admin session."""
    with client.session_transaction() as sess:
        sess["is_admin"] = True
        sess["admin_username"] = admin_user.username
    return client
