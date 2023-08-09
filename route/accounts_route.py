from datetime import datetime, timedelta
from werkzeug.security import check_password_hash, generate_password_hash
import jwt
from flask import jsonify, request, Blueprint, Response, make_response, current_app
from models import User, Security, SignupUserSchema, UserSchema, SigninUserSchema
from app import db

accounts_route = Blueprint("accounts_route", __name__, url_prefix="/accounts")


@accounts_route.route("/signup", methods=["POST"])
def signup() -> Response:
    user_data = SignupUserSchema().load(request.get_json(silent=True))
    user_to_add = User(user_data["email"], user_data["full_name"])
    security_to_add = Security(generate_password_hash(user_data["password"]))

    db.session.add(user_to_add)
    db.session.flush()

    security_to_add.user_id = user_to_add.id
    db.session.add(security_to_add)
    db.session.commit()

    user_schema = UserSchema(exclude=["id"])
    return make_response(user_schema.dump(user_to_add), 200)

@accounts_route.route("/signin", methods=["POST"])
def signin() -> Response:
    user_data = SigninUserSchema().load(request.get_json(silent=True))
    user = User.query.filter_by(email=user_data["email"]).first()

    if user is not None and check_password_hash(
        Security.query.filter_by(user_id=user.id).first().password_hash,
        user_data["password"],
    ):
        token = jwt.encode(
            {"id": user.id, "exp": datetime.utcnow() + timedelta(minutes=30)},
            current_app.config["JWT_SECRET_KEY"],
        )
        return make_response(jsonify({"token": token}), 200)
    return make_response("", 404)
