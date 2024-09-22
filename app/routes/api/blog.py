from flask import Blueprint, jsonify
from sqlalchemy.exc import SQLAlchemyError

from app.controllers.blog_controller import get_all_posts

api_blog_bp = Blueprint('api_blog', __name__)


@api_blog_bp.route('/api/posts', methods=['GET'])
def get_posts():
    try:
        return get_all_posts()
    except SQLAlchemyError as db_error:
        return jsonify(
            {'error': 'Database error', 'details': str(db_error)}), 500
    except ValueError as ve:
        return jsonify({'error': 'Invalid value', 'message': str(ve)}), 400
    except Exception as e:
        return jsonify({'error': 'Unexpected error', 'message': str(e)}), 500
