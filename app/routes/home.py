from flask import Blueprint, request, render_template, redirect, url_for, flash

from app.controllers.contact_form_controller import handle_contact_form_submission

home_bp = Blueprint('home_bp', __name__)


@home_bp.route('/')
def index():
    return render_template('index.html')


@home_bp.route('/submit_contact', methods=['POST'])
def submit_contact():
    form_data = request.form.to_dict()  # Get form data as a dictionary

    # Delegate to the controller for handling form submission
    success, flash_message, flash_category = handle_contact_form_submission(form_data)

    # Flash the message and redirect
    flash(flash_message, flash_category)
    return redirect(url_for('home_bp.index'))


@home_bp.route('/privacy')
def privacy():
    return render_template('privacy.html')
