"""Unit tests for the User domain model.

These tests verify the correct initialization and attribute handling of
User instances, ensuring that administrative identity keys and cryptographic
hash variables are properly assigned at the domain boundary.

Scenarios included:
    - Ensure a User instance is initialized correctly with a valid database ID.
    - Ensure a new transient User instance handles a None value for its identifier.
    - Ensure various edge case configurations and string boundaries map cleanly via parametrization.
"""

from typing import Optional
import pytest
from app.domain.user import User


@pytest.mark.dictionary
def test_user_initialization_with_id() -> None:
    """Verifies that a User instance is initialized with all expected properties.

    This scenario ensures that database identity anchors, administrative system usernames,
    and cryptographic hash strings are properly assigned and exposed via standard attributes.
    """
    # Arrange & Act
    user_entry = User(
        user_id=1,
        username="admin_damian",
        password_hash="$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Bw59G..."
    )

    # Assert
    assert user_entry.id == 1
    assert user_entry.username == "admin_damian"
    assert user_entry.password_hash == "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Bw59G..."


@pytest.mark.dictionary
def test_user_transient_initialization_without_id() -> None:
    """Verifies that a new transient User instance initializes with a None identifier.

    This scenario ensures that business logic domains can instantiate new operator objects safely
    before they are committed to the database engine or storage layer.
    """
    # Arrange & Act
    transient_user = User(
        user_id=None,
        username="temp_maintainer",
        password_hash="$2b$12$v7aK8mF92hNqB4wLpXzR0u1v2w3x4y5z6a7b8c9d0e1f2g3h4i5j"
    )

    # Assert
    assert transient_user.id is None
    assert transient_user.username == "temp_maintainer"
    assert transient_user.password_hash == "$2b$12$v7aK8mF92hNqB4wLpXzR0u1v2w3x4y5z6a7b8c9d0e1f2g3h4i5j"


@pytest.mark.dictionary
@pytest.mark.parametrize(
    "user_id,username,password_hash",
    [
        # Case 1: Zero testing boundary
        (0, "system_root", "$2y$10$p3K7n2mF9..."),

        # Case 2: Negative ID testing boundary
        (-1, "fallback_admin", "$argon2id$v=19$m=65536,t=3,p=4$..."),

        # Case 3: Empty string values / whitespace variations
        (99, " ", "  "),

        # Case 4: Long descriptive text or character boundaries for names
        (500, "dev_administrator_automated_pipeline_runner_account", "short_mock_digest"),
    ],
    ids=[
        "zero_id",
        "negative_id",
        "whitespace_strings",
        "long_username_boundary"
    ]
)
def test_user_parameterized_edge_cases(
        user_id: Optional[int],
        username: str,
        password_hash: str
) -> None:
    """Verifies that parameterized edge case payloads map accurately to internal instance variables.

    This scenario tests boundary numbers, whitespace tokens, and extreme string lengths
    to guarantee the initializer handles structural variance without modification.
    """
    # Act
    user_entry = User(
        user_id=user_id,
        username=username,
        password_hash=password_hash
    )

    # Assert
    assert user_entry.id == user_id
    assert user_entry.username == username
    assert user_entry.password_hash == password_hash