"""Admin controller for handling requests related to logs, blog posts, and Google Drive articles.

This module includes endpoints for:
- Fetching unpublished articles from Google Drive
- Retrieving all logs from the database
- Uploading new blog posts after validation and sanitization

Raises:
    RuntimeError: If there are issues fetching or saving data.
    KeyError: If required blog post fields are missing during upload.

"""

import logging
from typing import List, Dict, Tuple

from flask import current_app, jsonify

from app import exceptions
from app.services.article_sync_service import find_missing_articles
from app.services.blog_service import fetch_all_blog_posts
from app.services.file_processing_service import process_file
from app.services.google_drive_service import GoogleDriveService
from app.services.log_service import fetch_all_logs
from app.services.sanitization_service import normalize_title
from app.models.data_schemas.log_schema import LogSchema

logger = logging.getLogger(__name__)


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
        db_titles = {normalize_title(post.title) for post in db_posts}

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


def get_logs_data():
    """Fetch logs and serialize them for JSON response."""
    try:
        logs = fetch_all_logs()  # List[Log]
        if not logs:
            current_app.logger.info("No logs found.")
            return jsonify({"message": "No logs found"}), 404

        schema = LogSchema(many=True)  # Instantiate schema for multiple logs
        serialized_logs = schema.dump(logs)  # Serialize the domain objects
        return jsonify(serialized_logs), 200  # Return serialized data with status 200
    except RuntimeError as e:
        current_app.logger.error(f"Failed to retrieve logs: {e}")
        return jsonify({"error": str(e)}), 500  # Return error with status 500


def upload_blog_posts_from_drive(files: List[Dict[str, str]]) -> Tuple:
    """Uploads blog posts from Google Drive using provided file IDs and titles.

    Args:
        files (List[Dict[str, str]]): A list of dictionaries, each containing:
            - "id" (str): The Google Drive file ID.
            - "title" (str): The title to assign to the blog post.

    Returns:
        Tuple[Response, int]: A tuple containing:
            - A dictionary response, formatted as:
                - {"error": "No files provided"} if the input is invalid.
                - {"success": [...], "errors": [...]}:
                    - "success" contains a list of serialized blog post data for successfully
                        processed files.
                    - "errors" contains a list of dictionaries describing issues with individual
                        files.
            - An HTTP status code indicating the result:
                - 400 if no files are provided or none are valid for processing.
                - 201 if all blog posts are successfully created.
                - 207 if some blog posts are successfully created and there are errors.
                - 500 for unexpected critical errors during processing.

    Raises:
        RuntimeError: For critical failures during blog post processing.

    Examples:
        Success Response:
        {
            "success": [
                {
                    "title": "Example Blog Post",
                    "content": "...",
                    "drive_file_id": "12345",
                    "created_at": "2024-12-02T12:00:00"
                }
            ],
            "errors": []
        }

        Mixed Response (Success and Errors):
        {
            "success": [
                {
                    "title": "Example Blog Post",
                    "content": "...",
                    "drive_file_id": "12345",
                    "created_at": "2024-12-02T12:00:00"
                }
            ],
            "errors": [
                {"file_id": "67890", "error": "File not found"}
            ]
        }
    """
    # Initialize response data
    response_data = {"success": [], "errors": []}

    if not files:
        return {"error": "No files provided"}, 400

    for file in files:
        file_id = file.get("id")
        title = file.get("title")

        if not file_id or not title:
            response_data["errors"].append({"file_id": file_id, "error": "Missing required fields"})
            continue

        try:
            success, message = process_file(file_id, title)
            if success:
                response_data["success"].append({"file_id": file_id, "message": message})
            else:
                response_data["errors"].append({"file_id": file_id, "error": message})
        except ValueError as ve:
            # Handle expected errors like "File not found"
            error_message = str(ve)
            response_data["errors"].append({"file_id": file_id, "error": error_message})
        except PermissionError as pe:
            # Handle permission-related errors
            error_message = str(pe)
            response_data["errors"].append(
                {"file_id": file_id, "error": "Permission denied on Google Drive"})
            logger.error(f"Permission error encountered for file ID {file_id}: {error_message}")
        except Exception as e:
            # Handle unexpected critical errors
            error_message = str(e)
            response_data["errors"].append(
                {"file_id": file_id, "error": "Unexpected error occurred."})
            logger.error(f"Critical exception encountered for file ID {file_id}: {error_message}")
            break

    # Determine status code
    if any(error.get("error") == "Unexpected error occurred." for error in response_data["errors"]):
        # Critical or unexpected error occurred, halt processing and return 500
        return response_data, 500
    elif not response_data["success"] and response_data["errors"]:
        # All errors, no successes, return 500
        return response_data, 400
    elif response_data["success"] and response_data["errors"]:
        # Mixed results (non-critical errors), return 207
        return response_data, 207
    elif response_data["success"]:
        # All successful
        return response_data, 201

    return response_data, 400  # Fallback for invalid input
