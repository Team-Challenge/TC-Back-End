from flask import jsonify, request, Blueprint, Response, make_response, current_app, url_for, abort
from datetime import datetime, timedelta
from models import User, Security, SignupUserSchema, UserSchema, SigninUserSchema
from werkzeug.security import check_password_hash, generate_password_hash
from itsdangerous import URLSafeTimedSerializer
import jwt
from app import db

accounts_route = Blueprint("accounts_route", __name__, url_prefix="/accounts")


@accounts_route.route("/signup", methods=["POST"])
def signup() -> Response:
    try:
        user_data = SignupUserSchema().load(request.get_json(silent=True))
    except Exception as e:
        abort(400, str(e))

    user_to_add = User(user_data["email"], user_data["full_name"])
    security_to_add = Security(generate_password_hash(user_data["password"]))

    db.session.add(user_to_add)
    db.session.flush()

    security_to_add.user_id = user_to_add.id
    db.session.add(security_to_add)
    db.session.commit()

    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    verification_token = serializer.dumps(user_to_add.email, salt='email-verification')

    db.session.commit()

    verification_link = url_for('accounts_route.verify_email', token=verification_token, _external=True)
    user_schema = UserSchema(exclude=["id", "joined_at", "is_active"])
    print(verification_link)
    response = {"user": user_schema.dump(user_to_add)}

    return make_response(jsonify(response), 200)

@accounts_route.route("/signin", methods=["POST"])
def signin() -> Response:
    user_data = SigninUserSchema().load(request.get_json(silent=True))
    user = User.query.filter_by(email=user_data["email"]).first()

    if user is None or not check_password_hash(
        Security.query.filter_by(user_id=user.id).first().password_hash,
        user_data["password"],
    ):
        abort(401, "Invalid email or password")
    token = jwt.encode(
            {"id": user.id, "exp": datetime.utcnow() + timedelta(minutes=30)},
            current_app.config["JWT_SECRET_KEY"],
        )
    response = {"token": token}
    return make_response(response, 200)


@accounts_route.route('/verify/<token>', methods=['GET'])
def verify_email(token):
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])

    try:
        email = serializer.loads(token, salt='email-verification', max_age=3600)
        user = User.query.filter_by(email=email).first()
        user.is_active = True
        db.session.commit()
        return make_response(jsonify({"message": "OK"}), 200)
    except Exception as e:
        abort(404, "Invalid verification token")
