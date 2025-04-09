"""Admin routes for the Flask application.

This module defines routes for the admin panel, including viewing logs,
managing unpublished and published blog posts, uploading posts from Google Drive,
and deleting published posts.

Routes:
    - /admin/delete_post: Handles deleting published blog posts.
    - /admin/logs: Displays log data in the admin panel.
    - /admin/published_posts: Displays published blog posts.
    - /admin/unpublished_posts: Displays unpublished blog posts.
    - /admin/upload_post: Handles uploading blog posts from Google Drive.
"""

from flask import Blueprint, render_template, jsonify, request

from app.controllers.admin_controller import (
    find_unpublished_drive_articles,
    get_logs_data,
    upload_blog_posts_from_drive,
    # get_published_blog_posts,
    # delete_blog_posts
)

admin_bp = Blueprint('admin', __name__)


# @admin_bp.route('/admin/delete_post', methods=['DELETE'])
# def admin_delete_post():
#     """Handles deletion of published blog posts.
#
#     Extracts the list of selected blog post IDs from the JSON request body
#     and delegates the deletion operation to the controller.
#
#     Returns:
#         Response: JSON response with the deletion result and HTTP status code.
#     """
#     post_ids = request.get_json().get("post_ids", [])
#     result, status_code = delete_blog_posts(post_ids)
#     return jsonify(result), status_code

@admin_bp.route('/admin/logs', methods=['GET'])
def admin_logs():
    """Renders the admin logs page.

    Fetches log data from the system and renders it in an HTML template.

    Returns:
        Response: Rendered HTML template with log data.
    """
    log_data = get_logs_data()
    return render_template('admin_logs.html', log_data=log_data)


# @admin_bp.route('/admin/published_posts', methods=['GET'])
# def admin_published_posts():
#     """Renders the admin published posts page.
#
#     Fetches currently published blog posts and renders them in an HTML template.
#
#     Returns:
#         Response: Rendered HTML template with published blog post data.
#     """
#     published_posts_data = get_published_blog_posts()
#     return render_template('admin_published_posts.html', published_posts_data=published_posts_data)

@admin_bp.route('/admin/unpublished_posts', methods=['GET'])
def admin_unpublished_posts():
    """Renders the admin unpublished posts page.

    Fetches unpublished blog posts from Google Drive and renders them in an HTML template.

    Returns:
        Response: Rendered HTML template with unpublished blog post data.
    """
    posts_data = find_unpublished_drive_articles()
    return render_template('admin_unpublished_posts.html', posts_data=posts_data)


@admin_bp.route("/admin/upload_post", methods=["POST"])
def admin_upload_post():
    """Process unpublished blog posts from Google Drive and return a structured JSON response.

    This endpoint is triggered by a button in `/admin/unpublished_posts`. Instead of rendering
    a template, it processes selected unpublished blog posts from Google Drive and returns a JSON
    response indicating the outcome.

    Flow:
    - User selects unpublished posts and submits the form at `/admin/unpublished_posts`.
    - The front-end sends a JSON payload with a list of files to this endpoint.
    - This endpoint extracts the list and calls `upload_blog_posts_from_drive_controller(files)`.
    - The service reads the file, sanitizes content, and saves the blog post.
    - The response contains a `success` flag and a `message` explaining the result.

    Returns:
        JSON response with:
        - `success` (bool): Whether the operation was successful.
        - `message` (str): A status message indicating success or failure.
    """
    data = request.get_json()
    if not data or "files" not in data:
        return jsonify({"success": False, "message": "Missing 'files' data in request"}), 400

    files = data["files"]
    response, status_code = upload_blog_posts_from_drive(files)

    return jsonify(response), status_code
