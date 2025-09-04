"""Home blueprint routes for damianpiatkowski.com.

This module defines the home-related routes for the Flask application,
including the index page with a contact form, a privacy policy page,
a robots.txt endpoint for search engine crawlers, and the contact form
submission handler.

Blueprints:
    home_bp: Blueprint for home-related routes.

Routes:
    / (index): Render the home page with a contact form.
    /privacy: Render the privacy policy page.
    /robots.txt: Serve the robots.txt file for web crawlers.
    /submit_contact (POST): Handle the submission of the contact form.
"""
from datetime import datetime

from flask import Blueprint, render_template, redirect, url_for, flash, Response, request, jsonify

from app.controllers.contact_form_controller import handle_contact_form_submission
from app.services.blog_service import get_all_blog_post_identifiers
from app.models.forms.contact_form import ContactForm

home_bp = Blueprint('home_bp', __name__)


@home_bp.route('/')
def index():
    """Renders the home page with a contact form.

    Returns:
        str: Rendered HTML template for the home page including the contact form.
    """
    form = ContactForm()  # Create an instance of the form
    return render_template('index.html', form=form)  # Pass it to the template


@home_bp.route('/privacy')
def privacy():
    """Renders the privacy policy page.

    Returns:
        str: Rendered HTML template for the privacy policy page.
    """
    return render_template('privacy.html', include_social_meta=False)


@home_bp.route('/robots.txt')
def robots_txt():
    """Serves the robots.txt file for search engine crawlers.

    Returns:
        flask.Response: Plain text response containing the robots.txt rules.
    """
    return Response(
        "User-agent: *\n"
        "Disallow: /admin/\n"
        "Sitemap: https://damianpiatkowski.com/sitemap.xml\n",
        mimetype='text/plain'
    )

@home_bp.route('/sitemap.xml')
def sitemap():
    """Generates and returns the XML sitemap for search engine crawlers.

    This sitemap includes:
    - Static pages (e.g., homepage, privacy policy, about me, resume, blog)
    - Dynamic blog posts generated from the database using their slugs

    Each sitemap entry includes:
        - `loc`: The absolute URL of the page
        - `lastmod`: The last modification date (either `updated_at` or today's date)
        - `changefreq`: Set to 'monthly' for all pages
        - `priority`: Set to 0.8 for all pages

    Blog post entries will use `updated_at` from the database if available; otherwise,
    the current date is used as the fallback.

    Returns:
        flask.Response: The rendered XML sitemap with MIME type 'application/xml'.

    Template used:
        sitemap.xml — renders the structure of the XML using the provided `pages` list.

    Example XML Output:
        <urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
            <url>
                <loc>http://localhost:5000/</loc>
                <lastmod>2025-08-05</lastmod>
                <changefreq>monthly</changefreq>
                <priority>0.8</priority>
            </url>
            <url>
                <loc>http://localhost:5000/about-me</loc>
                <lastmod>2025-08-05</lastmod>
                <changefreq>monthly</changefreq>
                <priority>0.8</priority>
            </url>
            <url>
                <loc>http://localhost:5000/blog/six-essential-object-oriented-design-principles-from-matthias-nobacks-object-design-style-guide</loc>
                <lastmod>2025-08-01</lastmod>
                <changefreq>monthly</changefreq>
                <priority>0.8</priority>
            </url>
        </urlset>
    """
    pages = []
    base_url = request.url_root.rstrip('/')
    today = datetime.now().date().isoformat()

    # List of static paths on your site
    static_paths = [
        '/',
        '/privacy',
        '/about-me',
        '/resume',
        '/blog'
    ]

    for path in static_paths:
        pages.append({
            'loc': f"{base_url}{path}",
            'lastmod': today
        })

    # Blog posts (dynamic)
    for post in get_all_blog_post_identifiers():
        lastmod = (
            post["updated_at"].date().isoformat()
            if post.get("updated_at") else today
        )
        pages.append({
            'loc': f"{base_url}/blog/{post['slug']}",
            'lastmod': lastmod
        })

    xml = render_template('sitemap.xml', pages=pages)
    return Response(xml, mimetype='application/xml')


@home_bp.route('/submit-contact', methods=['POST'])
def submit_contact():
    """Handle contact form submission with AJAX support."""
    # Check if this is an AJAX request
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'

    form = ContactForm()
    if form.validate_on_submit():
        # Get form data
        form_data = {
            'name': form.name.data,
            'email': form.email.data,
            'message': form.message.data
        }

        # Process the form using your existing controller
        success, message, category = handle_contact_form_submission(form_data)

        if is_ajax:
            # Return JSON response for AJAX requests
            return jsonify({
                'success': success,
                'message': message,
                'category': category
            })
        else:
            # Fallback for non-AJAX requests (regular form submission)
            flash(message, category)
            if success:
                return redirect(url_for('home_bp.index') + '#contact')
            else:
                return redirect(url_for('home_bp.index') + '#contact')

    # Handle validation errors
    if is_ajax:
        # Collect validation errors for AJAX
        error_messages = []
        for field, errors in form.errors.items():
            for error in errors:
                error_messages.append(f"{field.title()}: {error}")

        return jsonify({
            'success': False,
            'message': '; '.join(error_messages),
            'category': 'danger'
        }), 400
    else:
        # Flash errors for regular form submission
        for field, errors in form.errors.items():
            for error in errors:
                flash(f"{field.title()}: {error}", 'danger')
        return redirect(url_for('home_bp.index') + '#contact')