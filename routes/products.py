
import json

from flask import Blueprint, abort, jsonify, request, url_for
from flask_cors import CORS
from flask_jwt_extended import jwt_required
from pydantic import ValidationError

from dependencies import db
from models.accounts import User
from models.products import Product, ProductDetail, ProductPhoto
from models.shops import Shop
from validation.products import (DetailValid,
                                 check_sub_category_belongs_to_category)

products = Blueprint("products_route", __name__, url_prefix="/products")

CORS(products, supports_credentials=True)

@products.route("/product", methods=["POST"])
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
        validated_data = DetailValid(**data).model_dump(exclude_none=True)
    except ValidationError as e:
        abort(400, description=str(e))
    
    check_sub_category_belongs_to_category(category_id=validated_data.get('category_id'),
                                    sub_category_name=validated_data.get('sub_category_name'))

    if validated_data.get('product_characteristic'):
        product_characteristic_dict = validated_data.get('product_characteristic', {})
        validated_data['product_characteristic'] = json.dumps(product_characteristic_dict,
                                                        ensure_ascii=False)
    if validated_data.get('delivery_post'):
        product_delivery_post = validated_data.get('delivery_post', {})
        validated_data['delivery_post'] = json.dumps(product_delivery_post,
                                                        ensure_ascii=False)
    if validated_data.get('method_of_payment'):
        product_method_of_payment = validated_data.get('method_of_payment', {})
        validated_data['method_of_payment'] = json.dumps(product_method_of_payment,
                                                        ensure_ascii=False)
    try:
        DetailValid.name_validator(value=validated_data.get('product_name'))
        if validated_data.get('product_description'):
            DetailValid.description_validator(value=validated_data.get('product_description'))
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    try:
        product = Product.add_product(shop_id=shop.id, **validated_data)
        validated_data['product_id'] = product.id
        ProductDetail.add_product_detail(**validated_data)
        return jsonify({"message": "Product created successfully"},
                        {"product_id": product.id}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@products.route("/product_photo/<int:product_id>", methods=["POST"])
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
        product_detail = ProductDetail.get_product_detail_by_product_id(product.id)
        if not product_detail:
            return jsonify({'error': 'Product detail not found'}), 404
        
        num_photos = ProductPhoto.get_num_photos_by_product_detail_id(product_detail.id)
        if num_photos >= 4:
            return jsonify({'error': 'The maximum photos for product has been 4'}), 400
        
        raw_value = request.form.get('main', '').lower()
        main_photo = raw_value == 'true'
        photo = request.files['image']
        allowed_extensions = {'png', 'jpg', 'jpeg', 'webp'}
        if '.' in photo.filename and photo.filename.rsplit('.', 1)[1].lower() in allowed_extensions:
            ProductPhoto.add_product_photo(product_detail.id, photo, main_photo)
            return jsonify({"message": "Photo product uploaded successfully"}), 200

        return jsonify({"error": "Invalid file extension"}), 400

    except Exception as e:
        return jsonify({"error": str(e)}), 400

@products.route("/shop_products", methods=["GET"])
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
            .outerjoin(ProductPhoto, ProductDetail.id == ProductPhoto.product_detail_id) \
            .filter(Product.shop_id == shop.id) \
            .all()

        result = []
        unique_product_ids = set()

        for product, product_detail, _product_photo in shop_products:
            if product.id not in unique_product_ids:
                photos = [photo.serialize() for photo in product_detail.product_to_photo]
                product_data = {
                    "id": product.id,
                    "category_id": product.category_id,
                    "sub_category_name": product.sub_category_name,
                    "shop_id": product.shop_id,
                    "product_name": product.product_name,
                    "product_description": product.product_description,
                    "time_added": product.time_added,
                    "time_modifeid": product.time_modifeid,
                    "is_active": product.is_active,
                    "price": product_detail.price,
                    "product_status": product_detail.product_status,
                    "product_characteristic": json.loads(product_detail.product_characteristic)
                    if product_detail.product_characteristic is not None else None,
                    "is_return": product_detail.is_return,
                    "delivery_post": json.loads(product_detail.delivery_post)
                    if product_detail.delivery_post is not None else None,
                    "method_of_payment": json.loads(product_detail.method_of_payment)
                    if product_detail.delivery_post is not None else None,
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
        return jsonify({"error": str(e)}), 400

@products.route("/update/<int:product_id>", methods=["PUT"])
@jwt_required()
def update_product(product_id):
    user = User.get_user_id()
    if not user:
        return jsonify({'error': 'User not found'}), 404
    shop = Shop.get_shop_by_owner_id(user.id)
    if not shop:
        return jsonify({'error': 'Shop not found'}), 404

    data = request.json
    validated_data = ProductDetail.validate_product_data(data)
    try:
        product = Product.get_product_by_id(product_id)
        if not product or product.shop_id != shop.id:
            return jsonify({'error': 'Product not found or does not belong to the shop'}), 404

        product_detail = product.product_to_detail
        if product_detail is None:
            return jsonify({'error': 'Product detail not found'}), 404

        product.update_product(**validated_data)

        if validated_data.get('product_characteristic'):
            product_characteristic_dict = validated_data.get('product_characteristic', {})
            validated_data['product_characteristic'] = json.dumps(product_characteristic_dict,
                                                                ensure_ascii=False)
        if validated_data.get('delivery_post'):
            product_delivery_post = validated_data.get('delivery_post', {})
            validated_data['delivery_post'] = json.dumps(product_delivery_post,
                                                        ensure_ascii=False)
        if validated_data.get('method_of_payment'):
            product_method_of_payment = validated_data.get('method_of_payment', {})
            validated_data['method_of_payment'] = json.dumps(product_method_of_payment,
                                                        ensure_ascii=False)
        product_detail.update_product_detail(**validated_data)

        return jsonify({"message": "Product updated successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@products.route("/deactivate/<int:product_id>", methods=["DELETE"])
@jwt_required()
def deactivate_product(product_id):
    user = User.get_user_id()
    if not user:
        return jsonify({'error': 'User not found'}), 404
    shop = Shop.get_shop_by_owner_id(user.id)
    if not shop:
        return jsonify({'error': 'Shop not found'}), 404
    
    try:
        product = Product.get_product_by_id(product_id)
        if not product or product.shop_id != shop.id:
            return jsonify({'error': 'Product not found or does not belong to the shop'}), 404

        Product.delete_product(product_id)

        return jsonify({"message": "Product deactivated"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400