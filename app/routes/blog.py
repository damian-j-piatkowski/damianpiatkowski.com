"""Blog routes for the Flask application.

This module defines routes for rendering blog-related pages.

Routes:
- /blog: Renders a paginated list of blog posts.
- /blog/<slug>: Renders a single blog post based on the given slug.
"""

from flask import Blueprint, render_template, request, current_app

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

    return render_template("single_blog_post.html", post=json_response.json)
