import os

from flask import (Blueprint, current_app, jsonify, make_response,
                   send_from_directory)
from flask_cors import CORS
from werkzeug.exceptions import NotFound

categories = Blueprint("categories", __name__, url_prefix="/categories")
CORS(categories, supports_credentials=True)


@categories.route('/categories', methods=['GET'])
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
