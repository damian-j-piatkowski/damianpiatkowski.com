"""CLI commands for system health snapshots."""

import click
from flask.cli import with_appcontext

from app import db
from app.services.system_health_service import SystemHealthService


@click.group("health")
def health_cli():
    """System health maintenance commands."""


@health_cli.command("process-snapshot")
@with_appcontext
def process_snapshot():
    """Capture a 15-minute health snapshot, alert on thresholds, and prune old logs."""
    service = SystemHealthService(db.session)
    result = service.process_15min_snapshot()
    if result.get("persisted"):
        click.echo(
            f"Snapshot saved (alert_sent={result.get('alert_sent')}, "
            f"pruned={result.get('pruned')})."
        )
    else:
        click.echo(result.get("reason", "Snapshot not persisted."))
