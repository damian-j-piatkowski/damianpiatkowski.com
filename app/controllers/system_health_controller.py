"""Controller for the admin System Health module."""

from typing import Tuple, Union

from flask import Response as FlaskResponse
from flask import jsonify, render_template

from app import db
from app.services.system_health_service import SystemHealthService, VALID_HISTORY_RANGES


def render_system_health_page(tab: str = "live") -> Tuple[str, int]:
    """Render the System Health admin page with live or trends tab."""
    active_tab = tab if tab in {"live", "trends"} else "live"
    html = render_template(
        "admin/system_health.html",
        active_tab=active_tab,
        history_ranges=VALID_HISTORY_RANGES,
    )
    return html, 200


def system_health_stats() -> Tuple[FlaskResponse, int]:
    """Return current node metrics as JSON."""
    service = SystemHealthService(db.session)
    metrics = service.get_node_metrics()
    return jsonify(metrics), 200


def system_health_history(range_key: str) -> Tuple[FlaskResponse, int]:
    """Return historical metric series as JSON for Chart.js."""
    service = SystemHealthService(db.session)
    try:
        payload = service.get_historical_metrics(range_key)
    except ValueError as exc:
        return jsonify({"success": False, "message": str(exc)}), 400
    return jsonify(payload), 200
