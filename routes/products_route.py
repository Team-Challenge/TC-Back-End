
import json

from flask import jsonify, request, Blueprint, make_response, current_app, url_for
from models.models import Shop, User, Product, ProductDetail, ProductPhoto
from models.schemas import ProductSchema
from marshmallow.exceptions import ValidationError
from flask_cors import CORS
from flask_jwt_extended import jwt_required
from werkzeug.utils import secure_filename
from dependencies import db


products_route = Blueprint("products_route", __name__, url_prefix="/products")

CORS(products_route, supports_credentials=True)

@products_route.route("/product", methods=["POST"])
@jwt_required()
def create_product():
    user = User.get_user_id()
    if not user:
        return jsonify({'error': 'User not found'}), 404
    shop = Shop.get_shop_by_owner_id(user.id)
    if not shop:
        return jsonify({'error': 'Shop not found'}), 404

    data = request.json
    try:
        product = Product.add_product(shop_id=shop.id, **data)
        product_characteristic_dict = data.get('product_characteristic', {})
        data['product_characteristic'] = json.dumps(product_characteristic_dict, ensure_ascii=False)
        data['product_id'] = product.id
        product_detail = ProductDetail.add_product_detail(**data)
        return jsonify({"message": "Product created successfully"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@products_route.route("/product_photo/<int:product_id>", methods=["POST"])
@jwt_required()
def add_product_photo(product_id):
    user = User.get_user_id()
    if not user:
        return jsonify({'error': 'User not found'}), 404

    shop = Shop.get_shop_by_owner_id(user.id)
    if not shop:
        return jsonify({'error': 'Shop not found'}), 404

    product = Product.get_product_by_id(product_id)
    if not product:
        return jsonify({'error': 'Product not found'}), 404

    try:
        product_detail = ProductDetail.get_product_detail_by_id(product_id)
        if not product_detail:
            return jsonify({'error': 'Product detail not found'}), 404

        main_photo = True if request.form.get('main', '').lower() == 'true' else False
        photo = request.files['image']

        ProductPhoto.add_product_photo(product_detail.id, photo, main_photo)

        return jsonify({"message": "Photo product uploaded successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@products_route.route("/shop_products", methods=["GET"])
@jwt_required()
def get_shop_products():
    user = User.get_user_id()
    if not user:
        return jsonify({'error': 'User not found'}), 404
    shop = Shop.get_shop_by_owner_id(user.id)
    if not shop:
        return jsonify({'error': 'Shop not found'}), 404

    try:
        shop_products = db.session.query(Product, ProductDetail, ProductPhoto) \
            .join(ProductDetail, Product.id == ProductDetail.product_id) \
            .join(ProductPhoto, ProductDetail.id == ProductPhoto.product_detail_id) \
            .filter(Product.shop_id == shop.id) \
            .distinct(Product.id) \
            .all()

        result = []
        unique_product_ids = set()

        for product, product_detail, product_photos in shop_products:
            if product.id not in unique_product_ids:
                photos = [photo.serialize() for photo in product_detail.product_to_photo]
                product_data = {
                    "id": product.id,
                    "category_id": product.category_id,
                    "sub_category_name": product.sub_category_name,
                    "shop_id": product.shop_id,
                    "product_name": product.product_name,
                    "product_description": product.product_description,
                    "time_added": product.time_added.isoformat(),
                    "time_modifeid": product.time_modifeid.isoformat(),
                    "is_active": product.is_active,
                    "price": product_detail.price,
                    "product_status": product_detail.product_status,
                    "product_characteristic": json.loads(product_detail.product_characteristic),
                    "is_return": product_detail.is_return,
                    "delivery_post": product_detail.delivery_post,
                    "method_of_payment": product_detail.method_of_payment,
                    "is_unique": product_detail.is_unique,
                    "photos": [{
                        "id": photo.get('id'),
                        "product_photo": url_for('static',
                                        filename=f'media/products/{photo.get("product_photo")}',
                                                                 _external=True),
                        "timestamp": photo.get('timestamp'),
                        "main": photo.get('main')
                    } for photo in photos]
                }
                result.append(product_data)
                unique_product_ids.add(product.id)

        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@products_route.route("/update/<int:product_id>", methods=["PUT"])
@jwt_required()
def update_product(product_id):
    user = User.get_user_id()
    if not user:
        return jsonify({'error': 'User not found'}), 404
    shop = Shop.get_shop_by_owner_id(user.id)
    if not shop:
        return jsonify({'error': 'Shop not found'}), 404

    data = request.json
    try:
        product = Product.get_product_by_id(product_id)
        if not product or product.shop_id != shop.id:
            return jsonify({'error': 'Product not found or does not belong to the shop'}), 404

        product_detail = product.product_to_detail

        product.update_product(product.id, **data)

        product_characteristic_dict = data.get('product_characteristic', {})
        data['product_characteristic'] = json.dumps(product_characteristic_dict, ensure_ascii=False)
        product_detail.update_product_detail(product.id, **data)

        return jsonify({"message": "Product updated successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400








