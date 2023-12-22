import os
import uuid

from flask import jsonify, request, Blueprint, Response, make_response, current_app, url_for, abort
from datetime import timedelta
from models.models import User, Security, full_name_validation, phone_validation, DeliveryUserInfo
from models.schemas import (UserSchema,
                            SigninUserSchema,
                            SignupUserSchema,
                            FullNameChangeSchema,
                            PasswordChangeSchema,
                            UserDeliveryInfoSchema)
from werkzeug.security import check_password_hash, generate_password_hash
from itsdangerous import URLSafeTimedSerializer
from marshmallow import ValidationError
from flask_cors import CORS
from routes.error_handlers import APIAuthError
from dependencies import db, jwt, cache
from config import Config
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

    if not request_data or "email" not in request_data \
        or "full_name" not in request_data \
        or "password" not in request_data:
        abort(400, "Incomplete data. Please provide email, full_name, and password.")

    try:
        user_data = SignupUserSchema().load(request.get_json(silent=True))
    except ValidationError as e:
        return make_response(jsonify(e.messages), 400)

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

    verification_link = url_for('accounts_route.verify_email',
                    token=verification_token, _external=True)
    user_schema = UserSchema(exclude=["id", "joined_at", "is_active"])

    response = {"user": user_schema.dump(user_to_add), "link": verification_link}

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
    response = {"access_token": token, "refresh_token": new_refresh_token}

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

    current_user_id = get_jwt_identity()
    user = User.query.filter_by(id=current_user_id).first()

    if user:
        try:
            phone_validation(phone_number)
            user.phone_number = phone_number
            db.session.commit()
            return jsonify({'message': 'Phone number updated successfully'}), 200
        except ValueError as e:
            return jsonify({'error': str(e)}), 400
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
    
    user_info = {
        "phone_number": user.phone_number,
        "full_name": user.full_name,
        "email": user.email,
        "profile_photo": url_for('static', filename=f'media/profile/{user.profile_picture}',
                                _external=True) if user.profile_picture else None,
        "post": None,
        "city": None,
        "branch_name": None,
        "address": None}

    delivery_info = DeliveryUserInfo.get_delivery_info_by_owner_id(user.id)

    if delivery_info:
        user_info["post"] = delivery_info.post
        user_info["city"] = delivery_info.city
        user_info["branch_name"] = delivery_info.branch_name
        user_info["address"] = delivery_info.address

    return user_info

@accounts_route.route('/profile_photo', methods=['POST', 'DELETE','GET'])
@jwt_required()
def profile_photo():
    if request.method == 'GET':
        user = User.query.filter_by(id=get_jwt_identity()).first()
        if user.profile_picture is not None:
            filename = user.profile_picture
            return url_for('static', filename=f'media/profile/{filename}', _external=True)
        return make_response('Profile_photo not allowed', 400)

    if request.method == 'POST':
        file = request.files['image']
        _ , file_extension = os.path.splitext(file.filename)
        file_name = uuid.uuid4().hex
        user = User.query.filter_by(id=get_jwt_identity()).first()

        if user.profile_picture is not None:
            prev_photo = os.path.join(PROFILE_PHOTOS_PATH, user.profile_picture)
            if os.path.isfile(prev_photo):
                os.remove(prev_photo)

        user.profile_picture = file_name + file_extension
        file.save(os.path.join(PROFILE_PHOTOS_PATH, file_name + file_extension))
        db.session.commit()
        filename = user.profile_picture
        return url_for('static', filename=f'media/profile/{filename}', _external=True)

    if request.method == 'DELETE':
        user = User.query.filter_by(id=get_jwt_identity()).first()
        file = os.path.join(PROFILE_PHOTOS_PATH, user.profile_picture)
        if os.path.isfile(file):
            os.remove(file)
        user.profile_picture = None
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

@accounts_route.route('/delivery_info', methods=['POST', 'DELETE'])
@jwt_required()
def manage_delivery_info():
    request_data = request.get_json(silent=True)
    user = User.get_user_id()
    existing_delivery = DeliveryUserInfo.get_delivery_info_by_owner_id(user.id)

    if user:
        if request.method == "POST":
            if not existing_delivery:
                try:
                    UserDeliveryInfoSchema().load(request_data)
                    DeliveryUserInfo.add_delivery_info(owner_id=user.id,
                                    post=request_data.get("post"),
                                    city=request_data.get("city"),
                                    branch_name=request_data.get("branch_name"),
                                    address=request_data.get("address"))

                    return jsonify({'message': 'Delivery address created successfully'}), 201
                except ValueError as e:
                    return jsonify({'error': str(e)}), 400
            else:
                existing_delivery.update_delivery_info(**request_data)
                return jsonify({'message': 'Delivery address updated successfully'}), 200

        elif request.method == "DELETE":
            if existing_delivery:
                existing_delivery.remove_delivery_info()
                return jsonify({'message': 'Delivery address removed successfully'}), 200
            return jsonify({'error': 'User does not have a delivery address'}), 400

    return jsonify({'error': 'User not found'}), 404
