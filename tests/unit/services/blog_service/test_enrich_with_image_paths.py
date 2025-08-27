"""Unit tests for the enrich_with_image_paths service function.

This module verifies that enrich_with_image_paths correctly attaches a resolved
image base path (for either thumbnails or hero images) to each blog post,
using either a remote or local static path.

Tests included:
    - test_enrich_with_image_paths_empty_list: Ensures an empty input returns an empty list.
    - test_enrich_with_image_paths_local_fallback: Verifies fallback to the default thumbnail if a specific
        directory is missing.
    - test_enrich_with_image_paths_local_found: Verifies correct path resolution when the local thumbnail exists.
    - test_enrich_with_image_paths_local_hero_fallback: Verifies fallback behavior for hero image type.
    - test_enrich_with_image_paths_local_hero_found: Verifies correct local resolution for hero image type.
    - test_enrich_with_image_paths_mixed_hybrid: Verifies behavior when some posts resolve to remote and
        others fallback to local.
    - test_enrich_with_image_paths_mixed_local: Verifies behavior when some slugs have thumbnail files
        and others fallback.
    - test_enrich_with_image_paths_missing_slug: Ensures posts without a slug are skipped safely.
    - test_enrich_with_image_paths_remote_base: Verifies URL resolution when using a remote image base path.
    - test_enrich_with_image_paths_remote_hero: Verifies correct remote resolution when using hero images.

Fixtures:
    - app: Provides a Flask test app context.
"""

import os
from unittest.mock import patch

from app.services.blog_service import enrich_with_image_paths


def test_enrich_with_image_paths_empty_list(app):
    """Verifies that an empty input list returns an empty list."""
    result = enrich_with_image_paths([])
    assert result == []


@patch("app.services.blog_service.os.path.exists")
@patch("app.services.blog_service.url_for")
def test_enrich_with_image_paths_local_fallback(mock_url_for, mock_exists, app):
    """Verifies fallback to the default thumbnail when retina.jpg is missing."""
    mock_exists.return_value = False
    mock_url_for.side_effect = lambda *args, **kwargs: f"/static/{kwargs['filename']}"

    posts = [{"slug": "missing-thumb"}]
    enriched = enrich_with_image_paths(posts)
    assert enriched[0]["thumb_base"] == "/static/blog-images/default/thumbnail"

    # Assert that the path corresponding to the post slug was checked for a thumbnail image
    expected_path = os.path.join(
        app.static_folder, "blog-images", "missing-thumb", "thumbnail", "desktop.jpg"
    )
    mock_exists.assert_called_once_with(expected_path)


@patch("app.services.blog_service.os.path.exists")
@patch("app.services.blog_service.url_for")
def test_enrich_with_image_paths_local_found(mock_url_for, mock_exists, app):
    """Verifies the correct thumbnail path is used when retina.jpg exists locally."""
    mock_exists.return_value = True
    mock_url_for.side_effect = lambda *args, **kwargs: f"/static/{kwargs['filename']}"

    posts = [{"slug": "post-1"}]
    enriched = enrich_with_image_paths(posts)
    assert enriched[0]["thumb_base"] == "/static/blog-images/post-1/thumbnail"

    expected_path = os.path.join(
        app.static_folder, "blog-images", "post-1", "thumbnail", "desktop.jpg"
    )
    mock_exists.assert_called_once_with(expected_path)


@patch("app.services.blog_service.os.path.exists")
@patch("app.services.blog_service.url_for")
def test_enrich_with_image_paths_local_hero_fallback(mock_url_for, mock_exists, app):
    """Verifies fallback to the default hero path when local hero image is missing."""
    mock_exists.return_value = False
    mock_url_for.side_effect = lambda *args, **kwargs: f"/static/{kwargs['filename']}"

    posts = [{"slug": "missing-hero"}]
    enriched = enrich_with_image_paths(posts, image_type="hero", key_name="hero_base")

    assert enriched[0]["hero_base"] == "/static/blog-images/default/hero"

    expected_path = os.path.join(
        app.static_folder, "blog-images", "missing-hero", "hero", "hero_16x9_1920w.jpg"
    )
    mock_exists.assert_called_once_with(expected_path)


