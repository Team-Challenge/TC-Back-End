import os

from flask import (Blueprint, current_app, jsonify, make_response,
                   send_from_directory)
from flask_cors import CORS

orders = Blueprint("orders", __name__, url_prefix="/orders")

CORS(orders, supports_credentials=True)


@orders.route("/nova_post", methods=["GET"])
def get_nova_post_json():
    static_dir = os.path.join(current_app.root_path, 'static')
    try:
        return send_from_directory(static_dir, 'delivery/nova_post.json', as_attachment=True)
    except Exception:
        error_message = {'error': 'File not found in the specified location'}
        return make_response(jsonify(error_message), 404)


@orders.route("/ukr_post", methods=["GET"])
def get_ukr_post_json():
    static_dir = os.path.join(current_app.root_path, 'static')
    return send_from_directory(static_dir, 'delivery/ukr_post.json', as_attachment=True)
    try:
        pass
    except Exception:
        error_message = {'error': 'File not found in the specified location'}
        return make_response(jsonify(error_message), 404)
