from flask import jsonify, request, Blueprint, Response, make_response, current_app, url_for, abort
from datetime import datetime, timedelta
from models.users import User, Security, SignupUserSchema, UserSchema, SigninUserSchema, UserUpdateSchema
from models.users import User, Security, SignupUserSchema, UserSchema, SigninUserSchema, UserInfoSchema
from werkzeug.security import check_password_hash, generate_password_hash
from itsdangerous import URLSafeTimedSerializer
from marshmallow import ValidationError
import jwt
import phonenumbers
import redis
from routes.error_handlers import *
from app import db, jwt
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    get_jwt_identity,
    get_jwt,
    jwt_required,
    set_access_cookies
)

ACCESS_EXPIRES = timedelta(hours=1)

accounts_route = Blueprint("accounts_route", __name__, url_prefix="/accounts")

jwt_redis_blocklist = redis.StrictRedis(
    host="localhost", port=6379, db=0, decode_responses=True
)

'''@jwt.token_in_blocklist_loader
def check_if_token_is_revoked(jwt_header, jwt_payload: dict):
    jti = jwt_payload["jti"]
    token_in_redis = jwt_redis_blocklist.get(jti)
    return token_in_redis is not None'''

@accounts_route.route("/signup", methods=["POST"])
def signup() -> Response:
    
    request_data = request.get_json(silent=True)

    if not request_data or "email" not in request_data or "full_name" not in request_data or "password" not in request_data:
        abort(400, "Incomplete data. Please provide email, full_name, and password.")

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
    # print(verification_link)
    response = {"user": user_schema.dump(user_to_add), "link": verification_token}

    return make_response(jsonify(response), 200)

@accounts_route.route("/signin", methods=["POST"])
def signin() -> Response:

    request_data = request.get_json(silent=True)

    if not request_data or "email" not in request_data or "password" not in request_data:
        abort(400, "Incomplete data. Please provide email and password.")


    user_data = SigninUserSchema().load(request.get_json(silent=True))

    user = User.query.filter_by(email=user_data["email"]).first()

    if user is None or not check_password_hash(
        Security.query.filter_by(user_id=user.id).first().password_hash,
        user_data["password"],
    ):
        raise APIAuthError()

    access_token = create_access_token(identity=user.id, fresh=True)
    refresh_token = create_refresh_token(user.id)
    response = {"access_token": access_token, "refresh_token": refresh_token}

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

@accounts_route.route("/refresh", methods=["POST"])
@jwt_required(refresh=True)
def refresh():
    user = get_jwt_identity()
    token = create_access_token(identity=user, fresh=False)
    jti = get_jwt()["jti"]
    jwt_redis_blocklist.set(jti, "", ex=ACCESS_EXPIRES)
    response = jsonify({"access_token": token})
    return make_response(response, 200)

@accounts_route.route("/logout", methods=["DELETE"])
@jwt_required(verify_type=False)
def logout():
    token = get_jwt()
    jti = token["jti"]
    ttype = token["type"]
    jwt_redis_blocklist.set(jti, "", ex=ACCESS_EXPIRES)
    return jsonify(msg=f"{ttype.capitalize()} token successfully revoked")


@accounts_route.route('/update_user', methods=['POST'])
@jwt_required()
def update_user():
    request_data = request.get_json(silent=True)

    if not request_data or "full_name" not in request_data or "phone_number" not in request_data:
        return jsonify({'error': 'Incomplete data. Please provide full_name, and phone_number.'}), 400

    try:
        user_data = UserUpdateSchema().load(request_data)
    except ValidationError as e:
        return jsonify({"error": str(e)}), 400

    current_user_id = get_jwt_identity()
    phone_number = user_data['phone_number']

    try:
        parsed_number = phonenumbers.parse(phone_number, None)
        is_valid = phonenumbers.is_valid_number(parsed_number)
    except phonenumbers.NumberParseException:
        return jsonify({'error': 'Invalid phone number'}), 400

    user = User.query.filter_by(id=current_user_id).first()

    if user:
        user.full_name = user_data['full_name']
        user.phone_number = phone_number
        db.session.commit()
        return jsonify({'message': 'User information updated successfully'}), 200
    else:
        return jsonify({'error': 'User not found'}), 404

@accounts_route.route("/info", methods=["GET"])
@jwt_required()
def user_info():
    user = User.query.filter_by(id=get_jwt_identity()).first()
    return UserInfoSchema().dump(user)
