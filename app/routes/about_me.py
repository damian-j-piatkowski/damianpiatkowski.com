"""About Me route for the Flask application.

This module defines the route for the 'About Me' page.

Routes:
    - /about-me: Renders the About Me page.
"""

from flask import Blueprint, render_template

about_me_bp = Blueprint('about_me_bp', __name__)


@about_me_bp.route('/about-me')
def about_me():
    """Renders the About Me page.

    Returns:
        Response: Rendered HTML template for the About Me page.
    """
    return render_template('about-me.html')
