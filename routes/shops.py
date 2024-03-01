
from flask import (Blueprint, current_app, jsonify, make_response, request,
                   url_for)
from flask_cors import CORS
from flask_jwt_extended import jwt_required
from pydantic import ValidationError

from models.accounts import User
from models.shops import Shop
from validation.shops import ShopCreateValid, ShopSchema, ShopUpdateValid

shops = Blueprint("shops_route", __name__, url_prefix="/shops")


CORS(shops, supports_credentials=True)

@shops.route("/shop", methods=["POST"])
@jwt_required()
def create_shops():
    user = User.get_user_id()

    if not user:
        return jsonify({'error': 'User not found'}), 404

    request_data = request.get_json(silent=True)
    existing_shop = Shop.get_shop_by_owner_id(user.id)
    if existing_shop:
        try:
            update_shop_data = ShopUpdateValid(owner_id=user.id, **request_data).model_dump()
            existing_shop.update_shop_details(**update_shop_data)
        except ValidationError as e:
            return jsonify({"error": str(e)}), 400
        return jsonify({'message': 'Shop updated successfully'}), 200
        
    if not existing_shop or existing_shop is None:
        try:
            create_shop_data = ShopCreateValid(owner_id=user.id, **request_data).model_dump()
            Shop.create_shop(**create_shop_data)
        except ValidationError as e:
            return jsonify({"error": str(e)}), 400

        return jsonify({'message': 'Shop created successfully'}), 201

@shops.route('/shop_photo', methods=['POST', 'DELETE', 'GET'])
@jwt_required()
def shop_photo():
    user = User.get_user_id()
    shop = Shop.get_shop_by_owner_id(user.id)

    if request.method == 'GET' and shop:
        if shop.photo_shop is not None:
            return current_app.send_static_file('media/shops/' + shop.photo_shop)
        return make_response('Photo shop not found', 404)

    if shop and request.method == 'POST':
        file = request.files['image']
        shop.add_photo(file)
        return url_for('static', filename=f'media/shops/{file}', _external=True)

    if shop and request.method == 'DELETE' and shop.photo_shop is not None:
        shop.remove_photo()
        return make_response('OK', 200)

    if shop:
        return make_response('Method Not Allowed', 405)
    
    return jsonify({'message': 'There is no store by user'}), 404


@shops.route('/shop_banner', methods=['POST', 'DELETE', 'GET'])
@jwt_required()
def shop_banner():
    user = User.get_user_id()
    shop = Shop.get_shop_by_owner_id(user.id)

    if request.method == 'GET' and shop:
        if shop.banner_shop is not None:
            return current_app.send_static_file('media/banner_shops/' + shop.banner_shop)
        return make_response('Banner shop not found', 404)

    if shop and request.method == 'POST':
        file = request.files['image']
        shop.add_banner(file)
        return url_for('static', filename=f'media/banner_shops/{file}', _external=True)

    if shop and request.method == 'DELETE' and shop.banner_shop is not None:
        shop.remove_banner()
        return make_response('OK', 200)

    if shop:
        return make_response('Method Not Allowed', 405)
    
    return jsonify({'message': 'There is no store by user'}), 404

@shops.route('/shop_info', methods=['GET'])
@jwt_required()
def get_shop_info():
    user = User.get_user_id()

    if not user:
        return make_response('User not found', 404)

    shop = Shop.get_shop_by_owner_id(user.id)

    if shop:
        shop_schema = ShopSchema(
            id=shop.id,
            owner_id=shop.owner_id,
            name=shop.name,
            description=shop.description,
            photo_shop=shop.photo_shop,
            banner_shop=shop.banner_shop,
            phone_number=shop.phone_number,
            link=shop.link
        )
        if shop_schema.photo_shop is not None:
            shop_schema.photo_shop = url_for('static',
                filename=f'media/shops/{shop_schema.photo_shop}', _external=True)

        if shop_schema.banner_shop is not None:
            shop_schema.banner_shop = url_for('static',
                filename=f'media/banner_shops/{shop_schema.banner_shop}', _external=True)
        
        return jsonify(shop_schema.model_dump()), 200

    return make_response('There is no store by user', 404)
