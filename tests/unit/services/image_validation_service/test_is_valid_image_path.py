"""Unit tests for image_validation_service.is_valid_image_path.

Tests included:
    - test_is_valid_image_path_accepts_supported_extensions: Verifies valid paths pass.
    - test_is_valid_image_path_rejects_unsupported: Verifies invalid extensions raise.
"""

import pytest
from marshmallow import ValidationError

from app.services.image_validation_service import is_valid_image_path


@pytest.mark.parametrize(
    "path",
    [
        "hero.jpg",
        "folder/image.JPEG",
        "a.png",
        "x.gif",
    ],
)
def test_is_valid_image_path_accepts_supported_extensions(path):
    """Verifies that supported image extensions are accepted without error."""
    assert is_valid_image_path(path) is None


@pytest.mark.parametrize(
    "path",
    [
        "doc.pdf",
        "script.js",
        "noext",
        "image.bmp",
    ],
)
def test_is_valid_image_path_rejects_unsupported(path):
    """Verifies that unsupported image extensions raise ValidationError."""
    with pytest.raises(ValidationError):
        is_valid_image_path(path)
