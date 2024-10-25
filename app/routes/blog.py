from flask import Blueprint

from app.controllers.blog_controller import get_all_posts

blog_bp = Blueprint('blog', __name__)


# Route for creating a blog post
@blog_bp.route('/api/blog_post', methods=['POST'])
def create_blog_post():
    return create_post()


# Route for fetching all blog posts
@blog_bp.route('/api/blog_posts', methods=['GET'])
def get_blog_posts():
    return get_all_posts()

# Route for comparing articles between Google Drive and DB
# @blog_bp.route('/compare/articles', methods=['GET'])
# def compare_blog_posts():
#     return compare_articles()

# todo render views
