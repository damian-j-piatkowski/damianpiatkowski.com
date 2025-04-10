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
    - real_drive_file_metadata: Metadata for a real file used in the upload process.
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
        app, client, google_drive_service_fixture, session, real_drive_file_metadata
):
    """Tests the /admin/upload-blog-posts route with real Google Drive API and database."""
    with app.app_context():
        file_id = real_drive_file_metadata["file_id"]
        title = real_drive_file_metadata["title"]
        slug = real_drive_file_metadata["slug"]

        payload = {
            "files": [{"id": file_id, "title": title, "slug": slug}]
        }

        response = client.post(
            "/admin/upload-blog-posts",
            data=json.dumps(payload),
            content_type="application/json"
        )

        assert response.status_code == 201
        response_data = response.get_json()
        assert len(response_data["success"]) == 1

        uploaded_post = response_data["success"][0]
        assert uploaded_post["drive_file_id"] == file_id
        assert uploaded_post["title"] == title
        assert uploaded_post["slug"] == slug
        assert "content" in uploaded_post and uploaded_post["content"]

        from app.models.tables.blog_post import blog_posts
        saved_post = session.query(blog_posts).filter_by(drive_file_id=file_id).one_or_none()
        assert saved_post is not None
        assert saved_post.title == title
        assert saved_post.slug == slug
        assert saved_post.content


@pytest.mark.admin_upload_blog_posts
def test_upload_blog_posts_unsupported_media_type(client):
    """Should return 415 for unsupported content-type like text/plain."""
    response = client.post(
        "/admin/upload-blog-posts",
        data="not-json",
        content_type="text/plain"
    )
    assert response.status_code == 415
