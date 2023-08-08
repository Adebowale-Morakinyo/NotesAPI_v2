from marshmallow import Schema, fields


class UserRegistrationSchema(Schema):
    username = fields.Str(required=True)
    email = fields.Email(required=True)
    password = fields.Str(required=True)
