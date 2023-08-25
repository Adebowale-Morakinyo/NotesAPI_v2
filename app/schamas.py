from marshmallow import Schema, fields, validate


class UserSchema(Schema):
    id = fields.Int(dump_only=True)
    username = fields.Str(required=True)
    email = fields.Email(required=True)
    password = fields.Str(required=True, load_only=True)


class TagSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)


class NoteSchema(Schema):
    id = fields.Int(dump_only=True)
    title = fields.Str(required=True)
    content = fields.Str(required=True)
    date = fields.DateTime(dump_only=True)
    user_id = fields.Int(required=True, load_only=True)
    user = fields.Nested(UserSchema(), dump_only=True)
    tags = fields.Nested(TagSchema(), many=True, dump_only=True)


class NoteUpdateSchema(Schema):
    title = fields.Str()
    content = fields.Str()


class NoteTagSchema(Schema):
    message = fields.Str()
    note_id = fields.Int(required=True, load_only=True)
    tag_id = fields.Int(required=True, load_only=True)


class UserNoteSchema(Schema):
    user_id = fields.Int(required=True, load_only=True)
    note_id = fields.Int(required=True, load_only=True)


class UserRegistrationSchema(Schema):
    username = fields.Str(required=True, validate=validate.Length(min=3))
    email = fields.Email(required=True)
    password = fields.Str(required=True, validate=validate.Length(min=6))


class UserLoginResponseSchema(Schema):
    access_token = fields.Str()


class UserProfileSchema(Schema):
    username = fields.Str(dump_only=True)
    email = fields.Email(dump_only=True)
    full_name = fields.Str(required=True)
    profile_picture = fields.Str()  # Field for profile picture URL
    bio = fields.Str()
