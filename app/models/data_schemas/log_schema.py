from marshmallow import Schema, fields, validate


class LogSchema(Schema):
    id = fields.Int(dump_only=True)
    level = fields.Str(required=True, validate=validate.Length(min=1))
    message = fields.Str(required=True)
    timestamp = fields.DateTime(dump_only=True)
