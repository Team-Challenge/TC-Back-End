
import uuid

from flask import jsonify, request, Blueprint, make_response, current_app
from models.models import Shop, User, phone_validation, name_shop_validation
from models.schemas import ShopSchema, ShopInfoPhotoShema, ShopInfoBannerShema
from dependencies import db
from marshmallow.exceptions import ValidationError
from flask_cors import CORS
from flask_jwt_extended import (
    get_jwt_identity,
    jwt_required
    )


shops_route = Blueprint("shops_route", __name__, url_prefix="/shops")


CORS(shops_route, supports_credentials=True)

@shops_route.route("/shop", methods=["POST"])
@jwt_required()
def create_shop():
    user = User.get_user_id()

    if not user:
        return jsonify({'error': 'User not found'}), 404

    request_data = request.get_json(silent=True)

    try:
        shop_data = ShopSchema().load(request_data)
    except ValidationError as e:
        return jsonify({"error": str(e)}), 400

    existing_shop = Shop.get_shop_by_owner_id(user.id)

    phone_number = request_data.get("phone_number")
    name = request_data.get("name")

    if existing_shop:

        if 'phone_number' in request_data:
            try:
                phone_validation(phone_number)
            except ValueError as e:
                return jsonify({'error': str(e)}), 400
        if 'name' in request_data:
            try:
                name_shop_validation(name)
            except ValueError as e:
                return jsonify({'error': str(e)}), 400
        
        existing_shop.update_shop_details(**request_data)
        return jsonify({'message': 'Shop details updated successfully'}), 200

    else:
        if not request_data or "name" not in request_data or "phone_number" not in request_data:
            return jsonify({'error': 'Incomplete or empty name or phone. Provide name and phone for the shop.'}), 401

        try:
           name_shop_validation(name)
           phone_validation(phone_number)
        except ValueError as e:
            return jsonify({'error': str(e)}), 400

        new_shop = Shop.create_shop(owner_id=user.id, name=name,
                            description=request_data.get("description"),
                            phone_number=phone_number,
                            link=request_data.get("link"))

        return jsonify({'message': 'Shop created successfully'}), 201

@shops_route.route('/shop_photo', methods=['POST', 'DELETE', 'GET'])
@jwt_required()
def shop_photo():
    user = User.get_user_id()
    shop = Shop.get_shop_by_owner_id(user.id)

    if request.method == 'GET' and shop:
        if shop.photo_shop is not None:
            return current_app.send_static_file('media/shops/' + shop.photo_shop)
        else:
            return make_response('Photo shop not found', 404)

    if shop:
        if request.method == 'POST':
            file = request.files['image']
            shop.add_photo(file)
            return make_response(ShopInfoPhotoShema().dump(shop), 200)

        elif request.method == 'DELETE':
            if shop.photo_shop is not None:
                shop.remove_photo()
                return make_response('OK', 200)

        return make_response('Method Not Allowed', 405)
    return jsonify({'message': 'There is no store by user'}), 404


@shops_route.route('/shop_banner', methods=['POST', 'DELETE', 'GET'])
@jwt_required()
def shop_banner():
    user = User.get_user_id()
    shop = Shop.get_shop_by_owner_id(user.id)

    if request.method == 'GET' and shop:
        if shop.banner_shop is not None:
            return current_app.send_static_file('media/banner_shops/' + shop.banner_shop)
        else:
            return make_response('Banner shop not found', 404)

    if shop:
        if request.method == 'POST':
            file = request.files['image']
            shop.add_banner(file)
            return make_response(ShopInfoBannerShema().dump(shop), 200)

        elif request.method == 'DELETE':
            if shop.banner_shop is not None:
                shop.remove_banner()
                return make_response('OK', 200)

        return make_response('Method Not Allowed', 405)
    return make_response('There is no store by user', 404)


@shops_route.route('/shop_info', methods=['GET'])
@jwt_required()
def get_shop_info():
    user = User.get_user_id()

    if not user:
        return make_response('User not found', 404)

    shop = Shop.get_shop_by_owner_id(user.id)

    if shop:
        shop_schema = ShopSchema()
        shop_info = shop_schema.dump(shop)
        return jsonify(shop_info), 200

    return make_response('There is no store by user', 404)
