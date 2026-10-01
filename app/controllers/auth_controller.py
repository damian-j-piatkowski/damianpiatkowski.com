"""Controller for admin login and logout workflows."""

from typing import Optional, Tuple, Union

from flask import Response as FlaskResponse
from flask import flash, redirect, render_template, url_for

from app import db
from app.auth.redirects import safe_internal_next_url
from app.exceptions import AuthenticationError
from app.models.repositories.user_repository import UserRepository
from app.services import auth_service


def _default_admin_destination() -> str:
    return url_for("admin.admin_home")


def _resolve_post_auth_destination(next_url: Optional[str]) -> str:
    return safe_internal_next_url(next_url) or _default_admin_destination()


def show_login_page(next_url: Optional[str] = None) -> Tuple[Union[str, FlaskResponse], int]:
    """Render the admin login page."""
    if auth_service.is_admin_authenticated():
        return redirect(_resolve_post_auth_destination(next_url)), 302
    safe_next = safe_internal_next_url(next_url) or ""
    html = render_template("admin/login.html", next_url=safe_next)
    return html, 200


def login_admin(
        username: str,
        password: str,
        next_url: Optional[str] = None,
) -> Tuple[Union[str, FlaskResponse], int]:
    """Authenticate the administrator and redirect on success."""
    repository = UserRepository(db.session)
    safe_next = safe_internal_next_url(next_url) or ""
    try:
        auth_service.authenticate_admin(repository, username, password)
    except AuthenticationError as exc:
        flash(exc.message, "error")
        html = render_template(
            "admin/login.html",
            next_url=safe_next,
            username=username,
        )
        return html, 401

    return redirect(_resolve_post_auth_destination(next_url)), 302


def logout_admin() -> Tuple[FlaskResponse, int]:
    """Clear the admin session and redirect to the login page."""
    auth_service.logout_admin()
    flash("You have been logged out.", "success")
    return redirect(url_for("admin.admin_login")), 302


def render_admin_home() -> Tuple[str, int]:
    """Render the admin tile landing page."""
    html = render_template("admin/home.html")
    return html, 200


def render_blog_wip() -> Tuple[str, int]:
    """Render the blog admin placeholder page."""
    html = render_template("admin/blog_wip.html")
    return html, 200


def render_dictionary_hub() -> Tuple[str, int]:
    """Render the dictionary admin hub."""
    html = render_template("admin/dictionary_hub.html")
    return html, 200
