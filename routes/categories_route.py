
from flask import jsonify, Blueprint
from models.models import Categories
from flask_cors import CORS


categories_route = Blueprint("categories_route", __name__, url_prefix="/categories")


CORS(categories_route, supports_credentials=True)

@categories_route.route("/categories", methods=["GET"])
def get_all_categories():
    categories = Categories.get_all_categories()
    serialized_categories = [category.as_dict() for category in categories]
    return jsonify(serialized_categories), 200
