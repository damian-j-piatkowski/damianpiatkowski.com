from marshmallow import Schema, fields, validate


class BlogPostSchema(Schema):
    id = fields.Int(dump_only=True)
    title = fields.Str(required=True, validate=validate.Length(min=1))
    content = fields.Str(required=True)
    image_small = fields.Str(required=True)
    image_medium = fields.Str(required=True)
    image_large = fields.Str(required=True)
    timestamp = fields.DateTime(dump_only=True)
