from flask import jsonify, request, Blueprint, Response, make_response, current_app, url_for, abort
from datetime import datetime, timedelta
from models.users import User, Security, SignupUserSchema, UserSchema, SigninUserSchema
from werkzeug.security import check_password_hash, generate_password_hash
from itsdangerous import URLSafeTimedSerializer
import jwt
from routes.error_handlers import *
from app import db
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    get_jwt_identity,
    get_jwt,
    jwt_required,
    set_access_cookies
)


users_route = Blueprint("users", __name__, url_prefix="/users")


@users_route.route("/", methods=["GET"])
def get_users() -> Response:
    users = User.query.all()
    user_schema = UserSchema(exclude=["id", "joined_at", "is_active"])
    response = {"users": user_schema.dump(users, many=True)}
    return make_response(jsonify(response), 200)
