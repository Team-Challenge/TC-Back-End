import logging
import os
from datetime import timedelta

from flask import (Blueprint, Response, current_app, jsonify, make_response,
                   redirect, request, url_for)
from flask_cors import CORS
from flask_jwt_extended import (create_access_token, create_refresh_token,
                                get_jwt, get_jwt_identity, jwt_required)
from google_auth_oauthlib.flow import Flow
from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer
from pydantic import ValidationError

from config import Config
from dependencies import cache, db, jwt
from models.accounts import DeliveryUserInfo, User
from models.errors import NotFoundError, UserError, serialize_validation_error, \
    FileTooLargeError, BadFileTypeError
from validation.accounts import (ChangePasswordSchema, DeliveryPostValid,
                                 FullNameValid, GoogleAuthValid,
                                 PhoneNumberValid, SigninValid, SignupValid,
                                 UserInfoSchema, UserSchema, UserSignupReturnSchema)
from routes.responses import ServerResponse

ACCESS_EXPIRES = timedelta(hours=1)

GOOGLE_CLIENT_SECRETS_FILE = os.path.join(
    Config.MEDIA_PATH, 'google', 'client_secret_2.json')
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
    if request_data is None:
        return ServerResponse.EMPTY_DATA
    try:
        user_data = SignupValid(**request_data)
    except ValidationError as e:
        return jsonify(serialize_validation_error(e)), 400

    try:
        user = User.create_user(user_data.email, user_data.full_name, user_data.password)
        serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
        token = serializer.dumps(user.email, salt='email-verification')
        verification_link = url_for('accounts.verify_email', token=token, _external=True)
        user_schema = UserSchema(
            id=user.id,
            full_name=user.full_name,
            email=user.email,
            phone_number=user.phone_number,
            profile_picture=user.profile_picture
        )
        response = UserSignupReturnSchema(link=verification_link, user=user_schema)
        return Response(response.model_dump_json(indent=4), mimetype="application/json", status=201)
    except UserError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        logging.error(e)
        return ServerResponse.INTERNAL_SERVER_ERROR


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
    profile_info = session.get(
        'https://www.googleapis.com/userinfo/v2/me').json()

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
    if request_data is None:
        return ServerResponse.EMPTY_DATA
    try:
        user_data = SigninValid(**request_data)
    except ValidationError as e:
        return jsonify(serialize_validation_error(e)), 400
    try:
        response = User.sign_in(email=user_data.email,
                                password=user_data.password)
        return make_response(response, 200)
    except UserError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        logging.error(e)
        return ServerResponse.INTERNAL_SERVER_ERROR


@accounts.route('/verify/<token>', methods=['GET'])
def verify_email(token):
    try:
        serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
        response = User.verify_email(token=token, serializer=serializer)
        if response == "OK":
            return redirect("http://dorechi.store", code=302)
        raise UserError('Bad request')
    except UserError as e:
        return jsonify({"error": str(e)}), 400
    except SignatureExpired:
        return ServerResponse.TOKEN_EXPIRED
    except BadSignature:
        return ServerResponse.INVALID_TOKEN
    except Exception as e:
        logging.error(e)
        return ServerResponse.INTERNAL_SERVER_ERROR


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
    if request_data is None:
        return ServerResponse.EMPTY_DATA
    try:
        user_data = PhoneNumberValid(**request_data)
    except ValidationError as e:
        return jsonify(serialize_validation_error(e)), 400
    try:
        user_id = get_jwt_identity()
        User.change_number(user_id, user_data.phone_number)
        return ServerResponse.OK
    except UserError as e:
        return jsonify({"error": str(e)}), 400
    except NotFoundError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        logging.error(e)
        return ServerResponse.INTERNAL_SERVER_ERROR


