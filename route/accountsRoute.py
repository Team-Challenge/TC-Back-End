from flask import jsonify, request, Blueprint, Response, make_response, current_app, url_for
from datetime import datetime, timedelta
from models import User, Security, SignupUserSchema, UserSchema, SigninUserSchema
from werkzeug.security import check_password_hash, generate_password_hash
from itsdangerous import URLSafeTimedSerializer
import jwt
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

    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    verification_token = serializer.dumps(user_to_add.email, salt='email-verification')

    user_to_add.verification_token = verification_token
    db.session.commit()

    verification_link = url_for('accounts_route.verify_email', token=verification_token, _external=True)
    user_schema = UserSchema(exclude=["id"])
    # Повернути відповідь з посиланням верифікації
    response_data = {
        "user": user_schema.dump(user_to_add),
        "verification_link": verification_link
    }

    return make_response(jsonify(response_data), 200)

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
    else:
        return make_response("", 404)


@accounts_route.route('/verify/<token>', methods=['GET'])
def verify_email(token):
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])

    try:
        email = serializer.loads(token, salt='email-verification', max_age=3600)
        user = User.query.filter_by(email=email).first()

        if user:
            user.is_verified = True
            db.session.commit()
            return jsonify({"message": "Email verified successfully"}), 200
        else:
            return jsonify({"message": "Invalid verification token"}), 404
    except:
        return jsonify({"message": "Invalid verification token"}), 404

