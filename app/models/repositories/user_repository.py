"""Repository for admin user credential lookups."""

from typing import Optional

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.domain.user import User
from app.models.tables.user import users


class UserRepository:
    """Persistence access for the users table."""

    def __init__(self, session: Session) -> None:
        self.session = session

    @staticmethod
    def _hydrate(row) -> User:
        return User(
            user_id=row.id,
            username=row.username,
            password_hash=row.password_hash,
        )

    def find_by_username(self, username: str) -> Optional[User]:
        """Return the user with the given username, or None."""
        try:
            row = self.session.execute(
                select(users).where(users.c.username == username)
            ).fetchone()
            return self._hydrate(row) if row else None
        except SQLAlchemyError as exc:
            raise RuntimeError(f"Failed to look up user '{username}': {exc}") from exc

    def create_user(self, username: str, password_hash: str) -> User:
        """Insert a new admin user and return the hydrated domain object."""
        try:
            result = self.session.execute(
                users.insert().values(username=username, password_hash=password_hash)
            )
            self.session.flush()
            row = self.session.execute(
                select(users).where(users.c.id == result.inserted_primary_key[0])
            ).fetchone()
            return self._hydrate(row)
        except SQLAlchemyError as exc:
            raise RuntimeError(f"Failed to create user '{username}': {exc}") from exc
