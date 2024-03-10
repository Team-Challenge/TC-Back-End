
import os
from datetime import timedelta

from flask import Blueprint, Response, jsonify, make_response, request
from flask_cors import CORS
from flask_jwt_extended import (create_access_token, create_refresh_token,
                                get_jwt, get_jwt_identity, jwt_required)
from google_auth_oauthlib.flow import Flow
from pydantic import ValidationError

from config import Config
from dependencies import cache, db, jwt
from models.accounts import DeliveryUserInfo, User
from validation.accounts import (ChangePasswordSchema, DeliveryPostValid,
                                 FullNameValid, GoogleAuthValid,
                                 PhoneNumberValid, SigninValid, SignupValid,
                                 UserInfoSchema, UserSchema)

ACCESS_EXPIRES = timedelta(hours=1)

GOOGLE_CLIENT_SECRETS_FILE = os.path.join(Config.MEDIA_PATH, 'google', 'client_secret_2.json')
accounts = Blueprint("accounts", __name__, url_prefix="/accounts")

CORS(accounts, supports_credentials=True)


@jwt.token_in_blocklist_loader
def check_if_token_is_revoked(jwt_header, jwt_payload: dict):  # pylint: disable=unused-argument
    jti = jwt_payload["jti"]
    token_in_redis = cache.get(jti)
    return token_in_redis is not None

@accounts.route("/signup", methods=["POST"])
def signup() -> Response:

    request_data = request.get_json(silent=True)

    try:
        user_data = SignupValid(**request_data)
    except ValidationError as e:
        return jsonify({"Error": str(e)}), 400

    try:
        user = User.create_user(user_data.email, user_data.full_name, user_data.password)
        link = user.generate_verification_token()
        user_schema = UserSchema(
                                id=user.id,
                                full_name=user.full_name,
                                email=user.email,
                                phone_number=user.phone_number,
                                profile_picture=user.profile_picture
                            )
    except Exception as e:
        return jsonify({"Error": str(e)}), 400

    response = {"user": user_schema.model_dump(), "link": link}

    return make_response(jsonify(response), 200)

@accounts.route("/authorize", methods=["POST"])
def authorize() -> Response:

    google_auth_data = GoogleAuthValid().load(request.get_json(silent=True))
    flow = Flow.from_client_secrets_file(
        GOOGLE_CLIENT_SECRETS_FILE,
        scopes=['https://www.googleapis.com/auth/userinfo.email',
                'https://www.googleapis.com/auth/userinfo.profile',
                'openid'],
    redirect_uri='http://localhost:8000')
    flow.authorization_url(prompt='consent')
    flow.fetch_token(code=google_auth_data['id_token'])

    session = flow.authorized_session()
    profile_info = session.get('https://www.googleapis.com/userinfo/v2/me').json()

    email = profile_info['email']
    name = profile_info['name']

    user = User.query.filter_by(email=email).first()
    if user is None:
        user_to_add = User(email, name)
        db.session.add(user_to_add)
        db.session.commit()
        user = User.query.filter_by(email=email).first()

    access_token = create_access_token(identity=user.id, fresh=True)
    refresh_token = create_refresh_token(user.id)

    response = {"access_token": access_token, "refresh_token": refresh_token}
    return make_response(response, 200)


@accounts.route("/signin", methods=["POST"])
def signin() -> Response:

    request_data = request.get_json(silent=True)

    try:
        user_data = SigninValid(**request_data)
    except ValidationError as e:
        return jsonify({'error': str(e)}), 400
    
    response = User.sign_in(email=user_data.email, password=user_data.password)

    return make_response(response, 200)

@accounts.route('/verify/<token>', methods=['GET'])
def verify_email(token):
    response = User.verify_user_email(token=token)
    return response

@accounts.route("/refresh", methods=["POST"])
@jwt_required(refresh=True)
def refresh():
    user = get_jwt_identity()
    new_refresh_token = create_refresh_token(identity=user)
    token = create_access_token(identity=user, fresh=False)
    jti = get_jwt()["jti"]
    cache.set(jti, "1", timeout=86400)
    response = {"access_token": token, "refresh_token": new_refresh_token}

    return make_response(response, 200)

@accounts.route("/logout", methods=["DELETE"])
@jwt_required(verify_type=False)
def logout():
    token = get_jwt()
    jti = token["jti"]
    ttype = token["type"]
    cache.set(jti, "1", timeout=86400)
    return jsonify(msg=f"{ttype.capitalize()} token successfully revoked")

@accounts.route('/change_phone_number', methods=['POST'])
@jwt_required()
def change_phone_number():
    request_data = request.get_json(silent=True)
    try:
        user_data = PhoneNumberValid(**request_data)
    except ValidationError as e:
        return jsonify({'error': str(e)}), 400
    response = User.user_phone_number_change(user_data.phone_number)
    return response

@accounts.route('/change_full_name', methods=['POST'])
@jwt_required()
def change_full_name():
    request_data = request.get_json(silent=True)

    try:
        user_data = FullNameValid(**request_data)
    except ValidationError as e:
        return jsonify({"error": str(e)}), 400

    response = User.user_full_name_change(user_data.full_name)

    return response

@accounts.route("/info", methods=["GET"])
@jwt_required()
def user_info():
    user_data = User.user_full_info()
    response = UserInfoSchema(**user_data)
    return jsonify(response.model_dump()), 200

@accounts.route('/profile_photo', methods=['POST', 'DELETE','GET'])
@jwt_required()
def profile_photo():
    if request.method == 'GET':
        response = User.user_profile_photo_get()
        return response

    if request.method == 'POST':
        response = User.user_profile_photo_update(request=request)
        return response

    if request.method == 'DELETE':
        response = User.user_profile_photo_delete()
        return response

    return make_response('Method Not Allowed', 405)

@accounts.route('/change_password', methods=['POST'])
@jwt_required()
def change_password():
    data = request.get_json(silent=True)
    try:
        user_data = ChangePasswordSchema(**data)
    except ValidationError as e:
        return jsonify({'error': str(e)}), 400

    response = User.user_change_password(user_data)
    return response

@accounts.route('/delivery_info', methods=['POST', 'DELETE'])
@jwt_required()
def manage_delivery_info():
    request_data = request.get_json(silent=True)
    try:
        delivery_data = DeliveryPostValid(**request_data).model_dump()
    except ValidationError as e:
        return jsonify({'error': str(e) }), 400
    
    if request.method == "POST":
        response = DeliveryUserInfo.add_delivery_info(**delivery_data)
        return response

    if request.method == "DELETE":
        return DeliveryUserInfo.remove_delivery_info()
    return jsonify({'error': "Method not alowed"}), 405