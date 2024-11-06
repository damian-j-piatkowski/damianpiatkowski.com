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

from app import exceptions
from app.models.data_schemas.blog_post_schema import BlogPostSchema
from app.services.article_sync_service import find_missing_articles
from app.services.blog_service import fetch_all_blog_posts, save_blog_post
from app.services.google_drive_service import GoogleDriveService
from app.services.log_service import fetch_all_logs
from app.services.sanitization_service import normalize_title, sanitize_html
from app.services.formatting_service import convert_markdown_to_html


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
        db_titles = {normalize_title(post['title']) for post in
                     db_posts}  # Using a set for comparison efficiency

        # Fetch folder ID from the app configuration
        folder_id = current_app.config.get('DRIVE_BLOG_POSTS_FOLDER_ID')
        if not folder_id:
            current_app.logger.error("Google Drive folder ID is missing in the configuration.")
            return jsonify({'error': 'Google Drive folder ID is missing in the configuration'}), 500

        # Get Google Drive service and list folder contents with IDs
        drive_service = GoogleDriveService()
        drive_files = drive_service.list_folder_contents(folder_id)

        # Normalize titles and map them to IDs
        drive_title_id_map = {
            normalize_title(file['name']): file['id']
            for file in drive_files
        }

        # Find missing articles by comparing with database titles
        missing_titles = find_missing_articles(list(db_titles), list(drive_title_id_map.keys()))
        missing_articles = [
            {'title': title, 'id': drive_title_id_map[title]}
            for title in missing_titles
        ]

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


def upload_blog_posts_from_drive() -> jsonify:
    """Uploads blog posts from Google Drive using provided file IDs.

    Returns:
        jsonify: JSON response with the status of each file processed.

    Raises:
        GoogleDriveFileNotFoundError: If a file is not found.
        GoogleDrivePermissionError: If permissions are insufficient.
        GoogleDriveAPIError: For general API errors.
    """
    file_ids = request.get_json().get("file_ids", [])
    if not file_ids:
        return jsonify({"error": "No file IDs provided"}), 400

    response_data = []
    google_drive_service = GoogleDriveService()

    for file_id in file_ids:
        try:
            # Fetch file content from Google Drive
            file_content = google_drive_service.read_file(file_id)

            # Convert plain text content to HTML
            html_content = convert_markdown_to_html(file_content)

            # Sanitize the HTML content for security
            sanitized_content = sanitize_html(html_content)

            # Create blog post data using the fetched and sanitized content
            blog_post = save_blog_post({
                "title": f"Imported Post {file_id}",  # Adjust title as needed
                "content": sanitized_content,
                "image_small": "path/to/small_image.jpg",
                "image_medium": "path/to/medium_image.jpg",
                "image_large": "path/to/large_image.jpg",
                "url": f"/blog/{file_id}"
            })

            current_app.logger.info("Blog post created successfully.")
            response_data.append(BlogPostSchema().dump(blog_post))
        except exceptions.GoogleDriveFileNotFoundError:
            current_app.logger.warning(f"File not found on Google Drive: {file_id}")
        except exceptions.GoogleDrivePermissionError:
            current_app.logger.warning(f"Permission denied for file: {file_id}")
        except RuntimeError as e:
            current_app.logger.error(f"Failed to save blog post for file {file_id}: {e}")
            return jsonify({"error": str(e)}), 500

    return jsonify(response_data), 201 if response_data else 404

