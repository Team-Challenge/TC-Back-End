
from flask import Blueprint, jsonify, request, make_response
from flask_cors import CORS
from flask_jwt_extended import jwt_required
from pydantic import ValidationError

from models.products import Product, ProductPhoto, get_all_shop_products
from utils.utils import serialize_product
from validation.products import CreateProductValid, UpdateProductValid

products = Blueprint("products_route", __name__, url_prefix="/products")

CORS(products, supports_credentials=True)

@products.route("/product", methods=["POST"])
@jwt_required()
def create_product():
    data = request.get_json(silent=True)
    try:
        validated_data = CreateProductValid(**data).model_dump()
        serialize_data = serialize_product(**validated_data)
    except ValidationError as e:
        return make_response(e.json(indent=2), 400)
    except TypeError:
        return make_response({"detail": "Bad request"}, 400)
    try:
        product = Product.add_product(**serialize_data)
        return jsonify({"message": "Product created successfully"},
                            {"product_id": product.id}), 201
    except ValueError as e:
        return make_response({"error": str(e)}, 400)
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@products.route("/product_photo/<int:product_id>", methods=["POST"])
@jwt_required()
def add_product_photo(product_id):
    try:      
        raw_value = request.form.get('main', '').lower()
        main_photo = raw_value == 'true'
        photo = request.files.get('image')
        if not photo:
            return make_response({"detail": "Bad request"}, 400)
        response = ProductPhoto.add_product_photo(product_id, photo, main_photo) 
        return response

    except Exception as e:
        return jsonify({"error": str(e)}), 400

@products.route("/shop_products", methods=["GET"])
@jwt_required()
def get_shop_products():
    response = get_all_shop_products()
    return response

@products.route("/update/<int:product_id>", methods=["PUT"])
@jwt_required()
def update_product(product_id):
    data = request.json
    data['product_id'] = product_id
    try:
        validated_data = UpdateProductValid(**data).model_dump()
        serialize_data = serialize_product(**validated_data)
    except ValidationError as e:
        return jsonify({'error': {e}}), 400
    try:
        response = Product.update_product(**serialize_data)
        return response
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@products.route("/deactivate/<int:product_id>", methods=["DELETE"])
@jwt_required()
def deactivate_product(product_id):    
    try:
        response = Product.delete_product(product_id)
        return response
    except Exception as e:
        return jsonify({"error": str(e)}), 400