"""Unit tests for auth_service.hash_password.

Tests included:
    - test_hash_password_returns_werkzeug_hash: Verifies hashed output differs from input.
"""

import pytest
from werkzeug.security import check_password_hash

from app.services.auth_service import hash_password


@pytest.mark.dictionary
def test_hash_password_returns_werkzeug_hash():
    """Verifies that hash_password returns a Werkzeug hash that validates the password."""
    hashed = hash_password("secret")
    assert hashed != "secret"
    assert check_password_hash(hashed, "secret")
