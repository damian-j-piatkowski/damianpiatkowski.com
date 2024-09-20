from flask import request, jsonify
from marshmallow import ValidationError
from app.services.blog_service import fetch_all_blog_posts, save_blog_post
from app.services.google_drive_service import list_files_in_drive
from app.services.article_sync_service import find_missing_articles
from app.api_schemas.blog_post_schema import BlogPostSchema


# Orchestrates the creation of a blog post
def create_post():
    data = request.get_json()
    schema = BlogPostSchema()

    try:
        validated_data = schema.load(data)
    except ValidationError as err:
        return jsonify(err.messages), 400

    blog_post = save_blog_post(validated_data)

    return jsonify(schema.dump(blog_post)), 201


# Orchestrates fetching of all blog posts
def get_all_posts():
    posts = fetch_all_blog_posts()
    schema = BlogPostSchema(many=True)
    return jsonify(schema.dump(posts)), 200


# Orchestrates comparison between Google Drive and DB articles
def compare_articles():
    db_posts = fetch_all_blog_posts()
    drive_docs = list_files_in_drive()
    missing_articles = find_missing_articles(db_posts, drive_docs)
    return jsonify(missing_articles)
