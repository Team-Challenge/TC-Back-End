import logging

from flask import (Blueprint, jsonify, make_response, request,
                   url_for)
from flask_cors import CORS
from flask_jwt_extended import jwt_required, get_jwt_identity
from pydantic import ValidationError

from models.accounts import User
from models.errors import serialize_validation_error, NotFoundError
from models.shops import Shop
from routes.responses import ServerResponse
from validation.shops import ShopCreateValid, ShopSchema, ShopUpdateValid

shops = Blueprint("shops_route", __name__, url_prefix="/shops")

CORS(shops, supports_credentials=True)


@shops.route("/shop", methods=["POST"])
@jwt_required()
def create_shops():
    data = request.get_json(silent=True)
    if not data:
        return ServerResponse.BAD_REQUEST
    user = User.get_user_by_id(get_jwt_identity())
    if not user:
        return ServerResponse.USER_NOT_FOUND
    existing_shop = Shop.get_shop_by_owner_id(user.id)
    data['owner_id'] = user.id
    if existing_shop:
        try:
            update_shop_data = ShopUpdateValid(**data).model_dump()
        except ValidationError as e:
            return jsonify(serialize_validation_error(e)), 400
        existing_shop.update_shop_details(**update_shop_data)
        return ServerResponse.SHOP_UPDATED
    if not existing_shop or existing_shop is None:
        try:
            create_shop_data = ShopCreateValid(**data).model_dump()
        except ValidationError as e:
            return jsonify(serialize_validation_error(e)), 400
        Shop.create_shop(**create_shop_data)
        return ServerResponse.SHOP_CREATED
    return ServerResponse.USER_NOT_FOUND


@shops.route('/shop_photo', methods=['POST', 'DELETE', 'GET'])
@jwt_required()
def shop_photo():
    shop = Shop.get_shop_by_owner_id(get_jwt_identity())
    if not shop:
        return ServerResponse.SHOP_NOT_FOUND

    if request.method == 'GET':
        if shop.photo_shop is not None:
            return make_response({"photo_shop": url_for('static',
                                                        filename=f'media/shops/{shop.photo_shop}',
                                                        _external=True)}, 200)
        return ServerResponse.PHOTO_SHOP_NOT_FOUND

    if request.method == 'POST':
        file = request.files.get('image')
        if not file:
            return ServerResponse.BAD_REQUEST
        file_path = shop.add_photo(file)
        return make_response({"photo_shop": url_for('static',
                                                    filename=f'media/shops/{file_path}',
                                                    _external=True)}, 200)
    if request.method == 'DELETE':
        if shop.photo_shop is not None:
            shop.remove_photo()
            return ServerResponse.OK
        return ServerResponse.PHOTO_SHOP_NOT_FOUND

    return ServerResponse.INTERNAL_SERVER_ERROR


@shops.route('/shop_banner', methods=['POST', 'DELETE', 'GET'])
@jwt_required()
def shop_banner():
    shop = Shop.get_shop_by_owner_id(get_jwt_identity())
    if not shop:
        return ServerResponse.SHOP_NOT_FOUND

    if request.method == 'GET':
        if shop.banner_shop is not None:
            return make_response({"shop_banner":
                                      url_for('static',
                                              filename=f'media/banner_shops/{shop.banner_shop}',
                                              _external=True)}, 200)

        return ServerResponse.BANNER_NOT_FOUND

    if request.method == 'POST':
        file = request.files.get('image', None)
        if not file:
            return ServerResponse.BAD_REQUEST

        shop.add_banner(file)
        return make_response({"shop_banner":
                                  url_for('static',
                                          filename=f'media/banner_shops/{shop.banner_shop}',
                                          _external=True)}, 200)
    if request.method == 'DELETE':
        if shop.banner_shop is not None:
            shop.remove_banner()
            return ServerResponse.OK
        return ServerResponse.BANNER_NOT_FOUND

    return ServerResponse.INTERNAL_SERVER_ERROR


@shops.route('/shop_info', methods=['GET'])
@jwt_required()
def get_shop_info():
    user = User.get_user_by_id(get_jwt_identity())
    if not user:
        return ServerResponse.USER_NOT_FOUND
    try:
        shop_info = Shop.get_shop_user_info(user.id)
        response = ShopSchema(**shop_info)
        return jsonify(response.model_dump()), 200
    except NotFoundError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        logging.error(e)
        return ServerResponse.INTERNAL_SERVER_ERROR
