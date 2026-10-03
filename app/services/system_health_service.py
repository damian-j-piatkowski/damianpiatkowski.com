"""Service for live and historical system health metrics."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List

from flask import current_app
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.exceptions import EmailSendError
from app.models.repositories.system_health_log_repository import SystemHealthLogRepository
from app.models.tables.system_health_log import system_health_logs
from app.services import email_service

VALID_HISTORY_RANGES = ("24h", "7d", "30d", "90d", "180d")

CPU_ALERT_THRESHOLD = 90.0
RAM_ALERT_THRESHOLD = 85.0
DISK_ALERT_THRESHOLD = 90.0
ALERT_COOLDOWN = timedelta(hours=1)


class SystemHealthService:
    """Collects node metrics, serves history charts, and processes cron snapshots."""

    def __init__(self, session: Session) -> None:
        self.session = session
        self.repository = SystemHealthLogRepository(session)

    def get_node_metrics(self) -> Dict[str, Any]:
        """Return current node metrics; mock in development/testing, psutil in production."""
        if self._uses_mock_metrics():
            return self._mock_metrics()
        return self._psutil_metrics()

    def get_historical_metrics(self, range_key: str) -> Dict[str, List]:
        """Return Chart.js-ready historical series for the given range key."""
        if range_key not in VALID_HISTORY_RANGES:
            raise ValueError(f"Unsupported health history range '{range_key}'")

        now = datetime.now(timezone.utc)
        if range_key == "24h":
            cutoff = now - timedelta(hours=24)
            rows = self.repository.list_since(cutoff)
            payload = {
                "labels": [self._format_label(row["timestamp"]) for row in rows],
                "cpu": [row["cpu_percent"] for row in rows],
                "ram": [row["ram_percent"] for row in rows],
                "swap": [row["swap_percent"] for row in rows],
                "disk": [row["disk_percent"] for row in rows],
            }
        else:
            if range_key == "7d":
                cutoff = now - timedelta(days=7)
                bucket_expr = func.date_format(system_health_logs.c.timestamp, "%Y-%m-%d %H:00")
            elif range_key == "30d":
                cutoff = now - timedelta(days=30)
                bucket_expr = func.date_format(
                    func.from_unixtime(
                        func.floor(func.unix_timestamp(system_health_logs.c.timestamp) / (6 * 3600))
                        * (6 * 3600)
                    ),
                    "%Y-%m-%d %H:00",
                )
            elif range_key == "90d":
                cutoff = now - timedelta(days=90)
                bucket_expr = func.date_format(system_health_logs.c.timestamp, "%Y-%m-%d")
            else:  # 180d
                cutoff = now - timedelta(days=180)
                bucket_expr = func.date_format(system_health_logs.c.timestamp, "%Y-%m-%d")
            rows = self.repository.list_bucketed(cutoff, bucket_expr)
            payload = {
                "labels": [row["bucket"] for row in rows],
                "cpu": [round(row["cpu_percent"], 2) for row in rows],
                "ram": [round(row["ram_percent"], 2) for row in rows],
                "swap": [round(row["swap_percent"], 2) for row in rows],
                "disk": [round(row["disk_percent"], 2) for row in rows],
            }

        if self._uses_mock_metrics() and not payload["labels"]:
            return self._mock_historical_metrics(range_key, now)
        return payload

    def process_15min_snapshot(self) -> Dict[str, Any]:
        """Capture metrics, persist (except development), alert on thresholds, prune."""
        if self._skip_snapshot_persistence():
            metrics = self.get_node_metrics()
            return {
                "persisted": False,
                "alert_sent": False,
                "pruned": 0,
                "metrics": metrics,
                "reason": "snapshot persistence skipped in development",
            }

        metrics = self.get_node_metrics()

        should_alert = self._thresholds_exceeded(metrics) and not self._alert_within_cooldown()
        alert_sent = False
        if should_alert:
            subject = "System health alert"
            body = (
                f"Threshold exceeded at {datetime.now(timezone.utc).isoformat()}\n"
                f"CPU: {metrics['cpu_percent']:.1f}%\n"
                f"RAM: {metrics['ram_percent']:.1f}%\n"
                f"Swap: {metrics['swap_percent']:.1f}%\n"
                f"Disk: {metrics['disk_percent']:.1f}%\n"
                f"Environment: {metrics.get('environment')}\n"
            )
            try:
                email_service.send_system_health_alert(subject, body)
                alert_sent = True
            except EmailSendError:
                current_app.logger.exception("Failed to send system health alert")

        row = self.repository.insert(
            cpu_percent=metrics["cpu_percent"],
            ram_percent=metrics["ram_percent"],
            ram_used_mb=metrics["ram_used_mb"],
            swap_percent=metrics["swap_percent"],
            disk_percent=metrics["disk_percent"],
            alert_sent=alert_sent,
        )
        pruned = self.repository.prune_older_than(days=180)
        self.session.commit()

        return {
            "persisted": True,
            "alert_sent": alert_sent,
            "pruned": pruned,
            "row_id": row["id"],
            "metrics": metrics,
        }

    def _uses_mock_metrics(self) -> bool:
        if current_app.config.get("TESTING"):
            return True
        env = (current_app.config.get("FLASK_ENV") or "").lower()
        return env in {"development", "testing"}

    def _skip_snapshot_persistence(self) -> bool:
        """Skip DB writes in local development; always persist in production and tests."""
        if current_app.config.get("TESTING"):
            return False
        env = (current_app.config.get("FLASK_ENV") or "").lower()
        return env == "development"

    @staticmethod
    def _mock_metrics() -> Dict[str, Any]:
        """Realistic ~1GB Lightsail-style mock metrics for local/CI."""
        return {
            "cpu_percent": 12.5,
            "ram_percent": 48.0,
            "ram_used_mb": 480.0,
            "ram_total_mb": 1000.0,
            "swap_percent": 5.0,
            "disk_percent": 42.0,
            "uptime": "3d 4h 12m",
            "os_info": "Mock Linux 6.1.0 (dev)",
            "environment": "DEV MOCK",
        }

    @staticmethod
    def _mock_historical_metrics(range_key: str, now: datetime) -> Dict[str, List]:
        """Synthetic Chart.js series for empty development/testing history."""
        configs = {
            "24h": (96, timedelta(minutes=15), "%Y-%m-%d %H:%M"),
            "7d": (168, timedelta(hours=1), "%Y-%m-%d %H:00"),
            "30d": (120, timedelta(hours=6), "%Y-%m-%d %H:00"),
            "90d": (90, timedelta(days=1), "%Y-%m-%d"),
            "180d": (180, timedelta(days=1), "%Y-%m-%d"),
        }
        count, step, label_fmt = configs[range_key]
        labels: List[str] = []
        cpu: List[float] = []
        ram: List[float] = []
        swap: List[float] = []
        disk: List[float] = []
        start = now - (step * (count - 1))
        for index in range(count):
            point = start + (step * index)
            labels.append(point.strftime(label_fmt))
            wave = (index % 12) - 6
            cpu.append(round(max(4.0, min(88.0, 18.0 + wave * 2.5 + (index % 5))), 2))
            ram.append(round(max(20.0, min(82.0, 45.0 + wave * 1.8 + ((index // 3) % 4))), 2))
            swap.append(round(max(0.0, min(40.0, 6.0 + (index % 7))), 2))
            disk.append(round(max(30.0, min(70.0, 42.0 + (index % 9) * 0.4)), 2))
        return {"labels": labels, "cpu": cpu, "ram": ram, "swap": swap, "disk": disk}

    @staticmethod
    def _psutil_metrics() -> Dict[str, Any]:
        import platform
        import psutil

        # Non-blocking sample; first call after process start may be 0.0.
        cpu_percent = float(psutil.cpu_percent(interval=None))
        virtual = psutil.virtual_memory()
        swap = psutil.swap_memory()
        disk = psutil.disk_usage("/")
        boot = datetime.fromtimestamp(psutil.boot_time(), tz=timezone.utc)
        uptime_delta = datetime.now(timezone.utc) - boot

        return {
            "cpu_percent": cpu_percent,
            "ram_percent": float(virtual.percent),
            "ram_used_mb": round(virtual.used / (1024 * 1024), 1),
            "ram_total_mb": round(virtual.total / (1024 * 1024), 1),
            "swap_percent": float(swap.percent),
            "disk_percent": float(disk.percent),
            "uptime": SystemHealthService._format_uptime(uptime_delta),
            "os_info": f"{platform.system()} {platform.release()}",
            "environment": "PRODUCTION",
        }

    @staticmethod
    def _format_uptime(delta: timedelta) -> str:
        total_seconds = int(delta.total_seconds())
        days, rem = divmod(total_seconds, 86400)
        hours, rem = divmod(rem, 3600)
        minutes, _ = divmod(rem, 60)
        parts = []
        if days:
            parts.append(f"{days}d")
        if hours or days:
            parts.append(f"{hours}h")
        parts.append(f"{minutes}m")
        return " ".join(parts)

    @staticmethod
    def _format_label(value: datetime) -> str:
        if value.tzinfo is None:
            value = value.replace(tzinfo=timezone.utc)
        return value.astimezone(timezone.utc).strftime("%Y-%m-%d %H:%M")

    @staticmethod
    def _thresholds_exceeded(metrics: Dict[str, Any]) -> bool:
        return (
            metrics["cpu_percent"] > CPU_ALERT_THRESHOLD
            or metrics["ram_percent"] > RAM_ALERT_THRESHOLD
            or metrics["disk_percent"] > DISK_ALERT_THRESHOLD
        )

    def _alert_within_cooldown(self) -> bool:
        last = self.repository.last_alert_sent_at()
        if last is None:
            return False
        if last.tzinfo is None:
            last = last.replace(tzinfo=timezone.utc)
        return datetime.now(timezone.utc) - last < ALERT_COOLDOWN
