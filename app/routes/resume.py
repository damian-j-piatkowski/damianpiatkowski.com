from flask import Blueprint, render_template

resume_bp = Blueprint('resume_bp', __name__)

@resume_bp.route('/resume')
def resume():
    return render_template('resume.html')