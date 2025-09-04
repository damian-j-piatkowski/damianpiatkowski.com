"""Blog routes for the Flask application.

This module defines routes for rendering blog-related pages.

Routes:
- /blog: Renders a paginated list of blog posts.
- /blog/<slug>: Renders a single blog post based on the given slug.
- /blog/category/<category_slug>: Renders posts filtered by category with SEO-friendly URL.
"""

from flask import Blueprint, render_template, request, current_app

from app.controllers.blog_controller import get_paginated_posts, get_single_post, get_related_posts
from app.services.formatting_service import format_date

blog_bp = Blueprint("blog", __name__)


def slug_to_category_name(slug: str) -> str:
    """Convert slug back to category name with fallback mapping for known exceptions.

    Examples:
        'python' -> 'Python'
        'object-oriented-programming' -> 'Object-Oriented Programming'
        'devops' -> 'DevOps'
        'c-sharp' -> 'C#'
    """
    exceptions = {
        "devops": "DevOps",
        "c-sharp": "C#",
        "c-plus-plus": "C++",
        "javascript": "JavaScript",
        "typescript": "TypeScript",
        "ai-ml": "AI/ML",
        "ios": "iOS",
        "html-css": "HTML/CSS",
        "object-oriented-programming": "Object-Oriented Programming",
    }

    if slug in exceptions:
        return exceptions[slug]

    return slug.replace('-', ' ').title()


@blog_bp.route("/blog", methods=["GET"])
def render_blog_posts():
    """Render the blog posts page with pagination and optional category filtering.

    Query Parameters:
        page (int, optional): The current page number. Example: `/blog?page=2`
        per_page (int, optional): The number of posts per page. Example: `/blog?page=2&per_page=5`
            (Defaults to `Config.PER_PAGE` if not provided).
        category (str, optional): Filter posts by category. Example: `/blog?category=Python`

    Returns:
        Response: Rendered HTML page with paginated blog posts.
    """
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", current_app.config["PER_PAGE"], type=int)
    category = request.args.get("category", None, type=str)

    json_response, status_code = get_paginated_posts(page, per_page, category)

    if status_code != 200:
        return render_template("blog.html", posts_data=[], total_pages=0, page=page,
                               current_category=category, all_categories=[], total_posts=0)

    posts_data = json_response.json["posts"]
    total_pages = json_response.json["total_pages"]

    # Format created_at dates for each post
    for post in posts_data:
        if 'created_at' in post:
            post['formatted_date'] = format_date(post['created_at'])

    # Get all categories with counts for the sidebar
    from app.controllers.blog_controller import get_all_categories_with_counts
    categories_response, categories_status = get_all_categories_with_counts()

    if categories_status == 200:
        all_categories = categories_response.json["categories"]
        total_posts = categories_response.json["total_posts"]
    else:
        all_categories = []
        total_posts = 0

    return render_template("blog.html", posts_data=posts_data, total_pages=total_pages, page=page,
                           current_category=category, all_categories=all_categories,
                           total_posts=total_posts)


@blog_bp.route("/blog/category/<category_slug>", methods=["GET"])
def render_category_posts(category_slug: str):
    """Render blog posts filtered by category using SEO-friendly URL.

    Args:
        category_slug (str): URL-friendly category slug (e.g., 'object-oriented-programming')

    Query Parameters:
        page (int, optional): The current page number. Example: `/blog/category/python?page=2`
        per_page (int, optional): The number of posts per page.

    Examples:
        /blog/category/python
        /blog/category/object-oriented-programming
        /blog/category/web-development?page=2

    Returns:
        Response: Rendered HTML page with category-filtered blog posts.
    """
    # Convert slug back to category name
    category_name = slug_to_category_name(category_slug)

    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", current_app.config["PER_PAGE"], type=int)

    json_response, status_code = get_paginated_posts(page, per_page, category_name)

    if status_code != 200:
        return render_template("blog.html", posts_data=[], total_pages=0, page=page,
                               current_category=category_name, category_slug=category_slug,
                               all_categories=[], total_posts=0)

    posts_data = json_response.json["posts"]
    total_pages = json_response.json["total_pages"]

    # Format created_at dates for each post
    for post in posts_data:
        if 'created_at' in post:
            post['formatted_date'] = format_date(post['created_at'])

    # Get all categories with counts for the sidebar
    from app.controllers.blog_controller import get_all_categories_with_counts
    categories_response, categories_status = get_all_categories_with_counts()

    if categories_status == 200:
        all_categories = categories_response.json["categories"]
        total_posts = categories_response.json["total_posts"]
    else:
        all_categories = []
        total_posts = 0

    return render_template("blog.html", posts_data=posts_data, total_pages=total_pages, page=page,
                           current_category=category_name, category_slug=category_slug,
                           all_categories=all_categories, total_posts=total_posts)


@blog_bp.route("/blog/<slug>", methods=["GET"])
def render_single_blog_post(slug: str):
    """Render a single blog post page, enriched with image paths and related posts.

    Args:
        slug (str): The unique identifier for the blog post.

    Returns:
        Response: Rendered HTML page with blog post content and related posts.
    """
    json_response, status_code = get_single_post(slug)

    if status_code != 200:
        return render_template("single_blog_post.html", post=None), status_code

    post_data = json_response.json

    # Format the created_at date for display
    if 'created_at' in post_data:
        # Format the date - convert "2025-07-22 07:39:58" to "July 22, 2025"
        post_data['formatted_date'] = format_date(post_data['created_at'])

    # Fetch related posts if applicable
    related_posts = []
    if post_data.get('categories'):
        related_response, related_status = get_related_posts(post_data['categories'], slug)
        if related_status == 200:
            related_posts = related_response.json.get('related_posts', [])

        for post in related_posts:
            post['formatted_date'] = format_date(post['created_at'])

    return render_template(
        "single_blog_post.html",
        post=post_data,
        related_posts=related_posts,
    )
