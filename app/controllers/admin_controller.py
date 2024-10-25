"""Admin controller for handling requests related to logs, blog posts, and Google Drive articles.

This module includes endpoints for:
- Fetching unpublished articles from Google Drive
- Retrieving all logs from the database
- Uploading new blog posts after validation and sanitization

Raises:
    RuntimeError: If there are issues fetching or saving data.
    KeyError: If required blog post fields are missing during upload.

"""

from flask import current_app, jsonify, request
from marshmallow import ValidationError

from app import exceptions
from app.api_schemas.blog_post_schema import BlogPostSchema
from app.services.article_sync_service import find_missing_articles
from app.services.blog_service import fetch_all_blog_posts, save_blog_post
from app.services.google_drive_service import GoogleDriveService
from app.services.log_service import fetch_all_logs
from app.services.sanitization_service import normalize_title


def find_unpublished_drive_articles() -> jsonify:
    """Fetches unpublished articles from Google Drive and compares with database entries.

    Returns:
        jsonify: JSON response with missing articles.

    Raises:
        GoogleDriveFileNotFoundError: If specific file(s) are not found in Google Drive.
        GoogleDrivePermissionError: If permissions are insufficient for Google Drive access.
        GoogleDriveAPIError: For general Google Drive API failures.
        RuntimeError: For other errors during article comparison.
    """
    try:
        # Fetch blog posts from the database and normalize their titles
        db_posts = fetch_all_blog_posts()
        db_titles = [post['title'] for post in db_posts]

        # Fetch folder ID from the app configuration
        folder_id = current_app.config.get('DRIVE_BLOG_POSTS_FOLDER_ID')
        if not folder_id:
            current_app.logger.error("Google Drive folder ID is missing in the configuration.")
            return jsonify({'error': 'Google Drive folder ID is missing in the configuration'}), 500

        # Get Google Drive service and list folder contents
        drive_service = GoogleDriveService()
        drive_files = drive_service.list_folder_contents(folder_id)
        drive_titles = [normalize_title(file['name']) for file in drive_files]

        # Compare and find missing articles
        missing_articles = find_missing_articles(db_titles, drive_titles)

        return jsonify(missing_articles), 200

    except exceptions.GoogleDriveFileNotFoundError as e:
        current_app.logger.error(f"Google Drive file not found: {e}")
        return jsonify({'error': str(e)}), 404
    except exceptions.GoogleDrivePermissionError as e:
        current_app.logger.error(f"Google Drive permission error: {e}")
        return jsonify({'error': str(e)}), 403
    except exceptions.GoogleDriveAPIError as e:
        current_app.logger.error(f"Google Drive API error: {e}")
        return jsonify({'error': str(e)}), 500
    except RuntimeError as e:
        current_app.logger.error(f"Error in finding unpublished articles: {e}")
        return jsonify({"error": str(e)}), 500


def get_logs_data() -> jsonify:
    """Fetches all logs from the database and returns them in JSON format.

    Returns:
        jsonify: JSON response containing logs or a message if none are found.

    Raises:
        RuntimeError: If there is an error retrieving the logs.
    """
    try:
        logs = fetch_all_logs()
        if not logs:
            current_app.logger.info("No logs found.")
            return jsonify({"message": "No logs found"}), 404
        return jsonify(logs), 200
    except RuntimeError as e:
        current_app.logger.error(f"Failed to retrieve logs: {e}")
        return jsonify({"error": str(e)}), 500


def upload_blog_post() -> jsonify:
    """Uploads a new blog post after validating and sanitizing the provided data.

    Returns:
        jsonify: JSON response with the newly created blog post data.

    Raises:
        ValidationError: If input data fails validation.
        RuntimeError: If there is an error saving the blog post.
    """
    data = request.get_json()
    schema = BlogPostSchema()

    try:
        validated_data = schema.load(data)
    except ValidationError as err:
        current_app.logger.warning(f"Validation error for blog post data: {err.messages}")
        return jsonify(err.messages), 400

    try:
        blog_post = save_blog_post(validated_data)
        current_app.logger.info("Blog post created successfully.")
        return jsonify(schema.dump(blog_post)), 201
    except RuntimeError as e:
        current_app.logger.error(f"Failed to save blog post: {e}")
        return jsonify({'error': str(e)}), 500
