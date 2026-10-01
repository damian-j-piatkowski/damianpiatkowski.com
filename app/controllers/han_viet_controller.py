"""Controller for public Hán Việt root explorer pages."""

from typing import Tuple, Union

from flask import Response as FlaskResponse
from flask import abort, render_template

from app import db
from app.exceptions import HanVietRootNotFoundError
from app.services.han_viet_service import HanVietService


def render_explorer_index(q: str = "") -> Tuple[str, int]:
    """Render the public Hán Việt roots index with optional search filter."""
    service = HanVietService(db.session)
    roots = service.get_explorer_index(q=q)
    html = render_template(
        "dictionary/han_viet_explorer.html",
        roots=roots,
        query=q or "",
    )
    return html, 200


def render_root_detail(root_syllable: str) -> Tuple[Union[str, FlaskResponse], int]:
    """Render the public cluster view for a single Hán Việt root."""
    service = HanVietService(db.session)
    try:
        cluster = service.get_root_cluster(root_syllable)
    except HanVietRootNotFoundError:
        abort(404)

    html = render_template(
        "dictionary/han_viet_detail.html",
        root=cluster["root"],
        compounds=cluster["compounds"],
    )
    return html, 200
