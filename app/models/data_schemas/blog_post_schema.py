"""Schema definition for blog post data serialization and validation.

This schema validates incoming blog post data, ensuring required fields are present and
correctly formatted. It also facilitates serialization of blog post instances, including
auto-generated fields like `id` and `created_at`.
"""

from marshmallow import Schema, fields, validate


class BlogPostSchema(Schema):
    id = fields.Int(dump_only=True)
    title = fields.Str(required=True, validate=validate.Length(min=1))
    slug = fields.Str(required=True, validate=validate.Length(min=1))  # Ensuring slug is required
    content = fields.Str(required=True)
    drive_file_id = fields.Str(required=True, validate=validate.Length(min=1))
    created_at = fields.DateTime(dump_only=True)
