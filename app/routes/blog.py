"""Blog routes for the Flask application.

This module defines the routes for displaying blog posts.

Routes:
    - /blog: Renders a paginated list of blog posts.
    - /blog/<post_id>: Renders a single blog post based on its ID.
"""

from flask import Blueprint, render_template, request, Response, current_app

# from app.controllers.blog_controller import get_all_posts

blog_bp = Blueprint('blog', __name__)
#
#
# @blog_bp.route("/blog", methods=["GET"])
# def render_blog_posts() -> Response:
#     """Render the blog posts page with pagination.
#
#     Query Parameters:
#         page (int, optional): The current page number. Example: `/blog?page=2`
#         per_page (int, optional): The number of posts per page. Example: `/blog?page=2&per_page=5`
#             (Defaults to `Config.PER_PAGE` if not provided).
#
#     Returns:
#         Response: Rendered HTML page with paginated blog posts.
#     """
#     page: int = request.args.get("page", 1, type=int)
#     per_page: int = request.args.get("per_page", current_app.config["PER_PAGE"], type=int)
#
#     posts_data, total_pages = get_all_posts(page, per_page)
#     return render_template("blog.html", posts_data=posts_data, total_pages=total_pages, page=page)
#
#
# @blog_bp.route("/blog/<int:post_id>", methods=["GET"])
# def render_single_blog_post(post_id: int) -> Response:
#     """Render a single blog post page.
#
#     Args:
#         post_id (int): The ID of the blog post to retrieve.
#
#     Returns:
#         Response: Rendered HTML page displaying the blog post.
#     """
#     post_data = get_single_blog_post(post_id)
#
#     if not post_data:
#         abort(404, description="Blog post not found.")
#
#     return render_template("single_blog_post.html", post=post_data)
