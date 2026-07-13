"""Defines the User domain model representing an administrative identity block.

This module isolates the clean domain representation of credentials required
to clear identity boundary operations inside the session orchestration flow.

Domain Instantiation Examples:

    Scenario A: Domain Instantiation (Ready for cryptographic verification)
        user = User(
            user_id=1,
            username="admin_damian",
            password_hash="$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Bw59G..."
        )

Classes:
    User: Captures a single operator security profile and context block.
"""

from typing import Optional


class User:
    """Represents a single system identity profile authorized to pass access controls.

    This class captures identity metrics independent of the underlying persistence engine,
    serving as the structural data container during credential validation workflows.
    """

    def __init__(
            self,
            user_id: Optional[int],
            username: str,
            password_hash: str
    ) -> None:
        """Initializes a new User domain record with validation fields.

        Args:
            user_id (Optional[int]): The unique database identity key.
            username (str): The unique canonical system identification handle.
            password_hash (str): The secure string digest verifying account authority.
        """
        self.id = user_id
        self.username = username
        self.password_hash = password_hash
