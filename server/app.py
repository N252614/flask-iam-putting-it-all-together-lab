#!/usr/bin/env python3

from flask import request, session
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError

from server.config import app, db, api
from server.models import User, Recipe
from server.schemas import UserSchema, RecipeSchema

user_schema = UserSchema()
recipe_schema = RecipeSchema()
recipes_schema = RecipeSchema(many=True)

class Signup(Resource):
    def post(self):
        # Get JSON payload
        data = request.get_json() or {}

        try:
            # Create new user
            user = User(
                username=data.get("username"),
                image_url=data.get("image_url"),
                bio=data.get("bio"),
            )

            # Hash + store password via the model setter
            user.password_hash = data.get("password")

            db.session.add(user)
            db.session.commit()

            # Log in user
            session["user_id"] = user.id

            # Return user JSON (schema must NOT include _password_hash)
            return user_schema.dump(user), 201

        except IntegrityError:
            db.session.rollback()
            return {"errors": ["Username already exists."]}, 422

        except ValueError as e:
            db.session.rollback()
            return {"errors": [str(e)]}, 422
    

class CheckSession(Resource):
    def get(self):
        # Check if user is logged in via session
        user_id = session.get("user_id")

        if user_id:
            user = User.query.get(user_id)
            return user_schema.dump(user), 200

        return {"error": "Unauthorized"}, 401

class Login(Resource):
    def post(self):
        # Get JSON payload
        data = request.get_json() or {}

        username = data.get("username")
        password = data.get("password")

        # Basic guard
        if not username or not password:
            return {"error": "Unauthorized"}, 401

        user = User.query.filter(User.username == username).first()

        if user and user.authenticate(password):
            session["user_id"] = user.id
            return user_schema.dump(user), 200

        return {"error": "Unauthorized"}, 401


class Logout(Resource):
    def delete(self):
        user_id = session.get("user_id")

        # If no active session -> 401
        if not user_id:
            return {"error": "Unauthorized"}, 401

        session["user_id"] = None
        return {}, 204


class RecipeIndex(Resource):
    def get(self):
        user_id = session.get("user_id")

        if not user_id:
            return {"error": "Unauthorized"}, 401

        recipes = Recipe.query.filter_by(user_id=user_id).all()
        return recipes_schema.dump(recipes), 200

    def post(self):
        user_id = session.get("user_id")

        if not user_id:
            return {"error": "Unauthorized"}, 401

        data = request.get_json()

        try:
            recipe = Recipe(
                title=data.get("title"),
                instructions=data.get("instructions"),
                minutes_to_complete=data.get("minutes_to_complete"),
                user_id=user_id
            )

            db.session.add(recipe)
            db.session.commit()

            return recipe_schema.dump(recipe), 201

        except (IntegrityError, TypeError, ValueError):
            db.session.rollback()
            return {"errors": ["validation errors"]}, 422

api.add_resource(Signup, '/signup', endpoint='signup')
api.add_resource(CheckSession, '/check_session', endpoint='check_session')
api.add_resource(Login, '/login', endpoint='login')
api.add_resource(Logout, '/logout', endpoint='logout')
api.add_resource(RecipeIndex, '/recipes', endpoint='recipes')


if __name__ == '__main__':
    app.run(port=5555, debug=True)