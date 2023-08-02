
from flask import Flask, jsonify, make_response, request, Blueprint, Response, redirect, url_for, abort, current_app
from functools import wraps
from datetime import datetime, timedelta
from dao.userDao import UserDao
from models import User
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
from flask_expects_json import expects_json
from flasgger import Swagger

user_route = Blueprint("user_route", __name__, url_prefix="/users")

signup_schema = {
  "type": "object",
  "properties": {
    "full_name": { "type": "string" },
    "email": { "type": "string", "pattern": "[^@]+@[^@]+\.[^@]" },
    "password": {"type": "string"}
  },
  "required": ["full_name", "email", "password"]
}

@user_route.route("/", methods=["POST"])
@expects_json(signup_schema)
def user_post() -> Response:
    """Example endpoint returning a list of colors by palette
    This is using docstrings for specifications.
    ---
    parameters:
      - name: palette
        in: path
        type: string
        enum: ['all', 'rgb', 'cmyk']
        required: true
        default: all
    definitions:
      Palette:
        type: object
        properties:
          palette_name:
            type: array
            items:
              $ref: '#/definitions/Color'
      Color:
        type: string
    responses:
      200:
        description: A list of colors (may be filtered by palette)
        schema:
          $ref: '#/definitions/Palette'
        examples:
          rgb: ['red', 'green', 'blue']
    """

    user_to_add = User(request.get_json(silent=True))
    UserDao.add_user(user_to_add)

    added_user = UserDao.get_user_by_email(user_to_add.email)

    return "fsfsd"


def user_get() -> Response:
    try:
        data = request.json
        user = UserDao.login(data['email'], data['password'])
        if user:
            try:
                # token should expire after 24 hrs
                user["token"] = jwt.encode({"user_id": user["email"]}, 'secret_key',algorithm="HS256")
                return {
                    "message": "Successfully fetched auth token",
                    "data": user
                }
            except Exception as e:
                return {
                    "error": "Something went wrong",
                    "message": str(e)
                }, 500
        return {
            "message": "Error fetching auth token!, invalid email or password",
            "data": None,
            "error": "Unauthorized"
        }, 404
    except Exception as e:
        return {
                "message": "Something went wrong!",
                "error": str(e),
                "data": None
        }, 500