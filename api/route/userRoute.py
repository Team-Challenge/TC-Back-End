
from flask import Flask, jsonify, make_response, request, Blueprint, Response, redirect, url_for, abort
from functools import wraps
from datetime import datetime, timedelta
from dao.userDao import UserDao
from models import User
from werkzeug.security import generate_password_hash, check_password_hash
import jwt

user_route = Blueprint("user_route", __name__, url_prefix="/users")

@user_route.route("", methods=["GET", "POST"])
#@auth_required(enabled_methods=[GET])
def users_redirect() -> Response:

    if request.method == "GET":
        return redirect(url_for("user_route.users"), code=302)

    if request.method == "POST":
        return redirect(url_for("user_route.users"), code=307)

    return abort(404)


@user_route.route("/", methods=["GET", "POST"])
#@auth_required(enabled_methods=[GET])
#@swag_from("swagger/userRoute/usersGet.yml", methods=["GET"])
#@swag_from("swagger/userRoute/usersPost.yml", methods=["POST"])
def users() -> Response:

    if request.method == "GET":
        return user_get()

    if request.method == "POST":
        return user_post()

    return abort(404)


def user_post() -> Response:
    user_data: dict = request.get_json(silent=True)
    user_to_add = User(user_data)

    password = user_to_add.password
    hashed_password = generate_password_hash(password)
    user_to_add.password = hashed_password

    UserDao.add_user(user_to_add)
    added_user = UserDao.get_user_by_email(user_to_add.email)
    print(added_user.full_name)
    if added_user is None:
        response = jsonify(
            {
                    "self": "/v2/users",
                    "added": False,
                    "user": None,
                    "error": "An unexpected error occurred creating the user.",
                    }
            )
        response.status_code = 500
        return response
    
    response = jsonify(
            {
                "self": "/v2/users",
                "added": True
            }
        )
    response.status_code = 201
    return response


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