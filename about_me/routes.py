from flask import Blueprint, render_template

about_me_bp = Blueprint('about_me_bp', __name__)

@about_me_bp.route('/about-me')
def about_me():
    return render_template('about-me.html')