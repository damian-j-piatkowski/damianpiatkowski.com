"""Controller for admin login and logout workflows."""

from typing import Optional, Tuple

from flask import Response as FlaskResponse
from flask import flash, redirect, render_template, url_for

from app import db
from app.exceptions import AuthenticationError
from app.models.repositories.user_repository import UserRepository
from app.services import auth_service


def show_login_page(next_url: Optional[str] = None) -> Tuple[str, int]:
    """Render the admin login page."""
    if auth_service.is_admin_authenticated():
        return redirect(next_url or url_for("dictionary.render_dictionary_page")), 302
    html = render_template("admin/login.html", next_url=next_url or "")
    return html, 200


def login_admin(
        username: str,
        password: str,
        next_url: Optional[str] = None,
) -> Tuple[FlaskResponse, int]:
    """Authenticate the administrator and redirect on success."""
    repository = UserRepository(db.session)
    try:
        auth_service.authenticate_admin(repository, username, password)
    except AuthenticationError as exc:
        flash(exc.message, "error")
        html = render_template("admin/login.html", next_url=next_url or "", username=username)
        return html, 401

    destination = next_url if next_url and next_url.startswith("/") else url_for(
        "dictionary.render_dictionary_page"
    )
    return redirect(destination), 302


def logout_admin() -> Tuple[FlaskResponse, int]:
    """Clear the admin session and redirect to the login page."""
    auth_service.logout_admin()
    flash("You have been logged out.", "success")
    return redirect(url_for("admin.admin_login")), 302
