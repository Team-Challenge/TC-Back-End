import os
import uuid

from flask import jsonify, request, Blueprint, Response, make_response, current_app, url_for, abort, redirect
from datetime import timedelta
from models.models import User, Security, full_name_validation
from models.schemas import UserSchema, SigninUserSchema, SignupUserSchema, FullNameChangeSchema, UserInfoSchema, PasswordChangeSchema, GoogleAuthSchema
from werkzeug.security import check_password_hash, generate_password_hash
from itsdangerous import URLSafeTimedSerializer
from marshmallow import ValidationError
from flask_cors import CORS
from routes.error_handlers import APIAuthError
from dependencies import db, jwt, cache
from config import Config
from google.auth.jwt import decode
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    get_jwt_identity,
    get_jwt,
    jwt_required
)

ACCESS_EXPIRES = timedelta(hours=1)
PROFILE_PHOTOS_PATH = os.path.join(Config.MEDIA_PATH, 'profile')
PRODUCT_PHOTOS_PATH = os.path.join(Config.MEDIA_PATH, 'products')

accounts_route = Blueprint("accounts_route", __name__, url_prefix="/accounts")

CORS(accounts_route, supports_credentials=True)

@jwt.token_in_blocklist_loader
def check_if_token_is_revoked(jwt_header, jwt_payload: dict):  # pylint: disable=unused-argument
    jti = jwt_payload["jti"]
    token_in_redis = cache.get(jti)
    return token_in_redis is not None

@accounts_route.route("/signup", methods=["POST"])
def signup() -> Response:
    
    request_data = request.get_json(silent=True)

    if not request_data or "email" not in request_data or "full_name" not in request_data or "password" not in request_data:
        abort(400, "Incomplete data. Please provide email, full_name, and password.")

    try:
        user_data = SignupUserSchema().load(request.get_json(silent=True))
        full_name_validation(user_data["full_name"])
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

    response = {"user": user_schema.dump(user_to_add), "link": verification_link}

    return make_response(jsonify(response), 200)

@accounts_route.route("/authorize", methods=["POST"])
def authorize() -> Response:
    google_auth_data = GoogleAuthSchema().load(request.get_json(silent=True))
    token_dict = decode(google_auth_data['id_token'], verify=False)
    user = User.query.filter_by(email=token_dict.get('email')).first()
    if user is None:
        user_to_add = User(token_dict.get('email'), token_dict.get('name'))
        db.session.add(user_to_add)
        db.session.commit()
    access_token = create_access_token(identity=user.id, fresh=True)
    refresh_token = create_refresh_token(user.id)
    response = {"access_token": access_token, "refresh_token": refresh_token}
    
    return make_response(response, 200) 

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
    except Exception:
        abort(404, "Invalid verification token")

@accounts_route.route("/refresh", methods=["POST"])
@jwt_required(refresh=True)
def refresh():
    user = get_jwt_identity()
    new_refresh_token = create_refresh_token(identity=user)
    token = create_access_token(identity=user, fresh=False)
    jti = get_jwt()["jti"]
    cache.set(jti, "1", timeout=86400)
    response = jsonify({"access_token": token}, {"refresh_token": new_refresh_token})
    return make_response(response, 200)

@accounts_route.route("/logout", methods=["DELETE"])
@jwt_required(verify_type=False)
def logout():
    token = get_jwt()
    jti = token["jti"]
    ttype = token["type"]
    cache.set(jti, "1", timeout=86400)
    return jsonify(msg=f"{ttype.capitalize()} token successfully revoked")

@accounts_route.route('/change_phone_number', methods=['POST'])
@jwt_required()
def change_phone_number():
    request_data = request.get_json(silent=True)

    if not request_data or 'phone_number' not in request_data:
        return jsonify({'error': 'Incomplete data. Please provide phone_number.'}), 400

    phone_number = request_data['phone_number']

    
    if not re.match(r'^\+380\d{9}$', phone_number):
        return jsonify({'error': 'Invalid phone number format. Must start with +380 and have 9 digits.'}), 400

    current_user_id = get_jwt_identity()
    user = User.query.filter_by(id=current_user_id).first()

    if user:
        user.phone_number = phone_number
        db.session.commit()
        return jsonify({'message': 'Phone number updated successfully'}), 200
    return jsonify({'error': 'User not found'}), 404

@accounts_route.route('/change_full_name', methods=['POST'])
@jwt_required()
def change_full_name():
    request_data = request.get_json(silent=True)

    if not request_data or "full_name" not in request_data:
        return jsonify({'error': 'Incomplete data. Please provide full_name.'}), 400

    try:
        user_data = FullNameChangeSchema().load(request_data)
        full_name_validation(request_data["full_name"])
    except ValidationError as e:
        return jsonify({"error": str(e)}), 400

    current_user_id = get_jwt_identity()
    full_name = user_data['full_name']

    user = User.query.filter_by(id=current_user_id).first()

    if user:
        user.full_name = full_name
        db.session.commit()
        return jsonify({'message': 'Full name updated successfully'}), 200
    
    return jsonify({'error': 'User not found'}), 404

@accounts_route.route("/info", methods=["GET"])
@jwt_required()
def user_info():
    user = User.query.filter_by(id=get_jwt_identity()).first()
    return UserInfoSchema().dump(user)

@accounts_route.route('/profile_photo', methods=['POST', 'DELETE','GET'])
@jwt_required()
def profile_photo():
    if request.method == 'GET':
        user = User.query.filter_by(id=get_jwt_identity()).first()
        return current_app.send_static_file('media/profile/' + user.profile_picture)
    
    if request.method == 'POST':
        file = request.files['image']
        _ , file_extension = os.path.splitext(file.filename)
        file_name = uuid.uuid4().hex
        user = User.query.filter_by(id=get_jwt_identity()).first()

        prev_photo = os.path.join(PROFILE_PHOTOS_PATH, user.profile_picture)
        if os.path.isfile(prev_photo):
            os.remove(prev_photo)

        user.profile_picture = file_name + file_extension
        file.save(os.path.join(PROFILE_PHOTOS_PATH, file_name + file_extension))
        db.session.commit()
        return make_response(UserInfoSchema().dump(user), 200)

    if request.method == 'DELETE':
        user = User.query.filter_by(id=get_jwt_identity()).first()
        file = os.path.join(PROFILE_PHOTOS_PATH, user.profile_picture)
        if os.path.isfile(file):
            os.remove(file)
        user.profile_picture = ''
        db.session.commit()
        return make_response('OK', 200)

    return make_response('Method Not Allowed', 405)

@accounts_route.route('/change_password', methods=['POST'])
@jwt_required()
def change_password():
    current_user_id = get_jwt_identity()
    
    data = request.get_json()
    current_password = data.get('current_password')
    new_password = data.get('new_password')
    user = User.query.filter_by(id=current_user_id).first()
    security = Security.query.filter_by(user_id=current_user_id).first()

    if user and security:
        schema = PasswordChangeSchema()
        errors = schema.validate(data)
        if errors:
            return jsonify({'error': errors}), 400

        if check_password_hash(security.password_hash, current_password):
            
            hashed_password = generate_password_hash(new_password)
            security.password_hash = hashed_password
            db.session.commit()
            return jsonify({'message': 'Password updated successfully'}), 200
        return jsonify({'error': 'Current password is incorrect'}), 400

    return jsonify({'error': 'User not found'}), 404
