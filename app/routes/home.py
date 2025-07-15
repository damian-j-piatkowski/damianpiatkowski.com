from flask import Blueprint, render_template, redirect, url_for, flash

from app.controllers.contact_form_controller import handle_contact_form_submission
from app.models.forms.contact_form import ContactForm

home_bp = Blueprint('home_bp', __name__)


@home_bp.route('/')
def index():
    form = ContactForm()  # Create an instance of the form
    return render_template('index.html', form=form)  # Pass it to the template


@home_bp.route('/submit_contact', methods=['POST'])
def submit_contact():
    form = ContactForm()  # Create an instance of the form
    if form.validate_on_submit():  # This will check CSRF token and validate form data
        # Delegate to the controller for handling form submission
        success, flash_message, flash_category = handle_contact_form_submission({
            'name': form.name.data,
            'email': form.email.data,
            'message': form.message.data
        })

        flash(flash_message, flash_category)
    else:
        # If form validation fails, flash an error message
        flash('Please check your input and try again.', 'error')

    return redirect(url_for('home_bp.index'))


@home_bp.route('/privacy')
def privacy():
    return render_template('privacy.html')
