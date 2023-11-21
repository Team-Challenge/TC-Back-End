
from flask import jsonify, Blueprint, Response, make_response
from models.models import User
from models.schemas import UserSchema


users_route = Blueprint("users", __name__, url_prefix="/users")


@users_route.route("/", methods=["GET"])
def get_users() -> Response:
    users = User.query.all()
    user_schema = UserSchema(exclude=["id", "joined_at", "is_active"])
    response = {"users": user_schema.dump(users, many=True)}
    return make_response(jsonify(response), 200)
