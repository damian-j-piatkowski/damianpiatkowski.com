from flask import Blueprint

from app.controllers.blog_controller import get_all_posts

blog_bp = Blueprint('blog', __name__)


@blog_bp.route('/api/blog_posts', methods=['GET'])
def get_blog_posts():
    return get_all_posts()

# todo render views
