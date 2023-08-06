from marshmallow import Schema, fields


class NoteSchema(Schema):
    id = fields.Int(dump_only=True)
    title = fields.Str(required=True)
    body = fields.Str(required=True)
    tags = fields.Str()
    date = fields.DateTime(dump_only=True)
    user_id = fields.Int(dump_only=True)
