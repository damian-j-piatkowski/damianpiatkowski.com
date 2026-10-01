"""Public and administrative dictionary routes."""

from flask import Blueprint, request

from app.auth.decorators import admin_required
from app.controllers import dictionary_controller

dictionary_bp = Blueprint("dictionary", __name__)


@dictionary_bp.route("/dictionary", methods=["GET"])
def render_dictionary_page():
    """Render the public dictionary search page."""
    return dictionary_controller.render_dictionary_page()


@dictionary_bp.route("/dictionary/search", methods=["GET"])
def search_dictionary():
    """Typeahead search endpoint for Vietnamese dictionary terms."""
    query = request.args.get("q", "")
    limit = request.args.get("limit", 20, type=int)
    return dictionary_controller.search_dictionary(query=query, limit=limit or 20)


@dictionary_bp.route("/admin/dictionary/new", methods=["GET"])
@admin_required
def render_create_workspace():
    """Render the dictionary entry creation workspace."""
    return dictionary_controller.render_create_workspace()


@dictionary_bp.route("/admin/dictionary/dashboard", methods=["GET"])
@admin_required
def render_dashboard():
    """Render the dictionary analytics dashboard."""
    return dictionary_controller.render_dashboard(
        tab=request.args.get("tab", "general"),
        page=request.args.get("page", 1, type=int) or 1,
        sort=request.args.get("sort", "created_at_desc"),
        source_type=request.args.get("type", ""),
        title_query=request.args.get("q", ""),
    )


@dictionary_bp.route("/admin/api/stats/word-velocity", methods=["GET"])
@admin_required
def word_velocity_stats():
    """Return word-creation velocity JSON for the dashboard chart."""
    return dictionary_controller.word_velocity_stats(
        range_key=request.args.get("range", "30d"),
    )


@dictionary_bp.route("/admin/dictionary/<int:word_id>/edit", methods=["GET"])
@admin_required
def render_edit_workspace(word_id: int):
    """Render the dictionary entry modification workspace."""
    return dictionary_controller.render_edit_workspace(word_id)


@dictionary_bp.route("/admin/dictionary/check-duplicate", methods=["GET"])
@admin_required
def check_duplicate():
    """Check whether a Vietnamese dictionary word already exists."""
    viet_word = request.args.get("viet_word", "")
    return dictionary_controller.check_duplicate(viet_word)


@dictionary_bp.route("/admin/dictionary/words", methods=["POST"])
@admin_required
def create_word():
    """Create a new dictionary entry."""
    data = request.get_json(silent=True) or {}
    return dictionary_controller.create_word(
        viet_word=data.get("viet_word", ""),
        english_translation=data.get("english_translation", ""),
        word_types=data.get("word_types"),
    )


@dictionary_bp.route("/admin/dictionary/words/<int:word_id>", methods=["GET"])
@admin_required
def get_word(word_id: int):
    """Return a dictionary entry as JSON."""
    return dictionary_controller.get_word(word_id)


@dictionary_bp.route("/admin/dictionary/words/<int:word_id>", methods=["PATCH", "PUT"])
@admin_required
def update_word(word_id: int):
    """Update an existing dictionary entry."""
    data = request.get_json(silent=True) or {}
    return dictionary_controller.update_word(
        word_id=word_id,
        viet_word=data.get("viet_word"),
        english_translation=data.get("english_translation"),
        word_types=data.get("word_types"),
    )


@dictionary_bp.route("/admin/dictionary/words/<int:word_id>", methods=["DELETE"])
@admin_required
def delete_word(word_id: int):
    """Permanently delete a dictionary entry."""
    return dictionary_controller.delete_word(word_id)


@dictionary_bp.route("/admin/dictionary/words/<int:word_id>/examples", methods=["POST"])
@admin_required
def add_example(word_id: int):
    """Add a contextual example to a dictionary entry."""
    data = request.get_json(silent=True) or {}
    return dictionary_controller.add_example(
        word_id=word_id,
        source_id=int(data.get("source_id")),
        sentence=data.get("sentence", ""),
        english_translation=data.get("english_translation", ""),
    )


@dictionary_bp.route("/admin/dictionary/examples/<int:example_id>", methods=["DELETE"])
@admin_required
def remove_example(example_id: int):
    """Remove a contextual example."""
    return dictionary_controller.remove_example(example_id)


@dictionary_bp.route("/admin/dictionary/sources", methods=["GET"])
@admin_required
def list_sources():
    """List or search dictionary sources."""
    query = request.args.get("q", "")
    return dictionary_controller.list_sources(query=query)


@dictionary_bp.route("/admin/dictionary/sources", methods=["POST"])
@admin_required
def create_source():
    """Create a new dictionary source."""
    data = request.get_json(silent=True) or {}
    return dictionary_controller.create_source(
        source_type=data.get("source_type", ""),
        title=data.get("title", ""),
        url=data.get("url"),
    )


@dictionary_bp.route("/admin/dictionary/sources/<int:source_id>", methods=["DELETE"])
@admin_required
def delete_source(source_id: int):
    """Delete a dictionary source and cascade its examples."""
    return dictionary_controller.delete_source(source_id)


@dictionary_bp.route("/admin/dictionary/han-viet/check", methods=["GET"])
@admin_required
def check_han_viet_roots():
    """Detect existing and missing Hán Việt roots for a compound word."""
    compound_word = request.args.get("word", "")
    return dictionary_controller.check_han_viet_roots(compound_word)


@dictionary_bp.route(
    "/admin/dictionary/words/<int:word_id>/han-viet/<int:root_id>",
    methods=["POST"],
)
@admin_required
def associate_han_viet_root(word_id: int, root_id: int):
    """Associate an existing Hán Việt root with a dictionary word."""
    return dictionary_controller.associate_han_viet_root(word_id, root_id)


@dictionary_bp.route("/admin/dictionary/words/<int:word_id>/han-viet", methods=["POST"])
@admin_required
def create_han_viet_root(word_id: int):
    """Create a Hán Việt root and associate it with a dictionary word."""
    data = request.get_json(silent=True) or {}
    return dictionary_controller.create_han_viet_root(
        word_id=word_id,
        root=data.get("root", ""),
        chinese_character=data.get("chinese_character", ""),
        root_meaning=data.get("root_meaning", ""),
    )


@dictionary_bp.route(
    "/admin/dictionary/words/<int:word_id>/han-viet/<int:root_id>",
    methods=["DELETE"],
)
@admin_required
def unlink_han_viet_root(word_id: int, root_id: int):
    """Unlink a Hán Việt root from a dictionary word."""
    return dictionary_controller.unlink_han_viet_root(word_id, root_id)


@dictionary_bp.route("/admin/dictionary/han-viet/<int:root_id>", methods=["DELETE"])
@admin_required
def delete_han_viet_root(root_id: int):
    """Delete a Hán Việt root when it is no longer associated."""
    return dictionary_controller.delete_han_viet_root(root_id)
