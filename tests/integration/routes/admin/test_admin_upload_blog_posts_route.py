"""Integration tests for the /admin/upload-blog-posts route.

This module verifies the integration between the Flask route `/admin/upload-blog-posts`
and the `upload_blog_posts_from_drive` controller function. It tests the route’s behavior
under various conditions, including real Google Drive API interaction, malformed input,
and unsupported content types.

Test Functions:

    - test_upload_blog_posts_missing_files_key
    - test_upload_blog_posts_malformed_json
    - test_upload_blog_posts_route_with_actual_api
    - test_upload_blog_posts_unsupported_media_type

Fixtures:
    - app: Provides the Flask application context for testing.
    - client: A Flask test client to simulate HTTP requests.
    - google_drive_service_fixture: Provides real access to Google Drive.
    - file_metadata: Metadata for a real file used in the upload process.
    - session: SQLAlchemy database session for verifying persistence.
"""

import json

import pytest


@pytest.mark.admin_upload_blog_posts
def test_upload_blog_posts_missing_files_key(client):
    payload = json.dumps({"wrong_key": "oops"})
    content_type = "application/json"

    response = client.post("/admin/upload-blog-posts", data=payload, content_type=content_type)

    assert response.status_code == 400
    assert response.get_json() == {
        "success": False,
        "message": "Missing 'files' data in request"
    }


@pytest.mark.admin_upload_blog_posts
def test_upload_blog_posts_malformed_json(client):
    """Should return 400 for malformed JSON with correct content-type."""
    response = client.post(
        "/admin/upload-blog-posts",
        data="{not: 'valid', json}",
        content_type="application/json"
    )
    assert response.status_code == 400


@pytest.mark.api
@pytest.mark.admin_upload_blog_posts
def test_upload_blog_posts_route_with_actual_api(
        app, client, google_drive_service_fixture, session, test_drive_file_metadata_map
):
    """Tests the /admin/upload-blog-posts route with real Google Drive API and database integration.

    Verifies:
    - Successful API interaction
    - Proper content processing
    - HTML sanitization
    - Database persistence
    - Content structure preservation
    """
    with app.app_context():
        file_metadata = test_drive_file_metadata_map["design_principles"]
        file_id = file_metadata["file_id"]
        slug = file_metadata["slug"]

        payload = {
            "files": [{"id": file_id, "slug": slug}]
        }

        response = client.post(
            "/admin/upload-blog-posts",
            data=json.dumps(payload),
            content_type="application/json"
        )

        # Verify API response
        assert response.status_code == 201
        response_data = response.get_json()
        assert len(response_data["success"]) == 1

        uploaded_post = response_data["success"][0]
        assert uploaded_post["drive_file_id"] == file_id
        assert uploaded_post["slug"] == slug
        assert "html_content" in uploaded_post and uploaded_post["html_content"]

        # Verify preview HTML content format
        html_content = uploaded_post["html_content"]

        # Check typographic elements (allow Unicode curly quotes too)
        assert any(q in html_content for q in ["&rsquo;", "'", "’"]), \
            "Smart quotes or apostrophes should be present"

        # Check preview content
        assert html_content.endswith("..."), "Preview should end with ellipsis"
        assert len(html_content) <= 203, "Preview should be no longer than 200 chars + ellipsis"

        # Verify database content
        from app.models.tables.blog_post import blog_posts
        saved_post = session.query(blog_posts).filter_by(drive_file_id=file_id).one_or_none()
        assert saved_post is not None
        assert saved_post.slug == slug
        assert saved_post.html_content

        # Verify full HTML structure and sanitization in database
        full_html = saved_post.html_content

        # Basic structure checks
        assert "<p>" in full_html, "Full content should have paragraphs"
        assert "</p>" in full_html

        # Verify markdown conversion
        assert "```" not in full_html, "Markdown code blocks should be converted"

        # Verify allowed HTML elements
        allowed_elements = {
            'strong': "Text emphasis should be preserved",
            'em': "Italic text should be preserved",
            'code': "Code snippets should be preserved",
            'pre': "Code blocks should be preserved",
            'blockquote': "Quotes should be preserved",
            'ul': "Unordered lists should be preserved",
            'ol': "Ordered lists should be preserved",
            'li': "List items should be preserved",
            'a': "Links should be preserved",
            'table': "Tables should be preserved"
        }

        # Only verify elements that are actually present in the content
        for tag, message in allowed_elements.items():
            if f"<{tag}" in full_html:
                assert f"</{tag}>" in full_html, message

        # Verify safe attributes on links and images
        if "<a " in full_html:
            assert 'href="' in full_html, "Links should have href attributes"
        if "<img " in full_html:
            assert 'alt="' in full_html, "Images should have alt attributes"


@pytest.mark.admin_upload_blog_posts
def test_upload_blog_posts_unsupported_media_type(client):
    """Should return 415 for unsupported content-type like text/plain."""
    response = client.post(
        "/admin/upload-blog-posts",
        data="not-json",
        content_type="text/plain"
    )
    assert response.status_code == 415
