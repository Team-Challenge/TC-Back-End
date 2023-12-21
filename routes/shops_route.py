
from flask import jsonify, request, Blueprint, make_response, current_app, url_for
from models.models import Shop, User, phone_validation
from models.schemas import ShopSchema
from marshmallow.exceptions import ValidationError
from flask_cors import CORS
from flask_jwt_extended import jwt_required


shops_route = Blueprint("shops_route", __name__, url_prefix="/shops")


CORS(shops_route, supports_credentials=True)

@shops_route.route("/shop", methods=["POST"])
@jwt_required()
def create_shops():
    user = User.get_user_id()

    if not user:
        return jsonify({'error': 'User not found'}), 404

    request_data = request.get_json(silent=True)

    try:
        ShopSchema().load(request_data)
    except ValidationError as e:
        return jsonify({"error": str(e)}), 400

    existing_shop = Shop.get_shop_by_owner_id(user.id)
    current_shop = Shop.query.filter_by(name=request_data["name"]).first()

    if existing_shop:
        if 'phone_number' in request_data:
            try:
                phone_validation(request_data['phone_number'])
            except ValueError as e:
                return jsonify({'error': str(e)}), 400

        if 'name' in request_data and current_shop and existing_shop.id != current_shop.id:
            return jsonify({'error': 'Shop name must be unique.'}), 400
        
        existing_shop.update_shop_details(**request_data)
        return jsonify({'message': 'Shop details updated successfully'}), 200
        
    if not request_data or "name" not in request_data or "phone_number" not in request_data:
        return jsonify({'error': 'Incomplete or empty name or phone. Provide name and phone'}), 401

    if current_shop:
        return jsonify({'error': 'Shop name must be unique.'}), 400

    try:
        phone_validation(request_data['phone_number'])
    except ValueError as e:
        return jsonify({'error': str(e)}), 400

    Shop.create_shop(owner_id=user.id, name=request_data['name'],
                    description=request_data.get("description"),
                    phone_number=request_data['phone_number'],
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


@shops_route.route('/shop_banner', methods=['POST', 'DELETE', 'GET'])
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
        if shop_info["photo_shop"] is not None:
            shop_info["photo_shop"] = url_for('static',
                filename=f'media/shops/{shop_info["photo_shop"]}', _external=True)

        if shop_info["banner_shop"] is not None:
            shop_info["banner_shop"] = url_for('static',
                filename=f'media/banner_shops/{shop_info["banner_shop"]}', _external=True)
        
        return jsonify(shop_info), 200

    return make_response('There is no store by user', 404)
