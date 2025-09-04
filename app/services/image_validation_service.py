import os
from marshmallow import ValidationError

def is_valid_image_path(image_path: str) -> None:
    # Check if the path has a valid image extension
    valid_extensions = {".jpg", ".jpeg", ".png", ".gif"}
    if os.path.splitext(image_path)[1].lower() not in valid_extensions:
        raise ValidationError("Invalid image file path. Must be a .jpg, .jpeg, .png, or .gif.")
