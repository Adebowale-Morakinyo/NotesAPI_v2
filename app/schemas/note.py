from marshmallow import Schema, fields


class NoteSchema(Schema):
    title = fields.Str(required=True)
    body = fields.Str(required=True)
    tags = fields.Str()
