"""Blog routes for the Flask application.

This module defines routes for rendering blog-related pages.

Routes:
- /blog: Renders a paginated list of blog posts.
- /blog/<slug>: Renders a single blog post based on the given slug.
"""

from flask import Blueprint, render_template, request, current_app
import os
from app.controllers.blog_controller import get_paginated_posts, get_single_post

blog_bp = Blueprint("blog", __name__)


@blog_bp.route("/blog", methods=["GET"])
def render_blog_posts():
    """Render the blog posts page with pagination.

    Query Parameters:
        page (int, optional): The current page number. Example: `/blog?page=2`
        per_page (int, optional): The number of posts per page. Example: `/blog?page=2&per_page=5`
            (Defaults to `Config.PER_PAGE` if not provided).

    Returns:
        Response: Rendered HTML page with paginated blog posts.
    """
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", current_app.config["PER_PAGE"], type=int)

    json_response, status_code = get_paginated_posts(page, per_page)

    if status_code != 200:
        return render_template("blog.html", posts_data=[], total_pages=0, page=page)

    posts_data = json_response.json["posts"]
    total_pages = json_response.json["total_pages"]

    return render_template("blog.html", posts_data=posts_data, total_pages=total_pages, page=page)


@blog_bp.route("/blog/<slug>", methods=["GET"])
def render_single_blog_post(slug: str):
    """Render a single blog post based on the provided slug.

    Args:
        slug (str): The unique identifier for the blog post.

    Returns:
        Response: Rendered HTML page displaying the blog post details.
    """
    json_response, status_code = get_single_post(slug)

    if status_code != 200:
        return render_template("single_blog_post.html", post=None), status_code

    # Get the post data and format the date
    post_data = json_response.json
    if post_data and 'created_at' in post_data:
        # Format the date - convert "2025-07-22 07:39:58" to "July 22, 2025"
        from datetime import datetime
        try:
            # Parse the datetime string
            dt = datetime.strptime(post_data['created_at'], '%Y-%m-%d %H:%M:%S')
            # Format it nicely
            post_data['formatted_date'] = dt.strftime('%B %d, %Y')
        except ValueError:
            # Fallback if the format is different
            post_data['formatted_date'] = post_data['created_at'][:10]

    # Get configuration
    flask_env = current_app.config.get('FLASK_ENV', 'development')
    images_base = current_app.config.get('IMAGES_BASE_PATH', '/static/hero-images')
    default_slug = current_app.config.get('DEFAULT_HERO_IMAGE_SLUG', 'default-placeholder')

    # Start with post-specific images
    hero_images_path = f"{images_base}/{slug}"

    # Environment-based logic
    if flask_env in ['production', 'qa']:
        # Production/QA: Assume S3, images should exist or fallback gracefully
        # We trust that images exist in S3, fallback handled by frontend
        pass  # Keep hero_images_path as is
    else:
        # Development/local: Check file system for existence
        # Fix: Use 'hero-images' instead of 'images' to match your actual folder structure
        local_path = os.path.join(current_app.static_folder, 'hero-images', slug, 'small.jpg')
        if not os.path.exists(local_path):
            # Fallback to default placeholder
            hero_images_path = f"{images_base}/{default_slug}"

    return render_template("single_blog_post.html",
                           post=post_data,
                           hero_images_path=hero_images_path)