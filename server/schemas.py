from marshmallow import Schema, fields


class UserSchema(Schema):
    id = fields.Int(dump_only=True)
    username = fields.Str(required=True)
    image_url = fields.Str(allow_none=True)
    bio = fields.Str(allow_none=True)


class RecipeSchema(Schema):
    id = fields.Int(dump_only=True)
    title = fields.Str(required=True)
    instructions = fields.Str(required=True)
    minutes_to_complete = fields.Int(required=True)
    user_id = fields.Int(required=True)