@patch("app.services.blog_service.os.path.exists")
@patch("app.services.blog_service.url_for")
def test_enrich_with_image_paths_local_hero_found(mock_url_for, mock_exists, app):
    """Verifies correct local hero image path is used when retina.jpg exists."""
    mock_exists.return_value = True
    mock_url_for.side_effect = lambda *args, **kwargs: f"/static/{kwargs['filename']}"

    posts = [{"slug": "post-hero"}]
    enriched = enrich_with_image_paths(posts, image_type="hero", key_name="hero_base")

    assert enriched[0]["hero_base"] == "/static/blog-images/post-hero/hero"

    expected_path = os.path.join(
        app.static_folder, "blog-images", "post-hero", "hero", "hero_16x9_1920w.jpg"
    )
    mock_exists.assert_called_once_with(expected_path)


@patch("app.services.blog_service.os.path.exists")
@patch("app.services.blog_service.url_for")
def test_enrich_with_image_paths_mixed_hybrid(mock_url_for, mock_exists, app):
    """Verifies behavior when some posts resolve to remote base and others fallback to local."""
    app.config["BLOG_IMAGE_BASE_PATH"] = "https://cdn.example.com/blog-thumbnails"

    # No os.path.exists or url_for is used when base is remote
    mock_url_for.side_effect = Exception("url_for should not be called with remote base")
    mock_exists.side_effect = Exception("os.path.exists should not be called with remote base")

    posts = [{"slug": f"post-{i + 1}"} for i in range(7)]

    # Manually override the base for last 3 to simulate fallback behavior
    remote = posts[:4]
    local = posts[4:]

    # Remote config is applied first
    enriched_remote = enrich_with_image_paths(remote)

    # Now simulate local config fallback
    app.config["BLOG_IMAGE_BASE_PATH"] = "blog-images"
    mock_exists.side_effect = [False, False, False]
    mock_url_for.side_effect = lambda *args, **kwargs: f"/static/{kwargs['filename']}"

    enriched_local = enrich_with_image_paths(local)

    combined = enriched_remote + enriched_local

    assert combined[0]["thumb_base"] == "https://cdn.example.com/blog-thumbnails/post-1/thumbnail"
    assert combined[3]["thumb_base"] == "https://cdn.example.com/blog-thumbnails/post-4/thumbnail"
    assert combined[4]["thumb_base"] == "/static/blog-images/default/thumbnail"
    assert combined[6]["thumb_base"] == "/static/blog-images/default/thumbnail"
    assert mock_exists.call_count == 3


@patch("app.services.blog_service.os.path.exists")
@patch("app.services.blog_service.url_for")
def test_enrich_with_image_paths_mixed_local(mock_url_for, mock_exists, app):
    """Verifies behavior when some posts have thumbnail files and others fallback (local base)."""
    # First 3 exist, next 4 do not
    mock_exists.side_effect = [True, True, True, False, False, False, False]
    mock_url_for.side_effect = lambda *args, **kwargs: f"/static/{kwargs['filename']}"

    posts = [{"slug": f"post-{i + 1}"} for i in range(7)]
    enriched = enrich_with_image_paths(posts)

    expected = [
        "/static/blog-images/post-1/thumbnail",
        "/static/blog-images/post-2/thumbnail",
        "/static/blog-images/post-3/thumbnail",
        "/static/blog-images/default/thumbnail",
        "/static/blog-images/default/thumbnail",
        "/static/blog-images/default/thumbnail",
        "/static/blog-images/default/thumbnail",
    ]

    assert [post["thumb_base"] for post in enriched] == expected
    assert mock_exists.call_count == 7


def test_enrich_with_image_paths_missing_slug(app):
    """Verifies that posts without a slug are skipped and not mutated."""
    posts = [{"title": "Untitled"}]
    result = enrich_with_image_paths(posts)
    assert "thumb_base" not in result[0]


def test_enrich_with_image_paths_remote_base(app):
    """Verifies thumbnail URLs are constructed directly when BLOG_IMAGE_BASE_PATH is a remote URL."""
    app.config["BLOG_IMAGE_BASE_PATH"] = "https://cdn.example.com/blog-thumbnails"

    posts = [{"slug": "remote-post"}]
    enriched = enrich_with_image_paths(posts)

    assert enriched[0]["thumb_base"] == "https://cdn.example.com/blog-thumbnails/remote-post/thumbnail"


def test_enrich_with_image_paths_remote_hero(app):
    """Verifies hero URLs are constructed directly when BLOG_IMAGE_BASE_PATH is a remote URL."""
    app.config["BLOG_IMAGE_BASE_PATH"] = "https://cdn.example.com/blog-images"

    posts = [{"slug": "remote-post"}]
    enriched = enrich_with_image_paths(posts, image_type="hero", key_name="hero_base")

    assert enriched[0]["hero_base"] == "https://cdn.example.com/blog-images/remote-post/hero"
