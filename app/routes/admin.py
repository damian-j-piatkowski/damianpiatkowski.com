from flask import Blueprint, render_template

from app.controllers.admin_controller import (
    get_logs_data,
    find_unpublished_drive_articles,
    upload_blog_post
)

admin_bp = Blueprint('admin', __name__)


@admin_bp.route('/admin/logs')
def admin_logs():
    log_data = get_logs_data()
    return render_template('admin_logs.html', log_data=log_data)


@admin_bp.route('/admin/posts')
def admin_posts():
    posts_data = find_unpublished_drive_articles()
    return render_template('admin_posts.html', posts_data=posts_data)


@admin_bp.route('/admin/upload_post', methods=['POST'])
def admin_upload_post():
    response = upload_blog_post()
    return response
