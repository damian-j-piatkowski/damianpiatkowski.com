from flask import jsonify, current_app

from app.models.data_schemas.blog_post_schema import BlogPostSchema
from app.services.blog_service import fetch_all_blog_posts


# Orchestrates fetching of all blog posts
def get_all_posts():
    try:
        # Fetch all blog posts as BlogPost instances
        posts = fetch_all_blog_posts()
        if not posts:
            current_app.logger.info("No blog posts found.")
            return jsonify({"message": "No blog posts found"}), 404

        # Serialize the blog posts using the schema
        schema = BlogPostSchema(many=True)
        serialized_posts = schema.dump(posts)
        return jsonify(serialized_posts), 200

    except RuntimeError as e:
        current_app.logger.error(f"Failed to retrieve blog posts: {e}")
        return jsonify({"error": str(e)}), 500  # Internal server error
