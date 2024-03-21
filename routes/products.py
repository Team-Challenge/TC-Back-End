import logging

from flask import Blueprint, jsonify, request
from flask_cors import CORS
from flask_jwt_extended import jwt_required, get_jwt_identity
from pydantic import ValidationError

from models.errors import NotFoundError, UserError, serialize_validation_error, BadFileTypeError
from models.products import Product, ProductPhoto, get_all_shop_products, get_product_info_by_id
from utils.utils import serialize_product
from validation.products import CreateProductValid, UpdateProductValid
from routes.responses import ServerResponse

products = Blueprint("products_route", __name__, url_prefix="/products")

CORS(products, supports_credentials=True)


@products.route("/product", methods=["POST"])
@jwt_required()
def create_product():
    data = request.get_json(silent=True)
    if data is None:
        return ServerResponse.EMPTY_DATA
    try:
        validated_data = CreateProductValid(**data).model_dump()
        serialize_data = serialize_product(**validated_data)
    except ValidationError as e:
        return jsonify(serialize_validation_error(e)), 400

    try:
        response = Product.add_product(get_jwt_identity(), **serialize_data)
        return jsonify({'message': "Product created successfull", "product_id": response}), 201
    except (ValueError, UserError) as e:
        return jsonify({'error': str(e)}), 400
    except NotFoundError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        logging.error(e)
        return ServerResponse.INTERNAL_SERVER_ERROR


@products.route("/product_photo/<int:product_id>", methods=["POST"])
@jwt_required()
def add_product_photo(product_id):
    if 'image' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    try:
        raw_value = request.form.get('main', '').lower()
        main_photo = raw_value == 'true'
        photo = request.files['image']
        response = ProductPhoto.add_product_photo(get_jwt_identity(), product_id, photo, main_photo)
        return jsonify(response), 200
    except (UserError, BadFileTypeError) as e:
        return jsonify({'error': str(e)}), 400
    except NotFoundError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        logging.error(e)
        return jsonify({'error': 'internal server error'}), 500


@products.route("/shop_products", methods=["GET"])
@jwt_required()
def get_shop_products():
    try:
        response = get_all_shop_products(get_jwt_identity())
        return jsonify(response), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except NotFoundError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        logging.error(e)
        return jsonify({'error': 'internal server error'}), 500


@products.route("/update/<int:product_id>", methods=["PUT"])
@jwt_required()
def update_product(product_id):
    data = request.get_json(silent=True)
    if data is None:
        return jsonify({'error': 'Request data is empty'}), 400
    data['product_id'] = product_id
    try:
        validated_data = UpdateProductValid(**data).model_dump()
        serialize_data = serialize_product(**validated_data)
    except ValidationError as e:
        return jsonify(serialize_validation_error(e)), 400
    try:
        response = Product.update_product(get_jwt_identity(), **serialize_data)
        return jsonify(response), 200
    except UserError as e:
        return jsonify({'error': str(e)}), 400
    except NotFoundError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        logging.error(e)
        return jsonify({'error': 'internal server error'}), 500


@products.route("/deactivate/<int:product_id>", methods=["DELETE"])
@jwt_required()
def deactivate_product(product_id):
    try:
        response = Product.delete_product(get_jwt_identity(), product_id)
        return jsonify(response), 200
    except UserError as e:
        return jsonify({'error': str(e)}, 400)
    except NotFoundError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        logging.error(e)
        return jsonify({'error': 'internal server error'}), 500


@products.route("/product_info/<int:product_id>", methods=["GET"])
def get_product_info(product_id):
    try:
        response = get_product_info_by_id(product_id)
        return jsonify(response), 200
    except NotFoundError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        logging.error(e)
        return ServerResponse.INTERNAL_SERVER_ERROR
