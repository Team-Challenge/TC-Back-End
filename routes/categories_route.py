
import os
from sqlalchemy import func
from models.models import Product, Categories
from flask_cors import CORS
from dependencies import db
from models.patterns import SubCategoryDict
from flask import Blueprint, current_app, send_from_directory, make_response, jsonify
from werkzeug.exceptions import NotFound
from sqlalchemy.exc import OperationalError

categories_route = Blueprint("categories_route", __name__, url_prefix="/categories")
CORS(categories_route, supports_credentials=True)


@categories_route.route('/categories', methods=['GET'])
def get_static_categories():

    static_dir = os.path.join(current_app.root_path, 'static')
    try:
        d = send_from_directory(static_dir, 'categories/categories.json', as_attachment=True)
        return d
    except NotFound:
        error_message = {'error': 'File not found in the specified location'}
        return make_response(jsonify(error_message), 404)
    except Exception as ex:
        error_message = {'error': f"{ex}"}
        return make_response(jsonify(error_message), 404)


@categories_route.route('/categories_detail', methods=['GET'])
def get_dynamic_categories():
    try:
        categories_with_subcategories = db.session.query(
        Categories.id,
        Categories.category_name,
        func.group_concat(Product.sub_category_name)
        ).join(Product, Categories.id == Product.category_id) \
        .group_by(Categories.id, Categories.category_name).all()

        result = []
        for category_id, category_name, subcategories_str in categories_with_subcategories:
            subcategories = subcategories_str.split(',') if subcategories_str else []
            subcats = set()
            subcategories_lst = []

            for subcat in subcategories:
                if subcat not in subcats:
                    subcats.add(subcat)
                    subcategories_lst.append([SubCategoryDict.get(subcat), subcat])

            subcategories_lst.sort(key=lambda x: x[0])

            category_info = {
                "id": category_id,
                "label": category_name,
                "subcategories": subcategories_lst
            }
            result.append(category_info)
        if len(result) < 6:
            result = {"message": "Not all categories used in already created products."}
        return jsonify(result), 200
    except OperationalError as ex:
        if "no such table" in str(ex):
            return jsonify({"message": "No tables have been created.",}), 502
    return None