@accounts.route('/change_full_name', methods=['POST'])
@jwt_required()
def change_full_name():
    request_data = request.get_json(silent=True)
    if request_data is None:
        return ServerResponse.EMPTY_DATA
    try:
        user_data = FullNameValid(**request_data)
    except ValidationError as e:
        return jsonify(serialize_validation_error(e)), 400
    try:
        user_id = get_jwt_identity()
        User.change_full_name(user_id=user_id, full_name=user_data.full_name)
        return ServerResponse.OK
    except UserError as e:
        return jsonify({"error": str(e)}), 400
    except NotFoundError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        logging.error(e)
        return ServerResponse.INTERNAL_SERVER_ERROR


@accounts.route("/info", methods=["GET"])
@jwt_required()
def user_info():
    try:
        user_id = get_jwt_identity()
        user_data = User.get_user_info(user_id)
        response = UserInfoSchema(**user_data)
        return Response(response.model_dump_json(indent=4), mimetype="application/json", status=200)
    except NotFoundError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        logging.error(e)
        return ServerResponse.INTERNAL_SERVER_ERROR


@accounts.route('/profile_photo', methods=['POST', 'DELETE'])
@jwt_required()
def profile_photo():
    if request.method == 'POST':
        if 'image' not in request.files:
            return ServerResponse.NO_FILE_PROVIDED
        try:
            filename = User.handle_profile_photo(request, action='upload')

            return make_response({"profile_picture":
                                      url_for('static',
                                              filename=f'media/profile/{filename}',
                                              _external=True)}, 200)
        except FileTooLargeError as ex:
            return make_response({"error": str(ex)}, 413)
        except BadFileTypeError as ex:
            return make_response({"error": str(ex)}, 422)
        except UserError as e:
            return jsonify({"error": str(e)}), 400
        except NotFoundError as e:
            return jsonify({"error": str(e)}), 404
        except Exception as e:
            logging.error(e)
            return ServerResponse.INTERNAL_SERVER_ERROR

    if request.method == 'DELETE':
        try:
            User.handle_profile_photo(request, action='delete')
            return ServerResponse.OK
        except UserError as e:
            return jsonify({"error": str(e)}), 400
        except NotFoundError as e:
            return jsonify({"error": str(e)}), 404
        except Exception as e:
            logging.error(e)
            return ServerResponse.INTERNAL_SERVER_ERROR
    return ServerResponse.METHOD_NOT_ALLOWED


@accounts.route('/change_password', methods=['POST'])
@jwt_required()
def change_password():
    request_data = request.get_json(silent=True)
    if request_data is None:
        return ServerResponse.EMPTY_DATA
    try:
        user_data = ChangePasswordSchema(**request_data).model_dump()
    except ValidationError as e:
        return jsonify(serialize_validation_error(e)), 400
    try:
        user_id = get_jwt_identity()
        User.change_password(user_id, **user_data)
        return ServerResponse.OK
    except UserError as e:
        return jsonify({"error": str(e)}), 400
    except NotFoundError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        logging.error(e)
        return ServerResponse.INTERNAL_SERVER_ERROR


@accounts.route('/delivery_info', methods=['POST', 'DELETE'])
@jwt_required()
def manage_delivery_info():
    try:
        user_id = get_jwt_identity()
        if request.method == "POST":
            request_data = request.get_json(silent=True)
            if request_data is None:
                return ServerResponse.EMPTY_DATA
            try:
                delivery_data = DeliveryPostValid(**request_data).model_dump()
            except ValidationError as e:
                return jsonify(serialize_validation_error(e)), 400
            DeliveryUserInfo.add_delivery_info(
                user_id=user_id, **delivery_data)
            return ServerResponse.OK

        if request.method == "DELETE":
            DeliveryUserInfo.remove_delivery_info(user_id=user_id)
            return ServerResponse.OK
    except NotFoundError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        logging.error(e)
        return ServerResponse.INTERNAL_SERVER_ERROR

    return ServerResponse.METHOD_NOT_ALLOWED
