from flask import Blueprint
from models.users import UserSchema
from utils.auth import token_required

test_route = Blueprint("test_route", __name__, url_prefix="/tests")

@test_route.route('/check_jwt_token', methods =['POST'])
@token_required
def test(current_user):
    user_schema = UserSchema(exclude=["id", "joined_at", "is_active"])
    response = {"user": user_schema.dump(current_user)}
    return response

@accounts_route.route("/check_redis", methods=["GET"])
def check_redis() -> Response:
    jwt_redis_blocklist.set("foo", "bar")
    return make_response(jsonify({"message": jwt_redis_blocklist.get("foo")}), 200)