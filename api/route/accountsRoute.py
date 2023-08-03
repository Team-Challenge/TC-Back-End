
from flask import jsonify, request, Blueprint, Response
from datetime import datetime, timedelta
from dao.userDao import UserDao
from models import User
from werkzeug.security import check_password_hash
import jwt
from flask_expects_json import expects_json

accounts_route = Blueprint("accounts_route", __name__, url_prefix="/accounts")

signup_schema = {
  "type": "object",
  "properties": {
    "full_name": { "type": "string" },
    "email": { "type": "string", "pattern": "[^@]+@[^@]+\.[^@]" },
    "password": {"type": "string"}
  },
  "required": ["full_name", "email", "password"]
}

@accounts_route.route("/signup", methods=["POST"])
@expects_json(signup_schema)
def signup() -> Response:
    user_to_add = User(request.get_json(silent=True))
    UserDao.add_user(user_to_add)

    added_user = UserDao.get_user_by_email(user_to_add.email)

    return "fsfsd"

@accounts_route.route("/signin", methods=["POST"])
def signin() -> Response:
    auth = request.get_json()

    user = UserDao.get_user_by_email(auth.get('email'))

    if check_password_hash(user.password, auth.get('password')):

        token = jwt.encode({
            'id': user.id,
            'exp' : datetime.utcnow() + timedelta(minutes = 30)
        }, 'secret')
        return jsonify({'token' : token})