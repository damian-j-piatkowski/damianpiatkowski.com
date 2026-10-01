"""Repository for Hán Việt roots and word-root associations."""

from typing import Dict, List, Optional

from sqlalchemy import delete, func, insert, select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from app.domain.han_viet_root import HanVietRoot
from app.exceptions import HanVietRootNotFoundError
from app.models.tables.han_viet_root import han_viet_roots
from app.models.tables.word_han_viet_association import word_han_viet_association


class HanVietRepository:
    """Persistence access for han_viet_roots and word_han_viet_association."""

    def __init__(self, session: Session) -> None:
        self.session = session

    @staticmethod
    def _hydrate(row) -> HanVietRoot:
        return HanVietRoot(
            root_id=row.id,
            root=row.root,
            chinese_character=row.chinese_character,
            root_meaning=row.root_meaning,
        )

    def find_by_root(self, root: str) -> Optional[HanVietRoot]:
        """Look up a single root by its Vietnamese root text."""
        try:
            row = self.session.execute(
                select(han_viet_roots).where(han_viet_roots.c.root == root)
            ).fetchone()
            return self._hydrate(row) if row else None
        except SQLAlchemyError as exc:
            raise RuntimeError(f"Failed to look up root '{root}': {exc}") from exc

    def find_by_roots(self, roots: List[str]) -> Dict[str, HanVietRoot]:
        """Batch-lookup roots by a list of syllable strings."""
        if not roots:
            return {}
        try:
            rows = self.session.execute(
                select(han_viet_roots).where(han_viet_roots.c.root.in_(roots))
            ).fetchall()
            return {row.root: self._hydrate(row) for row in rows}
        except SQLAlchemyError as exc:
            raise RuntimeError(f"Failed batch root lookup: {exc}") from exc

    def get_by_id(self, root_id: int) -> HanVietRoot:
        """Load a Hán Việt root by primary key."""
        try:
            row = self.session.execute(
                select(han_viet_roots).where(han_viet_roots.c.id == root_id)
            ).fetchone()
            if row is None:
                raise HanVietRootNotFoundError(
                    f"Hán Việt root id={root_id} was not found.",
                    root_id=root_id,
                )
            return self._hydrate(row)
        except HanVietRootNotFoundError:
            raise
        except SQLAlchemyError as exc:
            raise RuntimeError(f"Failed to load root id={root_id}: {exc}") from exc

    def create(self, root: str, chinese_character: str, root_meaning: str) -> HanVietRoot:
        """Insert a new Hán Việt root."""
        try:
            result = self.session.execute(
                insert(han_viet_roots).values(
                    root=root,
                    chinese_character=chinese_character,
                    root_meaning=root_meaning,
                )
            )
            self.session.flush()
            return self.get_by_id(result.inserted_primary_key[0])
        except IntegrityError as exc:
            raise RuntimeError(f"Hán Việt root '{root}' already exists.") from exc
        except SQLAlchemyError as exc:
            raise RuntimeError(f"Failed to create root '{root}': {exc}") from exc

    def delete(self, root_id: int) -> None:
        """Permanently delete a Hán Việt root row."""
        try:
            result = self.session.execute(
                delete(han_viet_roots).where(han_viet_roots.c.id == root_id)
            )
            if result.rowcount == 0:
                raise HanVietRootNotFoundError(
                    f"Hán Việt root id={root_id} was not found.",
                    root_id=root_id,
                )
            self.session.flush()
        except HanVietRootNotFoundError:
            raise
        except SQLAlchemyError as exc:
            raise RuntimeError(f"Failed to delete root id={root_id}: {exc}") from exc

    def count_associations(self, root_id: int) -> int:
        """Count word associations for a given root."""
        try:
            count = self.session.execute(
                select(func.count())
                .select_from(word_han_viet_association)
                .where(word_han_viet_association.c.root_id == root_id)
            ).scalar()
            return int(count or 0)
        except SQLAlchemyError as exc:
            raise RuntimeError(
                f"Failed to count associations for root id={root_id}: {exc}"
            ) from exc

    def associate(self, word_id: int, root_id: int) -> None:
        """Create a word/root association; ignore duplicates via composite PK."""
        try:
            existing = self.session.execute(
                select(word_han_viet_association.c.word_id).where(
                    word_han_viet_association.c.word_id == word_id,
                    word_han_viet_association.c.root_id == root_id,
                )
            ).fetchone()
            if existing is not None:
                return
            self.session.execute(
                insert(word_han_viet_association).values(word_id=word_id, root_id=root_id)
            )
            self.session.flush()
        except SQLAlchemyError as exc:
            raise RuntimeError(
                f"Failed to associate word id={word_id} with root id={root_id}: {exc}"
            ) from exc

    def unlink(self, word_id: int, root_id: int) -> None:
        """Remove only the association row; leave the root intact."""
        try:
            self.session.execute(
                delete(word_han_viet_association).where(
                    word_han_viet_association.c.word_id == word_id,
                    word_han_viet_association.c.root_id == root_id,
                )
            )
            self.session.flush()
        except SQLAlchemyError as exc:
            raise RuntimeError(
                f"Failed to unlink word id={word_id} from root id={root_id}: {exc}"
            ) from exc

    def count_roots(self) -> int:
        """Return the total number of Hán Việt roots."""
        try:
            return int(
                self.session.execute(
                    select(func.count()).select_from(han_viet_roots)
                ).scalar()
                or 0
            )
        except SQLAlchemyError as exc:
            raise RuntimeError(f"Failed to count Hán Việt roots: {exc}") from exc

    def count_distinct_chinese_characters(self) -> int:
        """Return the number of distinct Chinese characters across roots."""
        try:
            return int(
                self.session.execute(
                    select(func.count(func.distinct(han_viet_roots.c.chinese_character)))
                ).scalar()
                or 0
            )
        except SQLAlchemyError as exc:
            raise RuntimeError(
                f"Failed to count distinct Chinese characters: {exc}"
            ) from exc

    def list_top_reused_roots(self, limit: int = 10) -> List[Dict[str, object]]:
        """Return roots ordered by association reuse count."""
        try:
            stmt = (
                select(
                    han_viet_roots.c.id,
                    han_viet_roots.c.root,
                    han_viet_roots.c.chinese_character,
                    han_viet_roots.c.root_meaning,
                    func.count(word_han_viet_association.c.word_id).label("usage_count"),
                )
                .outerjoin(
                    word_han_viet_association,
                    word_han_viet_association.c.root_id == han_viet_roots.c.id,
                )
                .group_by(han_viet_roots.c.id)
                .order_by(func.count(word_han_viet_association.c.word_id).desc())
                .limit(limit)
            )
            rows = self.session.execute(stmt).fetchall()
            return [
                {
                    "id": row.id,
                    "root": row.root,
                    "chinese_character": row.chinese_character,
                    "root_meaning": row.root_meaning,
                    "usage_count": int(row.usage_count or 0),
                }
                for row in rows
            ]
        except SQLAlchemyError as exc:
            raise RuntimeError(f"Failed to list top reused roots: {exc}") from exc

    def list_orphan_roots(self) -> List[HanVietRoot]:
        """Return roots with no word associations."""
        try:
            associated = select(word_han_viet_association.c.root_id).distinct()
            rows = self.session.execute(
                select(han_viet_roots)
                .where(han_viet_roots.c.id.not_in(associated))
                .order_by(han_viet_roots.c.root.asc())
            ).fetchall()
            return [self._hydrate(row) for row in rows]
        except SQLAlchemyError as exc:
            raise RuntimeError(f"Failed to list orphan roots: {exc}") from exc
