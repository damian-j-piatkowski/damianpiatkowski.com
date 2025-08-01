"""Schema definition for blog post data serialization and validation.

This schema validates incoming blog post data, ensuring required fields are present and
correctly formatted. The schema expects HTML content that has been converted from markdown
during the import process. It also facilitates serialization of blog post instances,
including auto-generated fields like `id`, `created_at`, and `updated_at`.

Fields:
    - title: Required string with a minimum length.
    - slug: Required URL-friendly identifier.
    - html_content: Required blog post content in HTML format.
    - drive_file_id: Required identifier of the associated Google Drive file.
    - categories: Required list of strings for organizing posts.
    - created_at: Timestamp indicating when the post was created.
    - updated_at: Optional timestamp indicating when the post was last modified.
    - read_time_minutes: Required estimated reading time in minutes.
    - meta_description: Required short description for SEO.
    - keywords: Required list of SEO keywords.
"""

from marshmallow import Schema, fields, validate


class BlogPostSchema(Schema):
    title = fields.Str(required=True, validate=validate.Length(min=1))
    slug = fields.Str(required=True, validate=validate.Length(min=1))
    html_content = fields.Str(required=True)
    drive_file_id = fields.Str(required=True, validate=validate.Length(min=1))

    categories = fields.List(fields.Str(), load_default=list, validate=validate.Length(min=1))
    keywords = fields.List(fields.Str(), load_default=list, validate=validate.Length(min=1))

    read_time_minutes = fields.Int(required=True, validate=validate.Range(min=1))
    meta_description = fields.Str(required=True, validate=validate.Length(min=1))

    created_at = fields.DateTime(required=True, format="%Y-%m-%d %H:%M:%S")
    updated_at = fields.DateTime(allow_none=True, format="%Y-%m-%d %H:%M:%S")
