from flask import jsonify, request
from marshmallow import ValidationError

from app.api_schemas.blog_post_schema import BlogPostSchema
from app.services.blog_service import fetch_all_blog_posts, save_blog_post


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



