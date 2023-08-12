from marshmallow import Schema, fields


class UserSchema(Schema):
    id = fields.Int(dump_only=True)
    username = fields.Str(required=True)
    email = fields.Email(required=True)
    password = fields.Str(required=True, load_only=True)


class NoteSchema(Schema):
    id = fields.Int(dump_only=True)
    title = fields.Str(required=True)
    content = fields.Str(required=True)
    user_id = fields.Int(required=True, load_only=True)
    user = fields.Nested(UserSchema(), dump_only=True)


class NoteUpdateSchema(Schema):
    title = fields.Str()
    content = fields.Str()


class TagSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)


class NoteTagSchema(Schema):
    note_id = fields.Int(required=True, load_only=True)
    tag_id = fields.Int(required=True, load_only=True)


class UserNoteSchema(Schema):
    user_id = fields.Int(required=True, load_only=True)
    note_id = fields.Int(required=True, load_only=True)