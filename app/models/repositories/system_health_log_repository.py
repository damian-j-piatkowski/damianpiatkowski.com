"""Repository for system health metric snapshots."""

from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional

from sqlalchemy import delete, func, insert, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.models.tables.system_health_log import system_health_logs


class SystemHealthLogRepository:
    """Persistence access for system_health_logs."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def insert(
            self,
            *,
            cpu_percent: float,
            ram_percent: float,
            ram_used_mb: float,
            swap_percent: float,
            disk_percent: float,
            alert_sent: bool = False,
            timestamp: Optional[datetime] = None,
    ) -> Dict[str, Any]:
        """Insert a metric snapshot and return the hydrated row dict."""
        try:
            values: Dict[str, Any] = {
                "cpu_percent": cpu_percent,
                "ram_percent": ram_percent,
                "ram_used_mb": ram_used_mb,
                "swap_percent": swap_percent,
                "disk_percent": disk_percent,
                "alert_sent": alert_sent,
            }
            if timestamp is not None:
                values["timestamp"] = timestamp

            result = self.session.execute(insert(system_health_logs).values(**values))
            self.session.flush()
            row_id = result.inserted_primary_key[0]
            row = self.session.execute(
                select(system_health_logs).where(system_health_logs.c.id == row_id)
            ).fetchone()
            return self._hydrate(row)
        except SQLAlchemyError as exc:
            raise RuntimeError(f"Failed to insert system health log: {exc}") from exc

    def list_since(self, cutoff: datetime) -> List[Dict[str, Any]]:
        """Return snapshots at or after cutoff, oldest first."""
        try:
            rows = self.session.execute(
                select(system_health_logs)
                .where(system_health_logs.c.timestamp >= cutoff)
                .order_by(system_health_logs.c.timestamp.asc())
            ).fetchall()
            return [self._hydrate(row) for row in rows]
        except SQLAlchemyError as exc:
            raise RuntimeError(f"Failed to list system health logs: {exc}") from exc

    def list_bucketed(
            self,
            cutoff: datetime,
            bucket_expr,
    ) -> List[Dict[str, Any]]:
        """Return averaged metrics grouped by a SQL bucket expression."""
        try:
            stmt = (
                select(
                    bucket_expr.label("bucket"),
                    func.avg(system_health_logs.c.cpu_percent).label("cpu_percent"),
                    func.avg(system_health_logs.c.ram_percent).label("ram_percent"),
                    func.avg(system_health_logs.c.swap_percent).label("swap_percent"),
                    func.avg(system_health_logs.c.disk_percent).label("disk_percent"),
                )
                .where(system_health_logs.c.timestamp >= cutoff)
                .group_by(bucket_expr)
                .order_by(bucket_expr.asc())
            )
            rows = self.session.execute(stmt).fetchall()
            return [
                {
                    "bucket": str(row.bucket),
                    "cpu_percent": float(row.cpu_percent or 0.0),
                    "ram_percent": float(row.ram_percent or 0.0),
                    "swap_percent": float(row.swap_percent or 0.0),
                    "disk_percent": float(row.disk_percent or 0.0),
                }
                for row in rows
            ]
        except SQLAlchemyError as exc:
            raise RuntimeError(f"Failed to load bucketed health logs: {exc}") from exc

    def prune_older_than(self, days: int = 180) -> int:
        """Delete snapshots older than the retention window. Returns deleted count."""
        try:
            cutoff = datetime.now(timezone.utc) - timedelta(days=days)
            result = self.session.execute(
                delete(system_health_logs).where(system_health_logs.c.timestamp < cutoff)
            )
            self.session.flush()
            return int(result.rowcount or 0)
        except SQLAlchemyError as exc:
            raise RuntimeError(f"Failed to prune system health logs: {exc}") from exc

    def last_alert_sent_at(self) -> Optional[datetime]:
        """Return the timestamp of the most recent alert_sent snapshot, if any."""
        try:
            row = self.session.execute(
                select(system_health_logs.c.timestamp)
                .where(system_health_logs.c.alert_sent.is_(True))
                .order_by(system_health_logs.c.timestamp.desc())
                .limit(1)
            ).fetchone()
            if row is None:
                return None
            timestamp = row.timestamp
            if timestamp is not None and timestamp.tzinfo is None:
                timestamp = timestamp.replace(tzinfo=timezone.utc)
            return timestamp
        except SQLAlchemyError as exc:
            raise RuntimeError(f"Failed to load last health alert time: {exc}") from exc

    @staticmethod
    def _hydrate(row) -> Dict[str, Any]:
        timestamp = row.timestamp
        if timestamp is not None and timestamp.tzinfo is None:
            timestamp = timestamp.replace(tzinfo=timezone.utc)
        return {
            "id": row.id,
            "timestamp": timestamp,
            "cpu_percent": float(row.cpu_percent),
            "ram_percent": float(row.ram_percent),
            "ram_used_mb": float(row.ram_used_mb),
            "swap_percent": float(row.swap_percent),
            "disk_percent": float(row.disk_percent),
            "alert_sent": bool(row.alert_sent),
        }
