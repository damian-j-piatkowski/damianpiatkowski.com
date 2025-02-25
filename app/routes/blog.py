"""Blog routes for the Flask application.

This module defines the routes for displaying blog posts.

Routes:
    - /blog: Renders a paginated list of blog posts.
    - /blog/<post_id>: Renders a single blog post based on its ID.
"""

from flask import Blueprint, render_template, request

from app.controllers.blog_controller import get_all_posts

blog_bp = Blueprint('blog', __name__)

@blog_bp.route('/blog', methods=['GET'])
def render_blog_posts():
    """Renders the blog posts page with pagination.

    Retrieves paginated blog posts from the controller and renders them in a template.

    Query Params:
        page (int): The current page number (default is 1).
        per_page (int): The number of posts per page (default is 10).

    Returns:
        Response: Rendered HTML template with paginated blog posts.
    """
    page = request.args.get('page', 1, type=int)
    per_page = 10  # TODO: Make this configurable

    posts_data = get_all_posts(page, per_page)
    return render_template('blog.html', posts_data=posts_data)

# @blog_bp.route('/blog/<string:post_id>', methods=['GET'])
# def render_single_blog_post(post_id):
#     """Renders a single blog post page.
#
#     Retrieves the blog post by its ID and displays it.
#
#     Args:
#         post_id (str): The unique ID of the blog post.
#
#     Returns:
#         Response: Rendered HTML template with the blog post details.
#     """
#     post_data = get_blog_post_by_id(post_id)
#     if post_data is None:
#         return render_template('404.html'), 404  # Handle missing post
#
#     return render_template('single_blog_post.html', post_data=post_data)
