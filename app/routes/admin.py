from flask import Blueprint, request, render_template, jsonify

from app.controllers.admin_controller import find_unpublished_drive_articles, get_logs_data, \
    upload_blog_posts_from_drive

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
    # Extract JSON data from the request
    files = request.get_json().get("files", [])

    # Pass data to the controller
    result, status_code = upload_blog_posts_from_drive(files)
    return jsonify(result), status_code
