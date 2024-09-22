from marshmallow import Schema, fields, validate
from app.services.image_validation_service import is_valid_image_path

class BlogPostSchema(Schema):
    id = fields.Int(dump_only=True)
    title = fields.Str(required=True, validate=validate.Length(min=1))
    content = fields.Str(required=True)
    image_small = fields.Str(required=True, validate=is_valid_image_path)
    image_medium = fields.Str(required=True, validate=is_valid_image_path)
    image_large = fields.Str(required=True, validate=is_valid_image_path)
    url = fields.Str(required=True, validate=validate.Length(min=1))
    created_at = fields.DateTime(dump_only=True)
