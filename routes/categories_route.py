
from flask import jsonify, request, Blueprint, make_response, current_app, url_for
from marshmallow.exceptions import ValidationError
from models.models import Categories
from models.schemas import CategorySchema
from flask_cors import CORS


categories_route = Blueprint("categories_route", __name__, url_prefix="/categories")


CORS(categories_route, supports_credentials=True)

@categories_route.route("/category", methods=["POST"])
def create_category():
    request_data = request.get_json(silent=True)
    try:
        CategorySchema().load(request_data)
    except ValidationError as e:
        return jsonify({"error": str(e)}), 400

    Categories.create_category(category_name=request_data['category_name'])

    return jsonify({'message': 'Category created successfully'}), 201

@categories_route.route("/categories", methods=["GET"])
def get_all_categories():
    categories = Categories.get_all_categories()
    serialized_categories = [category.as_dict() for category in categories]
    return jsonify(serialized_categories), 200
