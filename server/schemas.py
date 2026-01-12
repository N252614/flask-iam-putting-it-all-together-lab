from marshmallow import fields
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from .config import db
from .models import User, Recipe

class RecipeSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Recipe
        load_instance = True
        include_fk = True

class UserSchema(SQLAlchemyAutoSchema):
    # accept "password" from request, but never return it
    password = fields.String(load_only=True)

    class Meta:
        model = User
        load_instance = True
        include_relationships = True
        exclude = ("_password_hash",) 