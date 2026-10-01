"""Admin authentication service using signed Flask sessions."""

from typing import Optional

from flask import session
from werkzeug.security import check_password_hash, generate_password_hash

from app.exceptions import AuthenticationError
from app.models.repositories.user_repository import UserRepository


def hash_password(password: str) -> str:
    """Hash a plaintext password for storage."""
    return generate_password_hash(password)


def authenticate_admin(user_repository: UserRepository, username: str, password: str) -> None:
    """Validate credentials and establish an admin session.

    Raises:
        AuthenticationError: If the username or password is invalid.
    """
    user = user_repository.find_by_username(username.strip())
    if user is None or not check_password_hash(user.password_hash, password):
        raise AuthenticationError()

    session.clear()
    session["is_admin"] = True
    session["admin_username"] = user.username


def logout_admin() -> None:
    """Clear the authenticated admin session."""
    session.pop("is_admin", None)
    session.pop("admin_username", None)


def is_admin_authenticated() -> bool:
    """Return whether the current session is an authenticated admin."""
    return session.get("is_admin") is True


def current_admin_username() -> Optional[str]:
    """Return the username stored in the admin session, if any."""
    return session.get("admin_username")
