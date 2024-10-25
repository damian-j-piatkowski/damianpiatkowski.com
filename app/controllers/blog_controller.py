from flask import jsonify

from app.api_schemas.blog_post_schema import BlogPostSchema
from app.services.blog_service import fetch_all_blog_posts


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
