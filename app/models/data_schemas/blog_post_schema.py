"""Schema definition for blog post data serialization and validation.

This schema validates incoming blog post data, ensuring required fields are present and
correctly formatted. The schema expects HTML content that has been converted from markdown
during the import process. It also facilitates serialization of blog post instances,
including auto-generated fields like `id` and `created_at`. The categories field accepts
a list of strings for post organization.
"""

from marshmallow import Schema, fields, validate


class BlogPostSchema(Schema):
    title = fields.Str(required=True, validate=validate.Length(min=1))
    slug = fields.Str(required=True, validate=validate.Length(min=1))
    html_content = fields.Str(required=True)
    drive_file_id = fields.Str(required=True, validate=validate.Length(min=1))
    categories = fields.List(fields.Str(), missing=[], allow_none=True)  # New categories field
    created_at = fields.DateTime(required=True, format="%Y-%m-%d %H:%M:%S")