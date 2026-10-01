"""Admin authentication helpers and route protection."""

from functools import wraps
from typing import Any, Callable

from flask import redirect, request, session, url_for, jsonify


def admin_required(view: Callable[..., Any]) -> Callable[..., Any]:
    """Require an authenticated admin session for the wrapped view.

    Browser HTML page requests are redirected to the admin login page.
    JSON/AJAX requests receive HTTP 401.
    """

    @wraps(view)
    def wrapped(*args: Any, **kwargs: Any) -> Any:
        if session.get("is_admin") is True:
            return view(*args, **kwargs)

        accepts_json = (
            request.accept_mimetypes.best
            and "application/json" in request.accept_mimetypes.best
        )
        wants_json = (
            request.is_json
            or request.method in {"POST", "PUT", "PATCH", "DELETE"}
            or accepts_json
            or request.headers.get("X-Requested-With") == "XMLHttpRequest"
            or request.headers.get("Accept", "").startswith("application/json")
        )
        if wants_json:
            return jsonify({"success": False, "message": "Authentication required"}), 401

        return redirect(url_for("admin.admin_login", next=request.path))

    return wrapped
