from flask import (Blueprint, request, render_template, redirect, url_for,
                   flash, current_app)
from flask_mail import Message

from app.extensions import mail

home_bp = Blueprint('home_bp', __name__)


@home_bp.route('/')
def index():
    return render_template('index.html')


@home_bp.route('/submit_contact', methods=['POST'])
def submit_contact():
    name = request.form.get('name')
    email = request.form.get('email')
    message = request.form.get('message')

    if not name or not email or not message:
        flash('All fields are required!', 'danger')
        return redirect(url_for('home_bp.index'))

    msg = Message(subject="Contact Form Submission",
                  sender=current_app.config['MAIL_USERNAME'],
                  recipients=[current_app.config['MAIL_RECIPIENT']],
                  body=f"Name: {name}\nEmail: {email}\nMessage: {message}")

    try:
        mail.send(msg)
        flash('Message sent successfully!', 'success')
    except Exception:
        # Log the error or handle it as needed
        flash('An error occurred while sending your message.', 'danger')

    return redirect(url_for('home_bp.index'))


@home_bp.route('/privacy')
def privacy():
    return render_template('privacy.html')
