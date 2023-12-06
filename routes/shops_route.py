import os
import uuid

from flask import jsonify, request, Blueprint, make_response
from models.models import Shop, Link, User
from models.schemas import ShopSchema, LinkSchema, ShopInfoPhotoShema, ShopInfoBannerShema
from dependencies import db
from config import Config
from marshmallow.exceptions import ValidationError
from flask_cors import CORS
from flask_jwt_extended import (
    get_jwt_identity,
    jwt_required
    )


shops_route = Blueprint("shops_route", __name__, url_prefix="/shops")


CORS(shops_route, supports_credentials=True)

SHOPS_PHOTOS_PATH = os.path.join(Config.MEDIA_PATH, 'shops')
SHOPS_BANNER_PHOTOS_PATH = os.path.join(Config.MEDIA_PATH, 'banner_shops')

@shops_route.route("/shop", methods=["POST"])
@jwt_required()
def create_shop():
    current_user_id = get_jwt_identity()
    user = User.query.filter_by(id=current_user_id).first()

    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    request_data = request.get_json(silent=True)

    try:
        shop_data = ShopSchema().load(request_data)
    except ValidationError as e:
        return jsonify({"error": str(e)}), 400

    existing_shop = Shop.query.filter_by(owner_id=user.id).first()

    if existing_shop:
        if "name" in request_data:
            existing_shop.name = request_data["name"]

        if "description" in request_data:
            existing_shop.description = request_data["description"]

        if "phone_number" in request_data:
            existing_shop.phone_number = request_data["phone_number"]

        db.session.commit()
        return jsonify({'message': 'Shop details updated successfully'}), 200
        
    else:
        if not request_data or "name" not in request_data or len(request_data["name"]) == 0:
            return jsonify({'error': 'Incomplete or empty name. Provide name for the shop.'}), 401
    
        new_shop = Shop(owner_id=user.id,
                        name=request_data["name"],
                        description=request_data.get("description", None),
                        phone_number=request_data.get("phone_number", None))

        db.session.add(new_shop)
        db.session.commit()

        return jsonify({'message': 'Shop created successfully'}), 201

@shops_route.route('/shop_photo', methods=['POST', 'DELETE'])
@jwt_required()
def shop_photo():

    current_user_id = get_jwt_identity()
    user = User.query.filter_by(id=current_user_id).first()
    shop = Shop.query.filter_by(owner_id=user.id).first()

    if shop:
        if request.method == 'POST':
            file = request.files['image']
            extension = file.filename.split('.')[1]
            file_name = uuid.uuid4().hex
            shop.photo_shop = file_name + '.' + extension
            file.save(os.path.join(SHOPS_PHOTOS_PATH, file_name + '.' + extension))
            db.session.commit()
            return make_response(ShopInfoPhotoShema().dump(shop), 200)

        if request.method == 'DELETE':
            file = os.path.join(SHOPS_PHOTOS_PATH, shop.photo_shop)
            if os.path.isfile(file):
                os.remove(file)
            shop.photo_shop = ''
            db.session.commit()
            return make_response('OK', 200)

        return make_response('Method Not Allowed', 405)
    return make_response('There is no store by user')

@shops_route.route('/shop_banner', methods=['POST', 'DELETE'])
@jwt_required()
def shop_banner():

    current_user_id = get_jwt_identity()
    user = User.query.filter_by(id=current_user_id).first()
    shop = Shop.query.filter_by(owner_id=user.id).first()

    if shop:
        if request.method == 'POST':
            file = request.files['image']
            extension = file.filename.split('.')[1]
            file_name = uuid.uuid4().hex
            shop.banner_shop = file_name + '.' + extension
            file.save(os.path.join(SHOPS_BANNER_PHOTOS_PATH, file_name + '.' + extension))
            db.session.commit()
            return make_response(ShopInfoBannerShema().dump(shop), 200)

        if request.method == 'DELETE':
            file = os.path.join(SHOPS_BANNER_PHOTOS_PATH, shop.banner_shop)
            if os.path.isfile(file):
                os.remove(file)
            shop.banner = ''
            db.session.commit()
            return make_response('OK', 200)

        return make_response('Method Not Allowed', 405)
    return make_response('There is no store by user')