"""Admin routes for the web application.

This module defines routes for the admin panel managing unpublished and published blog posts,
uploading posts from Google Drive, and deleting published posts.

Routes:
    - /admin/delete_blog_posts: Handles deleting published blog posts.
    - /admin/published_posts: Displays published blog posts.
    - /admin/unpublished_posts: Displays unpublished blog posts.
    - /admin/upload_post: Handles uploading blog posts from Google Drive.
"""

from flask import Blueprint, jsonify, request

from app.controllers.admin_controller import (
    delete_blog_posts,
    find_unpublished_drive_articles,
    upload_blog_posts_from_drive,
    get_published_blog_posts,
)

admin_bp = Blueprint('admin', __name__)


@admin_bp.route("/admin/delete-blog-posts", methods=["DELETE"])
def admin_delete_blog_posts():
    """Process deletion of selected blog posts and return a structured JSON response.

    This endpoint is triggered by a button in `/admin/published-posts`. Instead of rendering
    a template, it processes selected published blog posts and returns a JSON response
    indicating the outcome.

    Flow:
    - User selects multiple blog posts and submits the form at `/admin/published-posts`.
    - The front-end sends a JSON payload with a list of slugs to this endpoint.
    - This endpoint extracts the list and calls `delete_blog_posts(slugs)`.
    - The service deletes each corresponding blog post from the database.
    - The response indicates success or failure for each deletion.

    Returns:
        Tuple (JSON, int): A JSON response and HTTP status code.
        Response format varies based on the request:
        - If the 'slugs' key is missing or the JSON is malformed:
            {
                "success": False,
                "message": "Missing 'slugs' data in request"
            }
            HTTP 400

        - If processing was attempted:
            {
                "deleted": [...],  # List of successfully deleted slugs
                "errors": [...]     # List of error details for failed deletions
            }
            HTTP status codes:
                - 200: All posts deleted successfully
                - 207: Partial success (some deletions failed)
                - 400: All deletions failed due to non-critical errors
                - 500: Critical error halted processing

        - If unsupported media type is sent (e.g., not application/json):
            HTTP 415 with no JSON body.

    Notes:
        - This is a backend API endpoint used by the admin panel.
        - Responses are handled asynchronously via JavaScript.
        - JavaScript dynamically updates the UI by removing deleted posts
          and displaying success or error messages.
    """
    data = request.get_json()
    if not data or "slugs" not in data:
        return jsonify({"success": False, "message": "Missing 'slugs' data in request"}), 400
    slugs = data["slugs"]
    return delete_blog_posts(slugs)


@admin_bp.route('/admin/published-posts', methods=['GET'])
def admin_published_posts():
    """Return a list of published blog posts for the admin interface.

    This route retrieves all blog posts that have already been published
    (i.e., stored in the database). It delegates the work to the controller
    function `get_published_blog_posts()` and returns a JSON response.

    Each published post in the response includes:
        - `title`: The blog post title.
        - `slug`: The URL-safe identifier for the post.
        - `id`: The associated Google Drive file ID.

    NOTE: This route currently returns raw JSON for development/testing purposes.
    In production, it will render the `admin_published_posts.html` template.

    Related front-end functionality:
        - Allow admins to delete or edit published posts via AJAX.
        - Send POST requests to `/admin/delete-blog-posts` with selected slugs.
        - Dynamically update the UI upon successful deletions or errors.

    Returns:
        Tuple[FlaskResponse, int]: JSON response with published blog posts and HTTP status code.
    """
    # TODO: replace this with `render_template("admin_published_posts.html", published_posts_data=published_posts_data)`
    return get_published_blog_posts()


@admin_bp.route('/admin/unpublished-posts', methods=['GET'])
def admin_unpublished_posts():
    """Render the Unpublished Blog Posts admin page.

    This page lists blog post files stored on Google Drive that have not yet been published
    to the database. It provides an interface for admins to preview and select files
    for upload.

    Flow:
    - User visits `/admin/unpublished-posts` from the admin sidebar.
    - This route triggers a call to `admin_controller.find_unpublished_drive_articles()`.
    - The controller fetches:
        - Published blog post metadata from the database via the `blog_post_repository`.
        - All files in the configured Google Drive folder via `google_drive_service`.
    - The controller returns a list of files that are on Google Drive but not yet in the database.
    - Each item includes: title, slug, and Drive file ID.
    - The data is passed to the `admin_unpublished_posts.html` template for rendering.

    JavaScript on the front-end:
    - Allows selecting files for upload.
    - Sends an AJAX request to `/admin/upload-blog-posts` with selected file metadata.
    - Updates the UI dynamically upon success/failure.

    Returns:
        Response: Rendered HTML template with a list of unpublished blog posts.
    """
    # TODO: replace this with `render_template("admin_unpublished_posts.html", posts_data=posts_data)`
    return find_unpublished_drive_articles()


@admin_bp.route("/admin/upload-blog-posts", methods=["POST"])
def admin_upload_blog_posts():
    """Process unpublished blog posts from Google Drive and return a structured JSON response.

    This endpoint is triggered by a button in `/admin/unpublished-posts`. Instead of rendering
    a template, it processes selected unpublished blog posts from Google Drive and returns a JSON
    response indicating the outcome.

    Flow:
    - User selects unpublished posts and submits the form at `/admin/unpublished-posts`.
    - The front-end sends a JSON payload with a list of files to this endpoint.
    - This endpoint extracts the list and calls `upload_blog_posts_from_drive(files)`.
    - The service reads the files, sanitizes content, and saves the blog posts to the database.
    - The response indicates success or failure for each file.

    Returns:
        Tuple (JSON, int): A JSON response and HTTP status code.

        Response format varies based on the request:

        - If the 'files' key is missing or the JSON is malformed:
            {
                "success": False,
                "message": "Missing 'files' data in request"
            }
            HTTP 400

        - If processing was attempted:
            {
                "success": [...],  # List of serialized blog posts successfully uploaded
                "errors": [...]    # List of error messages for failed uploads
            }
            HTTP status codes:
                - 201: All files uploaded successfully
                - 207: Partial success (some failed)
                - 400: All failed due to non-critical errors (e.g., duplicates, missing data)
                - 500: Critical error halted processing

        - If unsupported media type is sent (e.g. not application/json):
            HTTP 415 with no JSON body
    """
    data = request.get_json()
    if not data or "files" not in data:
        return jsonify({"success": False, "message": "Missing 'files' data in request"}), 400

    files = data["files"]
    return upload_blog_posts_from_drive(files)
