from flask import jsonify, request
from marshmallow import ValidationError

from app.api_schemas.blog_post_schema import BlogPostSchema
from app.services import exceptions
from app.services.blog_service import fetch_all_blog_posts, save_blog_post
from app.services.google_drive_service import GoogleDriveService


# Orchestrates the creation of a blog post
def create_post():
    """Handles the logic for creating a blog post, used by both API and admin routes."""
    data = request.get_json()  # This will work for both API and frontend requests
    schema = BlogPostSchema()

    try:
        validated_data = schema.load(data)
    except ValidationError as err:
        return jsonify(err.messages), 400

    try:
        blog_post = save_blog_post(validated_data)
        return jsonify(schema.dump(blog_post)), 201
    except RuntimeError as e:
        return jsonify({'error': str(e)}), 500


# Orchestrates fetching of all blog posts
def get_all_posts():
    try:
        posts = fetch_all_blog_posts()
        if not posts:
            return jsonify({"message": "No blog posts found"}), 404
        schema = BlogPostSchema(many=True)
        return jsonify(schema.dump(posts)), 200
    except RuntimeError as e:
        return jsonify({"error": str(e)}), 500  # Internal server error


# Orchestrates comparison between Google Drive and DB articles
def compare_articles():
    try:
        # Fetch blog posts from the database
        db_posts = fetch_all_blog_posts()

        # Get Google Drive service
        google_drive_service = get_google_drive_service()

        # Fetch folder ID from the request arguments
        try:
            folder_id = request.args.get('folder_id')
            drive_service = GoogleDriveService()
            contents = drive_service.list_folder_contents(folder_id)
            return jsonify(contents), 200

        except exceptions.GoogleDriveFileNotFoundError as e:
            return jsonify({'error': str(e)}), 404
        except exceptions.GoogleDrivePermissionError as e:
            return jsonify({'error': str(e)}), 403
        except exceptions.GoogleDriveAPIError as e:
            return jsonify({'error': str(e)}), 500

        # Assuming a utility function `find_missing_articles` compares files
        missing_articles = find_missing_articles(db_posts, drive_files)

        return jsonify(missing_articles), 200

    except RuntimeError as e:
        return jsonify({"error": str(e)}), 500
